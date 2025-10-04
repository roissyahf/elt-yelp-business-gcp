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
- Vertex AI Workbench
- Power BI (planned Looker Studio, but limited by trial access). 
---

## **Project Structure**

wip

---

## **[Section I] Yelp Review ELT Pipeline**

This project implements a fully automated, event-driven Extract, Load, and Transform (ELT) pipeline on Google Cloud Platform (GCP) to ingest raw Yelp review data from Cloud Storage into a structured BigQuery analytics table.

This pipeline is triggered every time a new JSON file is uploaded to the designated input Cloud Storage bucket. It is designed to handle out-of-order data arrival and prevent duplicate records in the final analytics table.

### **Architecture**

(flowchart is in progress)

Cloud Storage >> Cloud Function 1 (Load) >> BigQuery Staging >> Cloud Function 2 (Transform) >> BigQuery Analytics (Target)

### **Pipeline Components**

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
| **Behavior** | Uses `WRITE_APPEND` to load all data into the staging table. It successfully loads only the triggering file, despite previous test complexities. |
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
| **Action** | Executes a BigQuery **`MERGE ... USING`** query. |
| **Deduplication Logic** | Uses the **Unique Key Check** (`WHEN  NOT MATCHED THEN`) to ensure records are only inserted once. |

### 5. BigQuery Analytics Table: `yelp_analytics.reviews` (The Target)

| Feature | Detail |
| :--- | :--- |
| **Data Integrity** | Contains only unique `review_id` records. |
| **Structure** | **Partitioned** by `date` (truncated to `YEAR`) and **Clustered** by `business_id` for query optimization. |
| **Readiness** | Ready for consumption by downstream tasks. |

### **Data Schema**

(data schema file is in progress)

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

**Key Insights (Sample Demo)**
- Product Variety & Selection dominates in review volume and is largely positive.
- Clothing & Apparel Experience shows mixed ratings, with a notable skew toward 1-star reviews.

---

## **Future Works**

wip

---

## **Reference**

wip

---

## **Author**

Developed by **Roissyah Fernanda**. This project benefited from the AI chatbots for code refinement, debugging hard problems & help with documentation.

Your input is valued! If you spot a bug or want to suggest an improvement, please submit a pull request. Let's collaborate to make this end-to-end Data Analysis project even better