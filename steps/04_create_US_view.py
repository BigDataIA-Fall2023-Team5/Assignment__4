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
 
 
def create_us_view(session):
    session.use_schema('HARMONIZED')
 
    geography_index = session.table("US_POINTS_OF_INTEREST__ADDRESSES.CYBERSYN.GEOGRAPHY_INDEX").select(F.col("geo_id"), \
                                                                       F.col("geo_name"), \
                                                                       F.col("level"))
    
 
    geography_relationships = session.table("US_POINTS_OF_INTEREST__ADDRESSES.CYBERSYN.GEOGRAPHY_RELATIONSHIPS").select(F.col("geo_name"), \
        F.col("geo_id"), \
        F.col("RELATED_GEO_NAME"), \
        F.col("related_geo_id"), \
        F.col("related_level"), \
        F.col("relationship_type"))
    
    us_addresses = session.table("US_POINTS_OF_INTEREST__ADDRESSES.CYBERSYN.US_ADDRESSES").select(
        F.col("id_zip").alias("geo_id"),  \
        # Alias to match the join column name
        F.col("address_id"), \
        F.col("city"), \
        F.col("state"), \
        F.col("zip"))
 
    poi_addresses_relationships = session.table("US_POINTS_OF_INTEREST__ADDRESSES.CYBERSYN.POINT_OF_INTEREST_ADDRESSES_RELATIONSHIPS").select(
        F.col("address_id"), \
        F.col("poi_id"), \
        F.col("relationship_type"))
    
    point_of_interest_index = session.table("US_POINTS_OF_INTEREST__ADDRESSES.CYBERSYN.POINT_OF_INTEREST_INDEX").select(
        F.col("poi_id"), \
        F.col("poi_name"), \
        F.col("category_main"))
 
 
    
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
 
    t_with_g = geography_index.join(geography_relationships, geography_index['geo_id'] == geography_relationships['geo_id'], rsuffix='_f')
 
    oh_w_t_and_l = us_addresses.join(t_with_g, us_addresses['geo_id'] == t_with_g['geo_id'], rsuffix='_t')
 
    sol = poi_addresses_relationships.join(oh_w_t_and_l, poi_addresses_relationships['address_id'] == oh_w_t_and_l['address_id'], rsuffix='_oh')
 
    final_df = point_of_interest_index.join(sol, point_of_interest_index['poi_id'] == sol['poi_id'], rsuffix='_sol')
                                     
 
 
    final_df = final_df.select(F.col("GEO_ID"), \
                            F.col("GEO_NAME"), \
                            F.col("LEVEL"), \
                            F.col("RELATED_GEO_ID"), \
                            F.col("RELATED_GEO_NAME"), \
                            F.col("RELATED_LEVEL"), \
                            F.col("ADDRESS_ID"), \
                            F.col("CITY"), \
                            F.col("ZIP"), \
                            F.col("STATE"), \
                            F.col("POI_ID"), \
                            F.col("RELATIONSHIP_TYPE"), \
                            F.col("POI_NAME"), \
                            F.col("CATEGORY_MAIN"))
 
   # final_df.create_or_replace_view('POS_FLATTENED_V')
 
    for column in final_df.columns:
        final_df = final_df.filter(F.col(column).is_not_null())
 
    final_df.create_or_replace_view("US_POI_V")
    
"""def create_us_view_stream(session):
    session.use_schema('HARMONIZED')
    _ = session.sql('CREATE OR REPLACE STREAM US_POI_V_STREAM \
                        ON VIEW US_POI_V \
                        SHOW_INITIAL_ROWS = TRUE').collect()"""
 
def test_crime_view(session):
    session.use_schema('HARMONIZED')
    tv = session.table('US_POI_V')
    tv.limit(5).show()
 
 
# For local debugging
if __name__ == "__main__":
    # Add the utils package to our path and import the snowpark_utils function
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

    print(current_dir)
    print(parent_dir)
    print(sys.path.append(parent_dir))
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    create_us_view(session)
    #create_us_view_stream(session)
    test_crime_view(session)
 
    session.close()