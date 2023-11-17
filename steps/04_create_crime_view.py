#------------------------------------------------------------------------------
# Hands-On Lab: Data Engineering with Snowpark
# Script:       04_create_order_view.py
# Author:       Jeremiah Hansen, Caleb Baechtold
# Last Updated: 1/9/2023
#------------------------------------------------------------------------------
 
# SNOWFLAKE ADVANTAGE: Snowpark DataFrame API
# SNOWFLAKE ADVANTAGE: Streams for incremental processing (CDC)
# SNOWFLAKE ADVANTAGE: Streams on views
 
 
from snowflake.snowpark import Session
#import snowflake.snowpark.types as T
import snowflake.snowpark.functions as F
 
 
def create_crime_view(session):
    session.use_schema('HARMONIZED')
 
    urban_crime_timeseries = session.table("CRIME_STATISTICS.CYBERSYN.URBAN_CRIME_TIMESERIES").select(F.col("geo_id"), \
                                                                                     F.year(F.col("date")).cast("STRING").alias("year"), \
                                                                                     F.col("city"), \
                                                                                     F.col("variable"), \
                                                                                     F.col("variable_name"), \
                                                                                     F.col("value"))
    geography_index = session.table("CRIME_STATISTICS.CYBERSYN.GEOGRAPHY_INDEX").select(F.col("geo_id"), \
                                                                       F.col("geo_name"), \
                                                                       F.col("level"))
    urban_crime_attributes = session.table("CRIME_STATISTICS.CYBERSYN.URBAN_CRIME_ATTRIBUTES").select(F.col("variable"), \
                                                                                     F.col("variable_name"), \
                                                                                     F.col("offense_category"), \
                                                                                     F.col("unit"), \
                                                                                     F.col("frequency"), \
                                                                                     F.col("measure"))
    geography_relationships = session.table("CRIME_STATISTICS.CYBERSYN.GEOGRAPHY_RELATIONSHIPS").select(F.col("geo_name"), \
                                                                                       F.col("level"), \
                                                                                       F.col("geo_id"), \
                                                                                       F.col("related_geo_id"), \
                                                                                       F.col("related_geo_name"), \
                                                                                       F.col("related_level"))
                                                                       
 
 
 
    
    '''
    We can do this one of two ways: either select before the join so it is more explicit, or just join on the full tables.
    The end result is the same, it's mostly a readibility question.
    '''
    # order_detail = session.table("RAW_POS.ORDER_DETAIL")
    # order_header = session.table("RAW_POS.ORDER_HEADER")
    # truck = session.table("RAW_POS.TRUCK")
    # menu = session.table("RAW_POS.MENU")
    # franchise = session.table("RAW_POS.FRANCHISE")
    # location = session.table("RAW_POS.LOCATION")
 
    t_with_g = urban_crime_timeseries.join(geography_index, urban_crime_timeseries['geo_id'] == geography_index['geo_id'], rsuffix='_f')
 
    oh_w_t_and_l = urban_crime_attributes.join(t_with_g, urban_crime_attributes['variable'] == t_with_g['variable'], rsuffix='_t')
                               
    final_df = geography_relationships.join(oh_w_t_and_l, geography_relationships['geo_id'] == oh_w_t_and_l['geo_id'], rsuffix='_oh')
                    
    
 
 
 
    final_df = final_df.select(F.col("GEO_ID"), \
                            F.col("GEO_NAME"), \
                            F.col("LEVEL"), \
                            F.col("RELATED_GEO_ID"), \
                            F.col("RELATED_GEO_NAME"), \
                            F.col("RELATED_LEVEL"), \
                            F.col("YEAR"), \
                            F.col("CITY"), \
                            F.col("VARIABLE"), \
                            F.col("VARIABLE_NAME"), \
                            F.col("VALUE"), \
                            F.col("OFFENSE_CATEGORY"), \
                            F.col("UNIT"), \
                            F.col("FREQUENCY"), \
                            F.col("MEASURE"))
   # final_df.create_or_replace_view('POS_FLATTENED_V')
 
    for column in final_df.columns:
        final_df = final_df.filter(F.col(column).is_not_null())
 
    final_df.create_or_replace_view("URBAN_CRIME_STATISTICS_V")
    
"""def create_crime_view_stream(session):
    session.use_schema('HARMONIZED')
    _ = session.sql('CREATE OR REPLACE STREAM URBAN_CRIME_STATISTICS_V_STREAM \
                        ON URBAN_CRIME_STATISTICS_V \
                        SHOW_INITIAL_ROWS = TRUE').collect()"""
    
def test_crime_view(session):
    session.use_schema('HARMONIZED')
    tv = session.table('URBAN_CRIME_STATISTICS_V')
    tv.limit(5).show()
 
 
# For local debugging
if __name__ == "__main__":
    # Add the utils package to our path and import the snowpark_utils function
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
 
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    create_crime_view(session)
    #create_crime_view_stream(session)
    test_crime_view(session)
 
    session.close()