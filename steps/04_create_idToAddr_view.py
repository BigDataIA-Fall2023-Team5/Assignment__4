from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
 
def create_geo_view(session):
    session.use_schema('HARMONIZED')
 
    # Creating the DataFrame for the GEOGRAPHY_RELATIONSHIPS table
    geography_relationships = session.table("FINANCIAL__ECONOMIC_ESSENTIALS.CYBERSYN.GEOGRAPHY_RELATIONSHIPS").select(
        F.col("GEO_NAME"),
        F.col("GEO_ID")
    )
 
    # Creating or replacing the view
    geography_relationships.create_or_replace_view('GEO_VIEW')
 
def test_geo_view(session):
    session.use_schema('HARMONIZED')
    gv = session.table('GEO_VIEW')
    gv.limit(5).show()
 
# For local debugging
if __name__ == "__main__":
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
 
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    create_geo_view(session)
    test_geo_view(session)
 
    session.close()