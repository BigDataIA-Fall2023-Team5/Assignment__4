from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
 
def get_crime_unemployment_ratio(session, geo_name, city, year):
    # Query the view with the given inputs
    results = session.table("BIG_DB.ANALYTICS.CRIME_UNEMPLOYMENT_RATIO_V").filter(
        (F.col("geo_name") == geo_name) &
        (F.col("city") == city) &
        (F.col("year") == year)
    ).select(
        "geo_name",
        "city",
        "year",
        "annual_incidents",
        "unemployment_rate",
        "crime_unemployment_ratio"
    ).collect()
 
    # Return the results
    return results
 
def main( geo_name, city, year):
    # Initialize Snowflake session
    # Replace this with your actual method of initializing the Snowflake session
    import os, sys
    current_dir = os.getcwd()
    parent_parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(parent_parent_dir)

    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    # Call the function to get the crime-unemployment ratio
    results = get_crime_unemployment_ratio(session, geo_name, city, year)
 
    # Close the Snowflake session
    session.close()
 
    # Return or print the results
    return results
 
# For local debugging
if __name__ == '__main__':
    import os, sys
 
    if len(sys.argv) >= 4:
        print(main(sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        print("Usage: script.py <geo_name> <city> <year>")