from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
 
def create_cpi_rent_view(session):
    session.use_schema('HARMONIZED')
 
    # Creating a DataFrame for the BUREAU_OF_LABOR_STATISTICS_PRICE_TIMESERIES table
    price_timeseries = session.table("FINANCIAL__ECONOMIC_ESSENTIALS.CYBERSYN.BUREAU_OF_LABOR_STATISTICS_PRICE_TIMESERIES")
 
    # Applying the SQL logic using Snowpark DataFrame transformations
    cpi_rent_df = price_timeseries \
        .filter((F.col("VALUE").is_not_null())) \
        .filter(F.col("VARIABLE_NAME").like('CPI: Rent of primary residence, Not seasonally adjusted, Annual')) \
        .select(F.col("GEO_ID"), F.year(F.col("DATE")).cast("STRING").alias("yr"), F.col("VALUE")) \
        .groupBy(F.col("GEO_ID"), F.col("yr")) \
        .agg(F.max(F.col("VALUE")).alias("CPI_Rent_of_Primary_Residence"))
 
 
 
    # Creating or replacing the view
    cpi_rent_df.create_or_replace_view("CPI_RENT_VIEW")
 
def test_cpi_rent_view(session):
    session.use_schema('HARMONIZED')
    tv = session.table('CPI_RENT_VIEW')
    tv.limit(5).show()
 
# Local debugging block (similar to the one in your provided script)
if __name__ == "__main__":
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
 
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()
 
    create_cpi_rent_view(session)
    test_cpi_rent_view(session)
 
    session.close()