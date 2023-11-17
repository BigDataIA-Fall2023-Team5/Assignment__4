from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
 
def create_bls_employment_view(session):
    session.use_schema('HARMONIZED')
 
    # Selecting the table
    bls_timeseries = session.table("FINANCIAL__ECONOMIC_ESSENTIALS.CYBERSYN.BUREAU_OF_LABOR_STATISTICS_EMPLOYMENT_TIMESERIES").select(
        F.col("GEO_ID"),
        F.col("VARIABLE_NAME"),
        F.col("VALUE"),
        F.year(F.col("DATE")).cast("STRING").alias("year")
    )
 
    # Adding the WHERE clause conditions
    filtered_bls = bls_timeseries.filter(
        (F.col("GEO_ID").regexp('^geoId/[0-9]{7}$')) &
        (F.col("VARIABLE_NAME").isin(
            'JOLTS: Layoffs and discharges, Total nonfarm, All size classes, Not seasonally adjusted, Annual, Level',
            'JOLTS: Job openings, Total nonfarm, All size classes, Not seasonally adjusted, Annual, Level',
            'JOLTS: Hires, Total nonfarm, All size classes, Not seasonally adjusted, Annual, Level',
            'JOLTS: Quits, Total nonfarm, All size classes, Not seasonally adjusted, Annual, Level',
            'Local Area Unemployment: Unemployment Rate, Not seasonally adjusted, Annual'
        )) &
        (F.col("GEO_ID").is_not_null()) &
        (F.col("VALUE").is_not_null()) &
        (F.col("DATE").is_not_null())
    )
 
    # Creating or replacing the view
    filtered_bls.create_or_replace_view("BLS_EMPLOYMENT_V")
 
def test_bls_employment_view(session):
    session.use_schema('HARMONIZED')
    tv = session.table('BLS_EMPLOYMENT_V')
    tv.limit(5).show()
 
 
# For local debugging
if __name__ == "__main__":
    # Assuming utils and snowpark_utils are set up as in the previous script
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)


    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    create_bls_employment_view(session)
    test_bls_employment_view(session)
 
    session.close()