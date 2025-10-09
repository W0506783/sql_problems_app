## Solution:

<details>
  <summary>Click to reveal solution</summary>

```SQL 

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

```

</details>



## Deconstruction:

### Core Tasks

1. **Filtering**: We only care about tweets from the year 2022
2. **Counting Tweets Per User**: We need to count how many tweets each user has posted
3. **Creating a Histogram**: We need to group the users by the *number of tweets they posted* and then count the number of users in each of those groups

### This multi-step process, where the result of one aggregation (counting tweets per user) is used in a subsequent aggregation (counting users in each tweet-count group), is a strong indicator that a Common Table Expression (CTE) or a subquery would be beneficial for clarity and organization. Using a CTE makes the logic easier to read and follow.

### This also brings us back to the pattern: we're Summarizing a Summary or "Aggregating an Aggregation"

### Now think about order of operations. In this case since we are going to use a CTE we will begin with a `WITH` clause. `WITH` is not in our order of operations because it is just presumed that it comes before the main query and therefore comes first.

### However, we can go to our order of operations WITHIN the CTE

The `WITH` clause, which defines the Common Table Expression (CTE) named `tweets_per_user`, is processed first. 

- Inside the CTE, using OOP (Order of Operations) we think of the `FROM` clause which identifies the `tweets` table.
- The `WHERE` clause filters this table to only include tweets from 2022.
- The `GROUP BY` clause then groups the remaining rows by `user_id`.
- The `SELECT` statement within the CTE, with the `COUNT` function, calculates the number of tweets for each user.

<details>
  <summary>Click to reveal SQL</summary>

```SQL
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

```
</details>

At the end of this CTE, we have a temporary table (tweets_per_user) that looks something like this:

|user_id|tweet_count|
|:---|:---|
|111|2|
|148|1|
|254|1|

The main query then executes, using the temporary `tweets_per_user` result set as its source table.

- The `FROM` clause in the outer query references `tweets_per_user`.
- The `GROUP BY` clause groups the results from the CTE by the `tweet_count`.
- The `SELECT` statement then counts the number of users (`user_id`) within each of these groups.
- The `ORDER BY` clause sorts the final result set.

<details>
  <summary>Click to reveal SQL</summary>

```SQL

SELECT
  tweet_count AS tweet_bucket,
  COUNT(user_id) AS users_num
FROM
  tweets_per_user
GROUP BY
  tweet_count
ORDER BY
  tweet_bucket;

```
</details>