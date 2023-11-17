from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
 
def create_home_mortgage_view(session):
    session.use_schema('HARMONIZED')
    
    home_mortgage_df = session.table("US_HOUSING__REAL_ESTATE_ESSENTIALS.CYBERSYN.HOME_MORTGAGE_DISCLOSURE_ATTRIBUTES")\
                              .select(F.col("YEAR"), \
                                      F.col("MSA_GEO_ID"), \
                                      F.col("LOAN_AMOUNT"), \
                                      F.col("INTEREST_RATE"), \
                                      F.col("PROPERTY_VALUE"))\
                              .where((F.col("LOAN_PURPOSE") == 'Home purchase') & \
                                     (F.col("YEAR").is_not_null()) & \
                                     (F.col("MSA_GEO_ID").is_not_null()) & \
                                     (F.col("LOAN_AMOUNT").is_not_null()) & \
                                     (F.col("INTEREST_RATE").is_not_null()) & \
                                     (F.col("PROPERTY_VALUE").is_not_null()))
    
    home_mortgage_df.create_or_replace_view('HOME_MORTGAGE_VIEW')
 
def test_home_mortgage_view(session):
    session.use_schema('HARMONIZED')
    hv = session.table('HOME_MORTGAGE_VIEW')
    hv.limit(5).show()
 
# For local debugging
if __name__ == "__main__":
    # Add the utils package to our path and import the snowpark_utils function
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
 
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    create_home_mortgage_view(session)
    test_home_mortgage_view(session)  # Test the view
 
    session.close()