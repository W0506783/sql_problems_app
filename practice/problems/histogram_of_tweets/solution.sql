WITH tweets_per_user AS (
  SELECT 
    user_id, 
    COUNT(tweet_id) AS tweet_count
  FROM 
    tweets
  WHERE 
    EXTRACT(YEAR FROM tweet_date) = 2022
  GROUP BY 
    user_id
)

SELECT
  tweet_count AS tweet_bucket,
  COUNT(user_id) AS users_num
FROM
  tweets_per_user
GROUP BY
  tweet_count
ORDER BY
  tweet_bucket;