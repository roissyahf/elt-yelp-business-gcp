import functions_framework
from google.cloud import bigquery
import os
import requests 
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token

# The actual deployed URL of Cloud Function 2
TRANSFORM_FUNCTION_URL = "https://elt-yelp-business-transform-bigquery-data-763994663224.asia-southeast2.run.app" 

@functions_framework.cloud_event
def load_data(cloud_event):
    """
    Triggers when a file is uploaded to the designated Cloud Storage bucket.
    Loads the JSON data into BigQuery, and then triggers the Transform Function.
    """
    
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]
    project_id = os.environ.get('GCP_PROJECT')
    
    # Ensure the file is in the correct folder and is a JSON file
    if not file_name.startswith("elt-inbound/") or not file_name.endswith(".json"):
        print(f"File {file_name} does not match expected prefix or extension. Skipping.")
        return "Not a valid ELT file.", 200 # Return 200 to indicate successful function execution, but data skip

    # Target table for the raw data
    dataset_id = "yelp_landing" 
    table_id = "reviews_raw"
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    source_uri = f"gs://{bucket_name}/{file_name}"

    print(f"Loading file {source_uri} into BigQuery table {table_ref}...")

    # Initialize the BigQuery client
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        # Append data to the existing staging table
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    
    # EXECUTE THE LOAD JOB
    try:
        load_job = client.load_table_from_uri(
            source_uri,
            table_ref,
            job_config=job_config
        )
        load_job.result()
        print(f"Load job completed. {load_job.output_rows} rows loaded.")
        
    except Exception as e:
        print(f"Error during BigQuery load job: {e}")
        return f"BigQuery Load Failed: {e}", 500
        
    # TRIGGER THE TRANSFORM FUNCTION (CF2)
    try:
        print(f"Securely triggering Cloud Function 2 at: {TRANSFORM_FUNCTION_URL}")
        
        # Get the ID token for authentication
        auth_req = GoogleAuthRequest()
        identity_token = id_token.fetch_id_token(auth_req, TRANSFORM_FUNCTION_URL)

        # Make the authenticated POST request (without a body to avoid the 400 error)
        response = requests.post(
            TRANSFORM_FUNCTION_URL,
            headers={"Authorization": f"Bearer {identity_token}"}
        )
        response.raise_for_status() # Raise exception for 4xx or 5xx status codes

        print(f"Successfully triggered Cloud Function 2. Status: {response.status_code}")
        
    except Exception as e:
        # Log the trigger failure but allow CF1 to succeed since its primary job (Load) is done
        print(f"Warning: Load Success, but Transform Trigger Failed: {e}")
        return f"Load Success, but Transform Trigger Failed: {e}", 200 
        
    return "Pipeline (Load and Trigger) successful!", 200
