from snowflake.snowpark import Session
import snowflake.snowpark.functions as F

def get_quality_of_life_index(session, geo_id, state, city):
    # Define weights for each component
    weight_unemployment = 0.25
    weight_schools = 0.25
    weight_healthcare = 0.25
    weight_food_beverage = 0.25

    # Max values for normalization
    max_unemployment_rate = 100  # Example max value for unemployment rate
    max_schools_count = 100      # Example max value for total schools
    max_healthcare_count = 100   # Example max value for total healthcare
    max_food_beverage_count = 100 # Example max value for total food & beverage

    # Query the view with the given inputs
    results = session.table("BIG_DB.ANALYTICS.EMPLOYMENT_POI_ANALYSIS_V").filter(
        (F.col("geo_id") == geo_id) &
        (F.col("state") == state) &
        (F.col("city") == city)
    ).select(
        "geo_id",
        "state",
        "city",
        "avg_unemployment_rate",
        "total_schools",
        "total_healthcare",
        "total_food_beverage"
    ).collect()

    # Calculate the Quality of Life Index
    quality_of_life_indices = []
    for row in results:
        normalized_unemployment_rate = (1 - row["AVG_UNEMPLOYMENT_RATE"] / max_unemployment_rate)
        normalized_schools = row["TOTAL_SCHOOLS"] / max_schools_count
        normalized_healthcare = row["TOTAL_HEALTHCARE"] / max_healthcare_count
        normalized_food_beverage = row["TOTAL_FOOD_BEVERAGE"] / max_food_beverage_count

        quality_of_life_index = (weight_unemployment * normalized_unemployment_rate) + \
                                (weight_schools * normalized_schools) + \
                                (weight_healthcare * normalized_healthcare) + \
                                (weight_food_beverage * normalized_food_beverage)
        quality_of_life_indices.append(quality_of_life_index)

    # Return the results
    return quality_of_life_indices

def main(geo_id, state, city):
    # Initialize Snowflake session
    import os, sys
    current_dir = os.getcwd()
    parent_parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(parent_parent_dir)
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()

    # Call the function to get the quality of life index
    results = get_quality_of_life_index(session, geo_id, state, city)

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
