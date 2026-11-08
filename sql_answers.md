\# SQL Analysis Answers



\## Database

SQLite – `sps\_blog.db`



\## Question 1: Find the top 5 users who post the longest posts (excluding the title).



\### SQL Query



```sql

SELECT

&#x20;   userId,

&#x20;   name,

&#x20;   MAX(LENGTH(body)) AS longest\_post\_length

FROM sps\_posts

GROUP BY userId, name

ORDER BY longest\_post\_length DESC, userId ASC

LIMIT 5;

```



\### Result



| User ID | Name | Longest Post Length |

|---|---|---:|

| 2 | Ervin Howell | 225 |

| 7 | Kurtis Weissnat | 218 |

| 10 | Clementina DuBuque | 215 |

| 4 | Patricia Lebsack | 212 |

| 1 | Leanne Graham | 206 |



\## Question 2: For each of these top 5 users, calculate their average post length (including the title).



\### SQL Query



```sql

WITH top\_five\_users AS (

&#x20;   SELECT

&#x20;       userId,

&#x20;       name,

&#x20;       MAX(LENGTH(body)) AS longest\_post\_length

&#x20;   FROM sps\_posts

&#x20;   GROUP BY userId, name

&#x20;   ORDER BY longest\_post\_length DESC, userId ASC

&#x20;   LIMIT 5

)

SELECT

&#x20;   p.userId,

&#x20;   p.name,

&#x20;   ROUND(

&#x20;       AVG(LENGTH(p.title) + LENGTH(p.body)),

&#x20;       2

&#x20;   ) AS average\_post\_length

FROM sps\_posts p

INNER JOIN top\_five\_users t

&#x20;   ON p.userId = t.userId

GROUP BY p.userId, p.name

ORDER BY average\_post\_length DESC;

```



\### Result



| User ID | Name | Average Post Length |

|---|---|---:|

| 4 | Patricia Lebsack | 217.4 |

| 2 | Ervin Howell | 202.9 |

| 7 | Kurtis Weissnat | 200.9 |

| 1 | Leanne Graham | 198.3 |

| 10 | Clementina DuBuque | 190.1 |



\## Question 3: Identify the weekday when the most lengthy posts are created.



Post ID is used as the day offset from the UNIX epoch date, 1970-01-01.



\### SQL Query



```sql

SELECT

&#x20;   CASE strftime(

&#x20;       '%w',

&#x20;       date('1970-01-01', '+' || id || ' days')

&#x20;   )

&#x20;       WHEN '0' THEN 'Sunday'

&#x20;       WHEN '1' THEN 'Monday'

&#x20;       WHEN '2' THEN 'Tuesday'

&#x20;       WHEN '3' THEN 'Wednesday'

&#x20;       WHEN '4' THEN 'Thursday'

&#x20;       WHEN '5' THEN 'Friday'

&#x20;       WHEN '6' THEN 'Saturday'

&#x20;   END AS weekday,

&#x20;   COUNT(\*) AS lengthy\_post\_count

FROM sps\_posts

WHERE status = 'lengthy'

GROUP BY weekday

ORDER BY lengthy\_post\_count DESC

LIMIT 1;

```



\### Result



| Weekday | Lengthy Post Count |

|---|---:|

| Wednesday | 12 |



\## Conclusion



All three SQL analysis queries were executed successfully against the SQLite database. The results identify the top five users by longest individual post, their average combined title and body length, and Wednesday as the weekday with the highest number of lengthy posts.

