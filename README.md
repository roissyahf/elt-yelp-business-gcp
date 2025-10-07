# **End-to-end Data Analysis Yelp Business Review Project**

This project is **inspired by** end-to-end analytics case studies built by [Ankit Bansal’s (Snowflake + AWS walkthrough)](https://youtu.be/oXLxbk5USFg?si=deFq-iMz8bOqDE9z) using the [Yelp Open Dataset](https://business.yelp.com/data/resources/open-dataset/) but reimagined entirely on Google Cloud Platform (GCP). Additionally, these **business scenario** motivates me to work on this project:
- Customer Experience Monitoring: Shopping & Retail chains analyzing customer reviews across multiple branches to quickly identify recurring issues (e.g., poor service vs. product quality).
- Product & Service Insights: Identifying themes like product variety, staff friendliness, or wait times to guide investments and staff training.
- Proof-of-Concept for Data Teams: Showcasing how a small analytics/data engineering team can build a full pipeline, from ingestion to ML-driven insight.


**The objective** is to: _Design and implement a simple yet extensible ELT pipeline that ingests raw review data into Cloud Storage and maps it into BigQuery. From there, we can do downstream tasks such as sentiment analysis, theme extraction (via Vertex AI), and dashboarding._ **This project demonstrates** how raw text reviews can be transformed into business-ready insights through automation, analytics, and visualization.

---

## **Technology Stack**
- Cloud Functions
- BigQuery
- Cloud Storage
- Vertex AI Workbench
- Power BI (planned Looker Studio, but limited by trial access). 
---

## **Project Structure**

```bash
├───cloud_function
│       cloud_function_1_UPD.py     # Cloud Function 1: Handle the extract, load
│       cloud_function_2_UPD.py     # Cloud Function 2: Handle the transformation
│       requirements.txt            # Requirements for both Cloud Function
│
├───downstream_task
│       downstream-task-t3.ipynb    # Notebook for downstream task
│
├───prepare_and_process
│       get_random_review.py        # Script to get random review from splitted JSON reviews
│       split_large_json_review.py  # Script to split large JSON reviews
|       general_business_category_mapping.ipynb   # Notebook for mapping general business category

```

---

## **[Section I] Yelp Review ELT Pipeline**

This project implements a fully automated, event-driven Extract, Load, and Transform (ELT) pipeline on Google Cloud Platform (GCP) to ingest raw Yelp review data from Cloud Storage into a structured BigQuery analytics table.

The pipeline is triggered every time a new JSON file is uploaded to the designated input Cloud Storage bucket. It is designed to handle out-of-order data arrival and prevent duplicate records in the final analytics table.

### **The Project Workflow**

(flowchart is in progress)


### **Pipeline Components**

<img width="952" height="321" alt="Image" src="https://github.com/user-attachments/assets/0ff49273-2c90-491a-82af-6b415a3c3d01" />

### 1. Cloud Storage (GCS)

| Component | Detail | Purpose |
| :--- | :--- | :--- |
| **Input Bucket** | `yelp-elt-inbound-data` | **Trigger:** New JSON files are uploaded here, triggering the ELT process. |
| **File Format** | Newline-Delimited JSON (NDJSON) | Original Dataset Format. |

### 2. Cloud Function 1: `load_data` (The Load Step)

This function handles the Extract and Load phases.

| Feature | Details |
| :--- | :--- |
| **Trigger** | GCS Event (`google.cloud.storage.object.v1.finalized`) on the input bucket. |
| **Action** | Loads the newly uploaded JSON file directly into the staging BigQuery table. |
| **Behavior** | Uses `WRITE_APPEND` to load all data into the staging table. |
| **Next Step** | Securely triggers Cloud Function 2 (`transform_data`) via an authenticated HTTP request upon successful load. |

### 3. BigQuery Staging Table: `yelp_landing.reviews_raw`

| Feature | Detail |
| :--- | :--- |
| **Purpose** | Temporary storage for raw, unsanitized data. Acts as an audit log. |
| **Data Integrity** | May contain duplicate `review_id` records due to file re-uploads, but this is handled by the next stage. |

### 4. Cloud Function 2: `transform_data` (The Transform Step)

This function handles the core business logic, transformation, and incremental loading.

| Feature | Details |
| :--- | :--- |
| **Trigger** | HTTP request from Cloud Function 1. |
| **Action** | Executes a BigQuery **`MERGE`** statement for atomic, race-condition-safe operations. |
| **Deduplication Logic** | Uses the **`MERGE ... USING ... ON target.review_id = source.review_id WHEN NOT MATCHED THEN`** to ensure records are only inserted once, even with concurrent executions |

### 5. BigQuery Analytics Table: `yelp_analytics.reviews` (The Target)

| Feature | Detail |
| :--- | :--- |
| **Data Integrity** | Contains only unique `review_id` records. |
| **Structure** | **Partitioned** by `date` (truncated to `YEAR`) and **Clustered** by `business_id` for query optimization. |
| **Readiness** | Ready for consumption by downstream tasks. |

### **Data Schema**

**`yelp_landing`**
<img width="776" height="372" alt="Image" src="https://github.com/user-attachments/assets/3107dd52-c7bf-4010-aede-0218a8071204" />

**`yelp_analytics`**
<img width="776" height="342" alt="Image" src="https://github.com/user-attachments/assets/025004d6-232a-4f5a-bed6-6e3103af81d4" />

**`yelp_golden`**
<img width="862" height="512" alt="Image" src="https://github.com/user-attachments/assets/b4e52b9b-7faa-4753-b98b-ac18525978a8" />

---

## **[Section II] Downstream Task: Sentiment Analysis & Theme Extraction**

After completing the ELT pipeline with Cloud Function, I proceeded with downstream analytics to enrich the Yelp reviews data. The processed dataset is stored in a new BigQuery dataset: **`yelp_golden`**.

### **Tasks**

* **Task 1 & 2: Sentiment Analysis**

  * Applied **VADER** for fast sentiment scoring (positive, neutral, negative).
  * Added both **sentiment label** and **sentiment score** to each review.

* **Task 3: Review Theme Extraction**

  * Used **TF-IDF + KMeans clustering** to group reviews into themes.
  * Interpreted clusters into 6 themes relevant to Shopping & Retail:

    * Product Variety & Selection
    * Clothing & Apparel Experience
    * Hair & Beauty Services
    * Customer Service Quality
    * Staff Friendliness & Atmosphere
    * Mall & Food Court Experience

> ⚡Note: These tasks were executed on **Vertex AI Workbench Notebook** for flexibility. BigQuery ML was considered, but initial experiments with thousands of reviews showed longer runtimes.

### **Dashboard**

> ️ Note: This analysis is based on a sample of ~14,700 reviews from a single business category (Shopping & Retail). The results do not represent the entire Yelp dataset or real-world conditions. The purpose is to demonstrate insights that can be derived after the full pipeline (ELT + downstream processing).

* Built a **Power BI dashboard** (original plan was Looker Studio, but access expired after free trial).
* Dashboard design started with business questions and sketching.
* Final dashboard includes:

  * KPIs: Count of reviews, Avg. Star Review, Avg. Star Business
  * Sentiment distribution by theme
  * Star rating distribution by theme (matrix heatmap)
  * Filters for Sentiment

**Dashboard Snapshot**
<img width="943" height="423" alt="Image" src="https://github.com/user-attachments/assets/b2817195-ab03-4ed7-ac9c-943cdc169f31" />

**Key Insights**
- Product Variety & Selection dominates in review volume and is largely positive.
- Clothing & Apparel Experience shows mixed ratings, with a notable skew toward 1-star reviews.
- Hair & Beauty Services performs well overall, with a strong concentration in 5-star reviews and minimal negative feedback. Suggesting this segment delivers reliably high customer experiences.

**Recommendation**
- Invest in Product & Store Quality Controls: Despite having the highest review volume, “Product Variety & Selection” also includes noticeable negative sentiment. Focus on stock availability, layout, and product curation.
- Enhance Mall & Food Court Offerings: The mixed and lower review distribution here suggests potential improvement opportunities in food quality, cleanliness, or seating comfort to boost overall retail experience.

---

## **Future Works**

wip

---

## **Reference**

- [Extract Load Transform Concept](https://www.getdbt.com/blog/extract-load-transform) 
- [Medallion Lakehouse Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion )
- [ETL Cloud Function Tutorial](https://github.com/RekhuGopal/PythonHacks/tree/main/GCP_ETL_CloudFunction_BigQuery) 
- [Bigquery Batch Prediction Job Tutorial](https://cloud.google.com/vertex-ai/docs/samples/aiplatform-create-batch-prediction-job-bigquery-sample#aiplatform_create_batch_prediction_job_bigquery_sample-python )
- [Vertex AI Custom Code Training Tutorial](https://codelabs.developers.google.com/codelabs/vertex-ai-custom-code-training#3)

---

## **Author**

Developed by **Roissyah Fernanda**. This project benefited from the AI chatbots for code refinement, debugging hard problems, and also help with documentation.

Your input is valued! If you spot a bug or want to suggest an improvement, please submit a pull request. Let's collaborate to make this end-to-end Data Analysis project even better