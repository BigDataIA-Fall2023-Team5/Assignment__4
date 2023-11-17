from snowflake.snowpark import Session
import snowflake.snowpark.functions as F

def analyze_employment_and_poi_data(session):
    session.use_schema('ANALYTICS')

    # Define the DataFrames for the employment and points of interest views
    bls_employment_df = session.table("BIG_DB.HARMONIZED.BLS_EMPLOYMENT_V").select(
        F.col("geo_id"),
        F.col("VARIABLE_NAME"),
        F.col("VALUE")
    ).filter(F.col("geo_id").is_not_null())

    us_poi_df = session.table("BIG_DB.HARMONIZED.US_POI_V").select(
        F.col("related_geo_id"),
        F.col("city"),
        F.col("state"),
        F.col("CATEGORY_MAIN")
    ).filter(
        F.col("city").is_not_null() & 
        F.col("state").is_not_null()
    )

    # Perform the join
    joined_df = bls_employment_df.join(
        us_poi_df,
        bls_employment_df["geo_id"] == us_poi_df["related_geo_id"]
    )

    # Calculate aggregates
    aggregated_df = joined_df.group_by(
        bls_employment_df["geo_id"],
        us_poi_df["city"],
        us_poi_df["state"]
    ).agg(
        F.avg(F.when(bls_employment_df["VARIABLE_NAME"].like('%Unemployment%'), bls_employment_df["VALUE"])).alias("avg_unemployment_rate"),
        F.count(F.when(us_poi_df["CATEGORY_MAIN"].like('%school%') | us_poi_df["CATEGORY_MAIN"].like('%education%'), 1)).alias("total_schools"),
        F.count(F.when(us_poi_df["CATEGORY_MAIN"].like('%Health%') | us_poi_df["CATEGORY_MAIN"].like('%care%'), 1)).alias("total_healthcare"),
        F.count(F.when(us_poi_df["CATEGORY_MAIN"].like('%Restaurant%') | us_poi_df["CATEGORY_MAIN"].like('%food%'), 1)).alias("total_food_beverage")
    )

    # Filter to remove rows with nulls in aggregated fields
    final_df = aggregated_df.filter(
        F.col("avg_unemployment_rate").is_not_null() &
        F.col("total_schools").is_not_null() &
        F.col("total_healthcare").is_not_null() &
        F.col("total_food_beverage").is_not_null()
    )

    # Create or replace view
    final_df.create_or_replace_view("EMPLOYMENT_POI_ANALYSIS_V")

def test_analyze_employment_and_poi_data(session):
    session.use_schema('ANALYTICS')
    tv = session.table('EMPLOYMENT_POI_ANALYSIS_V')
    tv.limit(5).show()

# For local debugging
if __name__ == "__main__":
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()

    analyze_employment_and_poi_data(session)
    test_analyze_employment_and_poi_data(session)

    session.close()
