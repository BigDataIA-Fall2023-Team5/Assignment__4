from snowflake.snowpark import Session
#import snowflake.snowpark.types as T
import snowflake.snowpark.functions as F
 
def calculate_crime_unemployment_ratio(session):
    # Assuming session is already established with Snowflake
    session.use_schema('ANALYTICS')
    # Define the first subquery for urban crime statistics
    urban_crime_stats = session.table("BIG_DB.HARMONIZED.URBAN_CRIME_STATISTICS_V").select(
        F.col("related_geo_id").alias("geo_id"),
        F.col("geo_name"),
        F.col("city"),
        F.col("year"),
        F.col("value")
    ).where(
        (F.col("variable_name") == "Daily count of incidents, all incidents") &
       ( F.col("related_geo_id").regexp('^geoId/[0-9]{7}$'))
    ).group_by(
        "geo_id", "year", "city", "geo_name"
    ).agg(
        F.sum("value").alias("annual_incidents")
    )
 
    # Define the second subquery for labor statistics
    labor_stats = session.table("BIG_DB.HARMONIZED.BLS_EMPLOYMENT_V").select(
        F.col("GEO_ID"),
        F.col("year"),
        F.col("VALUE")
    ).where(
        (F.col("VARIABLE_NAME") == "Local Area Unemployment: Unemployment Rate, Not seasonally adjusted, Annual") &
        (F.col("GEO_ID").regexp('^geoId/[0-9]{7}$'))
    ).group_by(
        "GEO_ID", "year"
    ).agg(
        F.avg("VALUE").alias("value")
    )
 
    # Perform the join
    joined_df = urban_crime_stats.join(
        labor_stats,
        (urban_crime_stats["geo_id"] == labor_stats["GEO_ID"]) &
        (urban_crime_stats["year"] == labor_stats["year"])
    )
 
    # Calculate the crime to unemployment ratio
    final_df = joined_df.select(
        urban_crime_stats["geo_name"],
        urban_crime_stats["city"],
        urban_crime_stats["year"].alias("year"),
        urban_crime_stats["annual_incidents"],
        labor_stats["value"].alias("unemployment_rate"),
        F.when(labor_stats["value"] == 0, None).otherwise(
            urban_crime_stats["annual_incidents"] / labor_stats["value"]
        ).alias("crime_unemployment_ratio")
    )
 
 
# For local testing or execution
    final_df.create_or_replace_view("CRIME_UNEMPLOYMENT_RATIO_V")
    
"""def create_crime_view_stream(session):
    session.use_schema('HARMONIZED')
    _ = session.sql('CREATE OR REPLACE STREAM URBAN_CRIME_STATISTICS_V_STREAM \
                        ON URBAN_CRIME_STATISTICS_V \
                        SHOW_INITIAL_ROWS = TRUE').collect()
"""
def test_calculate_crime_unemployment_ratio(session):
    session.use_schema('ANALYTICS')
    tv = session.table('CRIME_UNEMPLOYMENT_RATIO_V')
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
 
    calculate_crime_unemployment_ratio(session)
    #create_crime_view_stream(session)
    test_calculate_crime_unemployment_ratio(session)
 
    session.close()
 