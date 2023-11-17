from snowflake.snowpark import Session
import snowflake.snowpark.functions as F

def create_home_purchase_data_view(session):
    session.use_schema('ANALYTICS')

    # Define the DataFrames
    home_purchase_data = session.table("BIG_DB.HARMONIZED.HOME_MORTGAGE_VIEW") \
                                .filter((F.col("year").is_not_null()) &
                                        (F.col("msa_geo_id").is_not_null()) &
                                        (F.col("loan_amount").is_not_null()) &
                                        (F.col("interest_rate").is_not_null()) &
                                        (F.col("property_value").is_not_null()))

    rent_data = session.table("BIG_DB.HARMONIZED.CPI_RENT_VIEW") \
                      .filter((~F.col("GEO_ID").like('country%')))

    geo_data = session.table("BIG_DB.HARMONIZED.GEO_VIEW")

    # Join DataFrames
    joined_df = home_purchase_data.join(rent_data, (home_purchase_data['msa_geo_id'] == rent_data['GEO_ID']) & (home_purchase_data['year'] == rent_data['yr'])) \
                                  .join(geo_data, home_purchase_data['msa_geo_id'] == geo_data['GEO_ID'])

    # Aggregate Data
    aggregated_df = joined_df.group_by("year",
                                       "msa_geo_id",
                                       "GEO_NAME",
                                       "interest_rate",
                                       "CPI_Rent_of_Primary_Residence") \
                             .agg(F.avg("property_value").alias("avg_property_value"),
                                  F.avg("loan_amount").alias("avg_loan_amount"))

    # Remove Null Values and Create View
    final_view = aggregated_df.select("year",
                                      "msa_geo_id",
                                      "GEO_NAME",
                                      "avg_loan_amount",
                                      "interest_rate",
                                      "avg_property_value",
                                      "CPI_Rent_of_Primary_Residence").na.drop()

    final_view.create_or_replace_view("HOME_PURCHASE_DATA_VIEW")

def test_create_home_purchase_data_view(session):
    session.use_schema('ANALYTICS')
    tv = session.table('HOME_PURCHASE_DATA_VIEW')
    tv.limit(5).show()

# For local debugging
if __name__ == "__main__":
    import os, sys
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from utils import snowpark_utils
    session = snowpark_utils.get_snowpark_session()

    create_home_purchase_data_view(session)
    test_create_home_purchase_data_view(session)

    session.close()
