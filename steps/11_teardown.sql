/*-----------------------------------------------------------------------------
Hands-On Lab: Data Engineering with Snowpark
Script:       11_teardown.sql
Author:       Jeremiah Hansen
Last Updated: 1/9/2023
-----------------------------------------------------------------------------*/

-- Use accountadmin so that you are able to drop everything
USE ROLE ACCOUNTADMIN;

-- Drop the created database 
DROP DATABASE BIG_DB;

-- Drop the warehouse
DROP WAREHOUSE BIG_WH;

-- Drop the Roles
DROP ROLE BIG_ROLE;

-- Drop the marketplace databases
DROP DATABASE US_HOUSING__REAL_ESTATE_ESSENTIALS;

DROP DATABASE US_POINTS_OF_INTEREST__ADDRESSES;

DROP DATABASE FINANCIAL__ECONOMIC_ESSENTIALS;

DROP DATABASE CRIME_STATISTICS;
