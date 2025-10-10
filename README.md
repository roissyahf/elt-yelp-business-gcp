# **End-to-end Data Analysis Yelp Business Review Project**

This project is **inspired by** end-to-end analytics case studies built by [Ankit Bansal’s (Snowflake + AWS walkthrough)](https://youtu.be/oXLxbk5USFg?si=deFq-iMz8bOqDE9z) using the [Yelp Open Dataset](https://business.yelp.com/data/resources/open-dataset/) but reimagined entirely on Google Cloud Platform (GCP). **The objective** is to: _Design and implement a simple yet extensible ELT pipeline that ingests raw review data into Cloud Storage and maps it into BigQuery. From there, I can do downstream tasks such as sentiment analysis, theme extraction (via Vertex AI), and dashboarding._

### **Problem Statement**
- Vast volumes of unstructured customer review text remain dormant, preventing timely business decision-making.
- Businesses struggle to move beyond simple ratings to identify root causes of dissatisfaction (e.g., product vs. service). They lack automated pipelines for proactive customer service and data-driven investment.
- This project demonstrates how raw text reviews can be transformed into business-ready insights through automation, analytics, and visualization.

### **Constraints**
- Analysis was limited to a 600k review subset (for ELT) and a 14k subset (for intensive downstream AI) due to cloud cost and resource limitations.
- ELT automation was focused solely on the Reviews data. Business is handled manually, and User data were excluded.
- Visualization was constrained to Power BI due to Looker Studio trial limitations. Automated data refresh for the Power BI has not yet been configured
- LLM throughput limits (despite parallelization) forced the use of traditional ML methods executed via a Vertex AI Workbench script, rather than the Batch Prediction service.

### **Key Features**
- **Event-Driven ELT Pipeline**: Automated, serverless pipeline on GCP that transforms raw JSON to a clean, partitioned BigQuery Analytics table.
- **Hybrid Downstream Analytics**: POC for data enrichment using both VADER sentiment (fast, lexicon-based) and TF-IDF + KMeans (unsupervised themes).
- **BI Dashboard Reporting**: Developed a Power BI Dashboard with a manual data flow from BigQuery, enabling immediate visualization and access to key customer insights.

---

## **Technology Stack**
- Cloud Functions
- BigQuery
- Cloud Storage
- Vertex AI Workbench
- Power BI 
---
## **Project Development Step**

### **Phase 1: Data Preparation & Validation**
- Executed a manual ELT run using the Google Cloud CLI to validate core transformation logic.
- Mapped over 83k distinct business categories to 10 standard `general_category` labels using fuzzy string matching (`fuzzywuzzy`), and reloaded the mapping into the staging environment.

### **Phase 2: Automation & QA**
- Developed and deployed Python Cloud Functions to create an event-driven ELT pipeline for the reviews data.
- Ran SQL queries to answer five basic questions, verifying the quality of the transformed data.

### **Phase 3: Analysis & Delivery**
- Asked 5 questions to better understand the data in `data_joined` table
- Performed a detailed downstream task focusing on data from a single `general_category`.
- Defined key business questions and sketched the required Power BI dashboard layout.
- Developed the Power BI dashboard, extracted key findings, and formulated actionable recommendations.

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

**Pipeline Components Overview** 

<img width="952" height="321" alt="Image" src="https://github.com/user-attachments/assets/0ff49273-2c90-491a-82af-6b415a3c3d01" />

### **Business Data (One-Time Manual ELT)**
The business data required a one-time manual ELT pipeline due to its unique complexity. The original Yelp business categories, stored in the `categories` field, containing multiple specific entries per business (over 83,000 distinct combinations observed). This granularity made it difficult to define a high-level category necessary for downstream analysis.

To address this, I implemented a specialized data treatment:
1. All distinct categories were extracted and mapped to a set of 10 standardized general category labels using the `fuzzywuzzy` algorithm for flexible string matching.
2. The resulting mapping table was loaded back into the `yelp_landing` dataset as the `business_category_mapping_fw` table.
3. This mapping table was then transformed and loaded into the `yelp_analytics` dataset by performing a `LEFT JOIN` with the `businesses_raw` table. This standardized business data is now ready to be joined with the reviews data in the final gold layer for analysis.

### **Reviews Data (Automated ELT Pipeline)**

The reviews data is handled by a fully automated, event-driven ELT pipeline using Cloud Functions. The pipeline is triggered every time a new JSON file is uploaded to the designated input Cloud Storage bucket. It is designed to handle out-of-order data arrival and prevent duplicate records in the final analytics table. **The detail is as follow**:

### **1. Cloud Storage (GCS)**

| Component | Detail | Purpose |
| :--- | :--- | :--- |
| **Input Bucket** | `yelp-elt-inbound-data` | **Trigger:** New JSON files are uploaded here, triggering the ELT process. |
| **File Format** | Newline-Delimited JSON (NDJSON) | Original Dataset Format. |

### 2. **Cloud Function 1: `load_data` (The Load Step)**

This function handles the Extract and Load phases.

| Feature | Details |
| :--- | :--- |
| **Trigger** | GCS Event (`google.cloud.storage.object.v1.finalized`) on the input bucket. |
| **Action** | Loads the newly uploaded JSON file directly into the staging BigQuery table. |
| **Behavior** | Uses `WRITE_APPEND` to load all data into the staging table. |
| **Next Step** | Securely triggers Cloud Function 2 (`transform_data`) via an authenticated HTTP request upon successful load. |

### **3. BigQuery Staging Table: `yelp_landing.reviews_raw`**

| Feature | Detail |
| :--- | :--- |
| **Purpose** | Temporary storage for raw, unsanitized data. Acts as an audit log. |
| **Data Integrity** | May contain duplicate `review_id` records due to file re-uploads, but this is handled by the next stage. |

### **4. Cloud Function 2: `transform_data` (The Transform Step)**

This function handles the core business logic, transformation, and incremental loading.

| Feature | Details |
| :--- | :--- |
| **Trigger** | HTTP request from Cloud Function 1. |
| **Action** | Executes a BigQuery **`MERGE`** statement for atomic, race-condition-safe operations. |
| **Deduplication Logic** | Uses the **`MERGE ... USING ... ON target.review_id = source.review_id WHEN NOT MATCHED THEN`** to ensure records are only inserted once, even with concurrent executions |

### **5. BigQuery Analytics Table: `yelp_analytics.reviews` (The Target)**

| Feature | Detail |
| :--- | :--- |
| **Data Integrity** | Contains only unique `review_id` records. |
| **Structure** | **Partitioned** by `date` (truncated to `YEAR`) and **Clustered** by `business_id` for query optimization. |
| **Readiness** | Ready for consumption by downstream tasks. |

---

## **Data Schema**

**`yelp_landing`**
<img width="776" height="372" alt="Image" src="https://github.com/user-attachments/assets/3107dd52-c7bf-4010-aede-0218a8071204" />

**`yelp_analytics`**
<img width="776" height="342" alt="Image" src="https://github.com/user-attachments/assets/025004d6-232a-4f5a-bed6-6e3103af81d4" />

**`yelp_golden`**
<img width="862" height="512" alt="Image" src="https://github.com/user-attachments/assets/b4e52b9b-7faa-4753-b98b-ac18525978a8" />

---

## **Data Exploration with SQL**

Before commencing downstream tasks, a preliminary data exploration was conducted using SQL queries to ensure data quality and establish a foundational understanding of the transformed dataset. The five key questions defined below provided essential context for subsequent analysis.

| Question | Business Impact |
| -- | -- |
| Business Count per Category | Market sizing and coverage by category | 
| Popular Categories (by Reviews) | Customer engagement and demand proxy per category | 
|  % of 5-Star Reviews per Business |  Quality signal and competitive benchmarking | 
|  Top 5 Most-Reviewed Businesses by State |  Identifying local popularity and state-level leaders | 
|  Avg. Rating for High-Volume Businesses |  Stable performance view, filtering out noise from low review counts | 

---

## **[Section II] Downstream Task: Sentiment Analysis & Theme Extraction**

After completing the ELT pipeline with Cloud Function and completing Data Exploration with SQL, I proceeded with downstream analytics to enrich the Yelp reviews data. The processed dataset is stored in a new BigQuery dataset: **`yelp_golden`**.

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

> Note: These tasks were executed on **Vertex AI Workbench Notebook** for flexibility. BigQuery ML was considered, but initial experiments with thousands of reviews showed longer runtimes.

### **Dashboard**

> ️ Note: This analysis is based on a sample of ~14,700 reviews from a single business category (Shopping & Retail). The results do not represent the entire Yelp dataset or real-world conditions. The purpose is to demonstrate insights that can be derived after the full pipeline (ELT + downstream processing).

* Built a **Power BI dashboard**
* Dashboard design started with business questions and sketching.
* Final dashboard includes:

  * KPIs: Count of reviews, Avg. Star Review, Avg. Star Business
  * Sentiment distribution by theme
  * Star rating distribution by theme (matrix heatmap)
  * Filters for Sentiment

**Dashboard Snapshot**
<img width="943" height="423" alt="Image" src="https://github.com/user-attachments/assets/b2817195-ab03-4ed7-ac9c-943cdc169f31" />

**Key Findings**
- Product Variety & Selection dominates in review volume and is largely positive.
- Clothing & Apparel Experience shows mixed ratings, with a notable skew toward 1-star reviews.
- Hair & Beauty Services performs well overall, with a strong concentration in 5-star reviews and minimal negative feedback. Suggesting this segment delivers reliably high customer experiences.

**Recommendation**
- Despite having the highest review volume, “Product Variety & Selection” also includes noticeable negative sentiment. Focus on stock availability, layout, and product curation.
- The mixed and lower review distribution here suggests potential improvement opportunities in food quality, cleanliness, or seating comfort to boost overall retail experience.

---

## **Future Works**

### **ELT Pipeline Enhancements**
Enforce strict schema validation (e.g., data types, naming) in the Cloud Function.

### **Downstream AI & Customer Service**
- Add Urgency Tag and LLM-Generated Response for immediate customer service action.
- Deploy analysis to a scheduled Vertex AI Pipeline (Batch Prediction) to auto-process all new and existing data.
- Use embeddings model and clustering for more accurate semantic theme extraction.

### **Visualization & Reporting**
- Use Power BI DirectQuery or scheduled refresh via Gateway for live data updates.
- Implement a scheduled Cloud Run service to generate and send narrative summary reports using Gen AI to the stakeholder.

---

## **Reference**

- [Extract Load Transform Concept](https://www.getdbt.com/blog/extract-load-transform) 
- [Medallion Lakehouse Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion )
- [ETL Cloud Function Tutorial](https://github.com/RekhuGopal/PythonHacks/tree/main/GCP_ETL_CloudFunction_BigQuery) 
- [Bigquery Batch Prediction Job Tutorial](https://cloud.google.com/vertex-ai/docs/samples/aiplatform-create-batch-prediction-job-bigquery-sample#aiplatform_create_batch_prediction_job_bigquery_sample-python )
- [Vertex AI Custom Code Training Tutorial](https://codelabs.developers.google.com/codelabs/vertex-ai-custom-code-training#3)

---

## **Author**

Developed by **Roissyah Fernanda**. Some parts of the implementation and documentation were assisted by AI tools (e.g., for code refactoring, formatting, and technical writing support), while all project ideas, integration, and decision-making were independently developed by the author.

Your input is valued! If you spot a bug or want to suggest an improvement, please submit a pull request. Let's collaborate to make this end-to-end Data Analysis project even better!