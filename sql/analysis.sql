

SELECT
    userId,
    name,
    MAX(LENGTH(body)) AS longest_post_length
FROM sps_posts
GROUP BY userId, name
ORDER BY longest_post_length DESC, userId ASC
LIMIT 5;


-- QUERY 2:
-- Calculate the average post length (title + body)
-- for each of the top 5 users identified in Query 1.

WITH top_five_users AS (
    SELECT
        userId,
        name,
        MAX(LENGTH(body)) AS longest_post_length
    FROM sps_posts
    GROUP BY userId, name
    ORDER BY longest_post_length DESC, userId ASC
    LIMIT 5
)
SELECT
    p.userId,
    p.name,
    ROUND(
        AVG(LENGTH(p.title) + LENGTH(p.body)),
        2
    ) AS average_post_length
FROM sps_posts p
INNER JOIN top_five_users t
    ON p.userId = t.userId
GROUP BY p.userId, p.name
ORDER BY average_post_length DESC;


-- QUERY 3:
-- Find the weekday with the highest number of lengthy posts.
-- Post ID is used as the day offset from UNIX epoch.
-- UNIX epoch starts on 1970-01-01.

SELECT
    CASE strftime(
        '%w',
        date('1970-01-01', '+' || id || ' days')
    )
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS weekday,
    COUNT(*) AS lengthy_post_count
FROM sps_posts
WHERE status = 'lengthy'
GROUP BY weekday
ORDER BY lengthy_post_count DESC
LIMIT 1;

