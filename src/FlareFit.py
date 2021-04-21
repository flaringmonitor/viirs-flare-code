import argparse
import datetime
import re
import sys
import time
import os
import psycopg2
from psycopg2 import sql


import pandas as pd
import numpy as np
import scipy
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import model_selection, preprocessing, feature_selection, ensemble, linear_model, metrics, decomposition

# make sure chdir is our directory
os.chdir(os.path.join(os.path.dirname(__file__), '.'))

# top level directory
sys.path.append('..')

import local_settings as settings
import src.lib.db as db

graphs_subdir = 'graphs'

class FlareFit:
    def __init__(self, timestamp, conn = None):

        if conn:
            self.conn = conn
        else:
            self.conn = db.open_db()

        self.cursor = self.conn.cursor()
        self.timestamp = timestamp
        self.nsplit = 6
        
        self.output_table = sql.SQL('flare_automation.{table}').format(
            table = sql.Identifier('operator_factors_%s' % timestamp),
        )

        self.output_view = sql.SQL('flare_automation.operator_factors')
        
        pass
    
    def load(self):
        '''
        Load combined flare data
        '''
        query = sql.SQL('''
            SELECT
                state, month, operator, sum_rh, flared
            FROM
                flare_automation.{table}
            WHERE
                sum_rh IS NOT NULL AND
                flared IS NOT NULL
            ORDER BY
                month
        ''').format(
            table = sql.Identifier('combined_flare_%s' % self.timestamp),
        )
        
        db.do_sql(self.cursor, query)
        
        # set of state/operators
        self.keys = set()
        
        # prepare to build a data frame
        rows = []
        
        for state, month, operator, sum_rh, flared in self.cursor:
            rows.append({
                'state'    : state,
                'month'    : month,
                'operator' : operator,
                'sum_rh'   : sum_rh,
                'flared'   : flared,
            })
            
            self.keys.add((state, operator))
            
        self.df = pd.DataFrame(rows)

        print("keys: %s" % repr(self.keys))
        
        print("dataframe: %s" % self.df)
    
    def plot_correlation(self, state, operator, df):
        '''
        plot correlation between reported and measured
        '''
        title = '%s %s' % (state, operator)
        sns.jointplot(x="sum_rh", y="flared", data=df, dropna=True, kind='reg')
        plt.suptitle(title)
        file = re.sub(r'\W+', '_', title).lower()
        plt.savefig(os.path.join(graphs_subdir, 'correlation_%s.png' % file))
    
    def pearson(self, df):
        '''
        computer Pearson correlation
        '''
        if len(df) < 2:
            return (None, None, None)
        
        x, y = "sum_rh", "flared"
        coeff, p = scipy.stats.pearsonr(df[x], df[y])
        coeff, p = round(coeff, 3), round(p, 3)
        conclusion = "Significant" if p < 0.05 else "Non-Significant"
        print("Pearson: %s %s" % (p, conclusion))
        return (coeff, p, conclusion)
    
    def sk_coef(self, state, operator, df):
        '''
        sklearn based coefficient
        '''
        if len(df) < 15:
            print("Too small for sk_learn: %s" % len(df))
            return (None, None)

        ## split data
        train, test = model_selection.train_test_split(df, test_size=1/3)

        # Assigning values before k-fold
        X_train = train["sum_rh"].values.reshape(-1,1)
        y_train = train["flared"].values.reshape(-1,1)
        X_test = test["sum_rh"].values.reshape(-1,1)
        y_test = test["flared"].values.reshape(-1,1)

        ## call model
        model = linear_model.LinearRegression()

        ## K fold validation
        scores = []
        coeffs = []
        
        nsplit = self.nsplit
        if nsplit > len(X_train):
            nsplit = len(X_train)

        cv = model_selection.KFold(n_splits=nsplit, shuffle=True)
        fig = plt.figure()
        i = 1
        for train, test in cv.split(X_train, y_train):
            prediction = model.fit(X_train[train],
                     y_train[train]).predict(X_train[test])
            true = y_train[test]
            if model.coef_[0] >= 0.0:
                coeffs.append(model.coef_[0])
            else:
                print("Skipping negative coefficient: %s" % model.coef_[0])
            score = metrics.r2_score(true, prediction)
            scores.append(score)
            plt.scatter(prediction, true, lw=2, alpha=0.3, label='Fold %d (R2 = %0.2f)' % (i,score))
            i = i + 1
        
        flat_coeffs = [item for sublist in coeffs for item in sublist]
        plt.plot([min(y_train),max(y_train)], [min(y_train),max(y_train)], linestyle='--', lw=2, color='black')
        plt.xlabel('predicted')
        plt.ylabel('sum_rh')
        title = '%s %s' % (state, operator)
        plt.title('K-Folds of ' + title)
        plt.legend()
        file = re.sub(r'\W+', '_', title).lower()
        plt.savefig(os.path.join(graphs_subdir, 'sklearn_%s.png' % file))

        coeff_list = [item for sublist in coeffs for item in sublist]

        if len(coeffs) > 0:
            # average results
            avg_factor = float(sum(coeffs)/len(coeffs))
        else:
            # no usable coefficients found
            avg_factor = None

        print("coeff_list: %s" % repr(coeff_list))
        print("avg_factor: %s" % avg_factor)
        
        return (avg_factor, coeff_list)

    def curve_fit_coef(self, state, operator, df):
        '''
        curve_fit based coefficient
        '''
        sum_rh = df['sum_rh'].to_numpy()
        flared = df['flared'].to_numpy()
  
        if len(df) == 1:
            # one data point, resort to simple division
            if sum_rh[0] == 0:
                # avoid division by zero
                return None

            result = flared[0] / sum_rh[0]
        
        else:
            # simple linear function starting at 0
            def f(x, a):
                #print("f(%s,%s)" % (x,a)) 
                return x * a
        
            # curve fit
            popt, pcov = curve_fit(f, sum_rh, flared)
            
            result = popt[0]
        
        print("curve_fit_coefficient: %s" % result)
        
        # plot the fit
        plt.figure()
        plt.scatter(sum_rh, flared, lw=2, alpha=0.3)
        plt.plot([0, max(sum_rh)], [0, max(sum_rh) * result], linestyle='--', color='black')
        # lw=2
        plt.xlabel('predicted')
        plt.ylabel('sum_rh')
        title = '%s %s' % (state, operator)
        plt.title('Curve Fit ' + title)
        plt.legend()
        file = re.sub(r'\W+', '_', title).lower()
        plt.savefig(os.path.join(graphs_subdir, 'curve_fit_%s.png' % file))
        
        return result

    def build_output(self):
        '''
        build our output table
        '''
        query = sql.SQL('''
            DROP VIEW IF EXISTS {output_view};
        
            DROP TABLE IF EXISTS {output_table};
        
            CREATE TABLE {output_table}
            (
                -- state abbreviation
                state      TEXT, 
                -- operator name
                operator   TEXT,

                -- pearson correlation
                pearson    FLOAT,
                p          FLOAT, 
                conclusion TEXT,
                
                -- coefficient list from sk learn trials
                coeff_list FLOAT[],

                -- sk learn derived coefficient
                sk_learn FLOAT,
                -- curve fit derived coefficient
                curve    FLOAT,
                -- average of two approaches
                avg_coef FLOAT
            );

            CREATE INDEX ON {output_table} (state ASC, operator ASC);

            GRANT SELECT ON {output_table} TO internal_read_only;
            
            CREATE VIEW {output_view} AS
            SELECT
                *
            FROM
                {output_table};

            GRANT SELECT ON {output_view} TO internal_read_only;
        ''').format(
            output_table = self.output_table,
            output_view = self.output_view,
        )
        
        db.do_sql(self.cursor, query)
    
    def run(self):
    
        # load data
        self.load()
        
        # build output table
        self.build_output()
        
        # Pre make graphs subdr to store output charts of correlations
        if not os.path.exists(graphs_subdir):
            os.mkdir(graphs_subdir)

        # iterate over keys
        for state, operator in self.keys:
            subdf = self.df[(self.df['state'] == state) & (self.df['operator'] == operator)]
            print("Doing: %s %s" % (state, operator))
            print("subdf: %s" % subdf)
            pear, p, conclusion = self.pearson(subdf)
            self.plot_correlation(state, operator, subdf)
            
            if conclusion == 'Significant':
                print("Find averaged coefficient")
                sk_learn, coeff_list = self.sk_coef(state, operator, subdf)
                curve = self.curve_fit_coef(state, operator, subdf)

            else:
                print("Skip coefficient due to lack of correlation")
                sk_learn = None
                coeff_list = []
                curve = None
                
            # pick or average
            if curve is None:
                avg_coef = sk_learn
            elif sk_learn is None:
                avg_coef = curve
            else:
                avg_coef = (curve + sk_learn) / 2.0
             
            print("pearson: %s" % repr(pear))
            print("p: %s" % repr(p))
            print("conclusion: %s" % repr(conclusion))
            print("coeff_list: %s" % repr(coeff_list))
            print("sk_learn: %s" % repr(sk_learn))
            print("curve: %s" % repr(curve))
   
            # insert row
            query = sql.SQL('''
                INSERT INTO {output_table}
                (state, operator, pearson, p, conclusion, coeff_list,
                 sk_learn, curve, avg_coef)
                VALUES
                ({state}, {operator}, {pearson}, {p}, {conclusion}, {coeff_list},
                 {sk_learn}, {curve}, {avg_coef})
            ''').format(
                output_table = self.output_table,
                
                state = sql.Literal(state),
                operator = sql.Literal(operator),
                pearson = sql.Literal(pear),
                p = sql.Literal(p),
                conclusion = sql.Literal(conclusion),
                coeff_list = sql.Literal(coeff_list),
                sk_learn = sql.Literal(sk_learn),
                curve = sql.Literal(curve),
                avg_coef = sql.Literal(avg_coef),
            )

            db.do_sql(self.cursor, query)
        
        self.conn.commit()
        
        return self.output_table
        
def main():
    parser = argparse.ArgumentParser(description='Flare Fit')

    parser.add_argument("-t", "--timestamp", type=str,
                    help="run as this specific timestamp")

    args = parser.parse_args()

    try:
        f = FlareFit(args.timestamp)

        f.run()

    except Exception as e:
        #send_slack('operations', "@channel build_views needs attention: \n error: %s\n build_view arguments: %s" % (e, sys.argv[1:]))
        # make sure we don't throw stuff just into the slack abyss, also on the terminal/log
        raise

if __name__ == "__main__":
    main()
