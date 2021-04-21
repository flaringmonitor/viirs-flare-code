-- EXAMPLE DATABASE CREATION SCRIPT, PLEASE SET YOUR OWN PASSWORD!

-- create flaring db user
CREATE ROLE flare_user login password '**YOUR_PASSWORD**';
-- create flaring db
CREATE DATABASE flaredb;
-- connect to flaring db
\c flaredb
-- add postgis extension
CREATE EXTENSION postgis;
-- add gist extension
CREATE EXTENSION btree_gist;
-- create our schema
CREATE SCHEMA flare_automation;
-- grant user schema access
GRANT ALL ON SCHEMA flare_automation TO flare_user;
