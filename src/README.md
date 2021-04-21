**Overview**  

This repository contains SQL queries and scripts necessary to recreate the processed data and results published in *flaringmonitor/viirs-flare-data/processed*. The repo contains a list of commands necessary to process Flaring Monitor raw data files into Flaring Monitored processed data.  

The code returns the output of each major stage of the Methodology outlined within the Flaring Monitor White Paper (April 2021) and allows for the independent verification of each step. 

To improve performance of new raw data updates, the Process outlined only reprocesses the most recent months and recombines them with older pre-processed data. 

The SQL code makes extensive use of "geo-joins" using the PostGIS extension and GIST indexes where necessary. 

Input data files for Flaring Monitor VIIRS code located in *flaringmonitor/viirs-flare-code* repo. 

Ongoing data updates and refreshes will be pushed to this repo.

We strongly recommend loading data files into a Postgres SQL database given Excel file size limitations. 

**First Time Processing**  

If you are running Flare Monitor code for the first time, follow the steps below to setup a raw data database. If you have already run the code before, please jump to the next section "**Processing Future Updates**".  

1. Create a database or flare_automation schema on your postgres 11 server. 

   **Note:** A postgres server with 32 GB of RAM and a local SSD disk / cache is recommended.

2. See *createdb.sql* for example SQL. The 'postgis' and 'btree_gist' extensions must be installed to ensure all queries run smoothly.

3. Copy *local_settings.py.template* to local_settings.py and edit to match your server settings.

4. The *flaringmonitor/viirs-flare-data* repo contains compressed CSV files used to populate initial demonstration tables. The scripts published under *flaringmonitor/viirs-flare-code/src* by default assumes the data repo will be cloned under the same parent directory as where the *flaringmonitor/viirs-flare-code* repo is cloned under. 

5. The demonstration source tables are loaded using the script: *./load_tables.sh*

6. The first run requires a build of historic tables followed by the current tables. This will take several hours but for future updates it will only require rebuilding the current tables. Use the script *./build_all.sh* to build the historical and current tables for the first time.

7. Use the script *FlareFit.py* to fit VIIRS recorded radiant heat vs state reported flared volumes. 

   a. This script produces graphs with fit visualizations, under the graphs sub directory. Following are the three types of graphs that are produced:  

    <table>
    <thead>
    <tr>
    <th>Graph Title</th>
    <th>Description</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td>correlation_STATE_OPERATOR.png</td>
    <td>Scatter plot by basin or state-company combination representing sum of satellite observed radiant heat measurements in time megawatts on the x axis and reported flaring volume in mcf on the y axis</td>
    </tr>
    <tr>
    <td>curve_fit_STATE_OPERATOR.png</td>
    <td>correlation_STATE_OPERATOR.png scatter plot with a linear curve fit  on the data </td>
    </tr>
    <tr>
    <td>sklearn_STATE_OPERATOR.png</td>
    <td>Scatter plot that depicts various combinations of k fold linear regression fits, where x axis is predicted flaring volumes and y is reported flaring value.</td>
    </tr>
    </tbody>
    </table>

  **Note:** The sklearn regression fits and full curve fit are both used in the final prediction for each operator.

8. The final product is pointed to the view, *flare_automation.operator_estimates*

9. The view *flare_automation.operator_factors* provides scaling factors and correlation parameters.



**Processing Future Updates**  

This section details the steps to update the raw data for future processing. Do not follow these steps if you have not successfully run the above steps at least once.

1. Pull updates to the *flaringmonitor/viirs-flare-data* from github.

2. Run the *load_tables.sh* script to reload data tables.

3. Refresh current tables by running the *Flares.py* script. 

   a. This will build a new timestamped set of tables using previously computed historic data combined with several months look back based on the load of new data. 


