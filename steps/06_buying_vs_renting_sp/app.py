from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
 
def get_home_purchase_data_by_geoid(session: Session, input_geo_id: str):
    # Query the view with the given inputs
    results = session.table("BIG_DB.ANALYTICS.HOME_PURCHASE_DATA_VIEW").filter(
        (F.col("msa_geo_id") == input_geo_id)
    ).select(
        "year",
        "msa_geo_id",
        "GEO_NAME",
        "avg_loan_amount",
        "interest_rate",
        "avg_loan_amount",
        "CPI_Rent_of_Primary_Residence"
    ).collect()
 
 
    # Return the results
    return results
 
def main(input_geo_id):
    # Initialize Snowflake session
    # Replace this with your actual method of initializing the Snowflake session
    current_dir = os.getcwd()
    parent_parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(parent_parent_dir)
 
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    # Call the function to get the crime-unemployment ratio
    results = get_home_purchase_data_by_geoid(session, input_geo_id)
 
    # Close the Snowflake session
    session.close()
 
    # Return or print the results
    return results
 
# For local debugging
if __name__ == '__main__':
    import os, sys
 
    if len(sys.argv) == 2:
        print(main(sys.argv[1]))
    else:
        print("Usage: script.py <input_geo_id> ")