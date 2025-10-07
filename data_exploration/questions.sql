-- (1) Number of businesses id in each category
SELECT 
COUNT(DISTINCT business_id) AS num_businesses,
general_category
FROM `lithe-camp-465507-v0.yelp_golden.reviews_for_batch_prediction_rnf`
GROUP BY general_category
ORDER BY num_businesses DESC



-- (2) Most popular business categories (by number of reviews)
SELECT 
COUNT(DISTINCT review_id) AS num_reviews,
general_category
FROM `lithe-camp-465507-v0.yelp_golden.reviews_for_batch_prediction_rnf`
GROUP BY general_category
ORDER BY num_reviews DESC



-- (3) % of 5-star reviews for each business category
SELECT 
COUNTIF(star_review = 5)/COUNT(*) AS num_5_star_reviews,
general_category
FROM `lithe-camp-465507-v0.yelp_golden.reviews_for_batch_prediction_rnf`
GROUP BY general_category
ORDER BY num_5_star_reviews DESC;



-- (4) Avg rating of business category with ≥100 reviews
SELECT 
AVG(star_business) AS avg_star_businesss,
general_category,
COUNT(DISTINCT review_id) AS num_reviews
FROM `lithe-camp-465507-v0.yelp_golden.reviews_for_batch_prediction_rnf`
GROUP BY general_category
HAVING num_reviews >= 100
ORDER BY avg_star_businesss DESC;



-- (5) Top 3 most-reviewed businesses id in each state 
WITH
  BusinessReviewCounts AS (
  -- Calculate the number of reviews for each business in eah state
  SELECT
    business_id,
    state,
    general_category,
    COUNT(DISTINCT review_id) AS num_reviews,
  FROM `lithe-camp-465507-v0.yelp_golden.reviews_for_batch_prediction_rnf`
  GROUP BY
    state,
    business_id,
    general_category
),
  RankedBusiness AS (
  -- Apply window function to rank businesses by num_reviews within each state
  SELECT
    state,
    business_id,
    general_category,
    num_reviews,
    -- Partition the data by state, start ranking over for each new state, order by the calculated review count in DESC order
    ROW_NUMBER() OVER (PARTITION BY state ORDER BY num_reviews DESC) AS rank_num
  FROM
    BusinessReviewCounts
)

-- Filter the results to only include the top 3
SELECT
  state,
  rank_num,
  business_id,
  general_category,
  num_reviews
FROM
  RankedBusiness
WHERE
  rank_num <= 3
ORDER BY
  state ASC,
  rank_num ASC;



