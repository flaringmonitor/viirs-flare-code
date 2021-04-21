import argparse
import datetime
import re
import sys
import time
import os
import psycopg2
from psycopg2 import sql

# make sure chdir is our directory
os.chdir(os.path.join(os.path.dirname(__file__), '.'))

# top level directory
sys.path.append('..')

import local_settings as settings
import src.lib.db as db

import FlareFit

class Flares:
    def __init__(self, timestamp, first, last):
        # postgres
        self.conn = db.open_db(conn_string=settings.POSTGRES_STRING)
        self.cursor = self.conn.cursor()
        self.months = 5
        
        self.reported_flares = sql.SQL('flare_automation.reported_flares')

        # if no timestamp specified, create one
        if timestamp is None:
            self.timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        else:
            self.timestamp = timestamp
        
        self.first = first
        self.last = last

        # first/last args for query formatting
        # default
        self.fl_args = {
            'first' : sql.SQL('''
                DATE_TRUNC('month', NOW()) - ({months}||' months')::INTERVAL
            ''').format(
                months = sql.Literal(str(self.months)),
            ),

            'last'  : sql.SQL('''
                DATE_TRUNC('month', NOW())
            '''),
        }
        
        # override first and last dates
        if self.first is not None:
            self.fl_args['first'] = sql.SQL('''{first}::date''').format(
                first = sql.Literal(self.first),
            )
        
        if self.last is not None:
            self.fl_args['last'] = sql.SQL('''{last}::date''').format(
                last = sql.Literal(self.last),
            )
        
        # remember tables we've already created
        self.have_table = set()

        pass
        
    def schemafy(self, table):
        '''
        Add flare_automation schema and encode as identifier
        '''
        return sql.SQL('flare_automation.{table}').format(
            table=sql.Identifier(table),
        )
    
    def select_to_table(self, query, table, args):
        '''
        Given an SQL file and a base table name, create table or
        insert additional data to it as required.
        
        query - file to read SQL from, or Composable SQL
        table - table to add to
        args  - dict of composable sql formatting
        '''
        
        table_dated = '%s_%s' % (table, self.timestamp)
        table_comp = self.schemafy(table_dated)
        view_comp = self.schemafy(table)

        args['our_table'] = table_comp
        args['table_group'] = sql.Literal(table)
        args['our_timestamp'] = sql.Literal(self.timestamp)

        if isinstance(query, str):
            with open(query, 'r') as i:
                # read and format
                select_query = sql.SQL(i.read()).format(**args)
        else:
            # expect sql to be a composable query
            select_query = query
        
        if table in self.have_table:
           # just insert
           query = sql.SQL('''
                INSERT INTO {table}
                {select_query}
           ''').format(
               table = table_comp,
               select_query = select_query,
           )
           
        else:
           # create table
           query = sql.SQL('''
                DROP TABLE IF EXISTS {table} CASCADE;

                CREATE TABLE {table} AS
                {select_query};
                
                GRANT SELECT ON {table} TO internal_read_only;
                
                CREATE OR REPLACE VIEW {view} AS
                SELECT
                    *
                FROM
                    {table};
                
                GRANT SELECT ON {view} TO internal_read_only;
           ''').format(
               table = table_comp,
               view = view_comp,
               select_query = select_query,
           )
        
        # run query
        db.do_sql(self.cursor, query)
        
        # we now have this table
        self.have_table.add(table)
    
        return table_comp

    def vacuum_analyze(self, table):
        self.conn.autocommit = True
        
        # vacuum analyze
        query = sql.SQL('''
            VACUUM ANALYZE {table};
        ''').format(
            table = table,
        )

        db.do_sql(self.cursor, query)
        
        self.conn.autocommit = False
    
    def input_clusters(self):
        '''
        run weekly flares and monthly wells
        '''
        
        
        # default
        args = self.fl_args.copy()
        
        self.raw_flare = None

        # raw flares for all states
        for state in ['ND', 'NM', 'TX']:
            self.raw_flare = self.select_to_table('sql/raw_flare_%s.sql' % state.lower(),
                'raw_flare', args)
        
        # weekly flares will use raw flares
        args['raw_flare'] = self.raw_flare
        
        self.weekly_flare = None
        
        # weekly flares for all states
        for state in ['ND', 'NM', 'TX']:
            self.weekly_flare = self.select_to_table('sql/weekly_flares_%s.sql' % state.lower(),
                'weekly_flare', args)
        
        self.monthly_wells = None
        
        # monthly wells possible in one pass
        for state in ['ND', 'NM', 'TX']:
            self.monthly_wells = self.select_to_table('sql/monthly_wells_%s.sql' % state.lower(),
                'monthly_wells', args)

        # extra stuff added to monthly wells
        for state in ['ND', 'NM', 'TX']:
            self.monthly_wells = self.select_to_table('sql/dec_wells_%s.sql' % state.lower(),
                'monthly_wells', args)

        # add indexes
        query = sql.SQL('''
            CREATE INDEX ON {weekly}  USING GIST (state, flare_month_d, cluster_geom);
            CREATE INDEX ON {monthly} USING GIST (state, disp_dte, cluster_geom);
        ''').format(
            weekly = self.weekly_flare,
            monthly = self.monthly_wells,
        )

        db.do_sql(self.cursor, query)

        self.conn.commit()
    
        self.vacuum_analyze(self.weekly_flare)
        self.vacuum_analyze(self.monthly_wells)        
    
    def merge_clusters(self):
        self.merged = self.select_to_table('sql/cluster_ftw.sql', 
            'cluster_ftw', {
            'weekly' : self.weekly_flare,
            'monthly': self.monthly_wells,
        })

        self.conn.commit()

        self.vacuum_analyze(self.merged)

    def total_clusters(self):
        self.totals = self.select_to_table('sql/cluster_totals.sql', 
            'cluster_totals', {
            'merged' : self.merged,
        })
        
        # add indexes
        query = sql.SQL('''
            CREATE INDEX {i1} ON {totals} (state ASC, ticker ASC, month ASC);
            CREATE INDEX {i2} ON {totals} (state ASC, month ASC, ticker ASC);
        ''').format(
            i1 = sql.Identifier('cluster_totals_stm_%s' % self.timestamp),
            i2 = sql.Identifier('cluster_totals_smt_%s' % self.timestamp),
            totals = self.totals,
        )

        db.do_sql(self.cursor, query)

        self.conn.commit()

        self.vacuum_analyze(self.totals)

    re_ts_table = re.compile(r'^(.*)_[0-9]{14}$')

    def union_of(self, table):
        '''
        Build a union all expression of the specific table type
        '''
        query = sql.SQL('''
            SELECT 
                tablename
            FROM
                pg_tables
            WHERE
                schemaname='flare_automation'
        ''')
        
        db.do_sql(self.cursor, query)
        
        matches = []
        
        for row in self.cursor:
            m = self.re_ts_table.match(row[0])
            if not m:
                continue
            
            if m.group(1) != table:
                continue
            
            # format one query
            query = sql.SQL('''
                SELECT
                    *
                FROM
                    flare_automation.{table}
            ''').format(
                table = sql.Identifier(row[0])
            )
            
            matches.append(query)
        
        if not matches:
            # no tables found
            return None
        
        # return the union
        return sql.SQL('\nUNION ALL\n').join(matches)
    
    def build_combined(self):
        '''
        Combine all known cluster totals and real flare data
        giving preference to newest.
        '''
        # join our two queries
        query = sql.SQL('''
            SELECT
                COALESCE(c.state, r.state) AS state,
                COALESCE(c.month, r.month) AS month,
                COALESCE(c.ticker, r.operator) AS operator,
                c.sum_rh,
                r.flared
            FROM
            (
                {cluster_merge}
            ) c
            FULL OUTER JOIN
            (
                SELECT
                    state, month, operator,
                    SUM(flared) AS flared
                FROM
                    {reported_flares}
                GROUP BY
                    state, month, operator
            ) r
            ON
                c.state = r.state AND
                c.month = r.month AND
                c.ticker = r.operator
            WHERE
                c.sum_rh IS NOT NULL OR
                r.flared IS NOT NULL
            ORDER BY
                1, 2, 3
        ''').format(
            cluster_merge = self.cluster_merge,
            reported_flares = self.reported_flares,
        )

        self.combined = self.select_to_table(query,
                'combined_flare', {})

        self.conn.commit()        
    
    def flare_ui(self):
        '''
        build unioned flare ui dataset
        '''
        
        self.flare_ui = self.select_to_table('sql/flare_ui.sql', 'flare_ui', {
            'raw_flare' : self.raw_flare,
            'cluster_ftw' : self.cluster_ftw_merge,
            'weekly' : self.weekly_flare,
            'operator_factors' : self.operator_factors,
        })

        self.conn.commit()

        self.vacuum_analyze(self.flare_ui)

    def build_unions(self):
        '''
        build union expressions for next steps
        '''
        self.cluster_merge = sql.SQL('''
            SELECT
                DISTINCT ON (state, month, ticker)
                    run, state, month, ticker, sum_rh
            FROM
                (
                 {union}
                ) a
            ORDER BY
                state, month, ticker, run DESC
        ''').format(
            union = self.union_of('cluster_totals')
        )
        
        self.cluster_ftw_merge = sql.SQL('''
            -- first build a map of highest run per state/ticker/month
            WITH run_for AS
            (
                SELECT
                    state, flare_month_d,
                    MAX(run) as max_run
                FROM
                (
                    {union}
                ) u
                
                GROUP BY
                    state, flare_month_d
            )
        
            SELECT
                u.*
            FROM
                (
                 {union}
                ) u,
                run_for r
            WHERE
                -- select only cluster entries for the newest run per
                -- state-month
                u.state = r.state AND
                u.flare_month_d = r.flare_month_d AND
                u.run = r.max_run
            ORDER BY
                u.state, u.flare_month_d, u.company_key
        ''').format(
            union = self.union_of('cluster_ftw')
        )
        

    def operator_estimates(self):
        '''
        create operator estimates
        '''
        
        self.operator_estimates = self.select_to_table('sql/operator_estimates.sql', 
            'operator_estimates', {
            'cluster_totals' : self.cluster_merge,
            'reported_flares'    : self.reported_flares,
            'operator_factors' : self.operator_factors,
        })

        self.conn.commit()

        self.vacuum_analyze(self.operator_estimates)

    def state_oper_errors(self):
        '''
        derive error from operator_estimates
        '''
        self.state_oper_errors = self.select_to_table('sql/state_oper_errors.sql', 
            'state_oper_errors', {
            'operator_estimates' : self.operator_estimates,
        })

        self.conn.commit()

        self.vacuum_analyze(self.state_oper_errors)
            
    def run_operators(self):
        '''
        Run through flare automation process for operators
        '''
        #print("Build flare_ui table")
        #self.flare_ui()

        #sys.exit(0)

        print("Building well and flare clusters")
        self.input_clusters()

        print("Associating well and flare clusters")
        self.merge_clusters()

        print("Computing operator totals")
        self.total_clusters()

        print("Build union SQL")
        self.build_unions()

        print("Build combined flare")
        self.build_combined()

        print("Build FlareFit")
        f = FlareFit.FlareFit(self.timestamp, conn = self.conn)
        self.operator_factors = f.run()
        
        print("Build flare_ui table")
        self.flare_ui()
        
        print("Build flare_automation.operator_flare_estimates")
        self.operator_estimates()
        
        print("Build flare_automation.state_oper_errors")
        self.state_oper_errors()
        
    def setup(self):
        # build geo indexed tmp table off well_all (ND, NM and TX)
        db.sql_from_file(self.cursor, 'sql/tmp_geo.sql', {})

        # build production
        db.sql_from_file(self.cursor, 'sql/tmp_prod.sql', {})

        # viirs
        db.sql_from_file(self.cursor, 'sql/tmp_viirs.sql', {})

def main():
    parser = argparse.ArgumentParser(description='Flare processor')

    parser.add_argument("-t", "--timestamp", type=str,
                    help="run as this specific timestamp")
    parser.add_argument('-f', '--first', type=str,
                    help="first date")
    parser.add_argument('-l', '--last', type=str,
                    help="last date")

    args = parser.parse_args()

    try:
        f = Flares(args.timestamp, args.first, args.last)

        f.setup()
        f.run_operators()

    except Exception as e:
        #send_slack('operations', "@channel build_views needs attention: \n error: %s\n build_view arguments: %s" % (e, sys.argv[1:]))
        # make sure we don't throw stuff just into the slack abyss, also on the terminal/log
        raise

if __name__ == "__main__":
    main()
