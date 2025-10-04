import functions_framework
from google.cloud import bigquery
import os

@functions_framework.http
def transform_data(request):
    """
    Triggers a BigQuery query to transform data from the staging table 
    and save it to the final analytics table, handling partitioning automatically.
    """
    
    # BigQuery configuration
    project_id = os.environ.get('GCP_PROJECT')
    staging_dataset_id = "yelp_landing"
    staging_table_id = "reviews_raw"
    target_dataset_id = "yelp_analytics" 
    target_table_id = "reviews"
    
    # The transformation logic
    sql_query = f"""
    MERGE `{project_id}.{target_dataset_id}.{target_table_id}` AS target
    USING (
        SELECT DISTINCT
            review_id,
            user_id,
            business_id,
            stars,
            text,
            date
        FROM `{project_id}.{staging_dataset_id}.{staging_table_id}`
        WHERE 
            LENGTH(TRIM(text)) > 0 
            AND date IS NOT NULL
            AND stars IS NOT NULL
    ) AS source
    ON target.review_id = source.review_id
    WHEN NOT MATCHED THEN
        INSERT (review_id, user_id, business_id, stars, text, date)
        VALUES (source.review_id, source.user_id, source.business_id, 
                source.stars, source.text, source.date)
    """

    print("Starting BigQuery MERGE (race-condition safe) transformation...")

    client = bigquery.Client()
    query_job = client.query(sql_query)
    query_job.result()

    print(f"MERGE completed. {query_job.num_dml_affected_rows} new rows inserted.")

    return "Transformation successful!", 200