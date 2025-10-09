\c practice;

CREATE TABLE "01_tweets" (
    tweet_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    msg VARCHAR(280),
    tweet_date TIMESTAMP
);