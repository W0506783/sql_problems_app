-- This file populates our tables with sample data

\c practice;
INSERT INTO "01_tweets" (user_id, msg, tweet_date) VALUES
(111, 'Despite the constant negative press covfefe', '2022-01-01 11:00:00'),
(111, 'Following @NickSinghTech on Twitter changed my life!', '2022-02-14 11:00:00'),
(148, 'I no longer have a manager. I cannot be managed','2022-03-23 11:00:00'),
(254, 'If the salary is so competitive why won’t you tell me what it is?','2022-03-01 11:00:00'),
(111, 'Am considering taking Tesla private at $420. Funding secured.', '2021-12-30 00:00:00');