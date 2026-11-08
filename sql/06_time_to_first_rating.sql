-- 06 Hours from note creation to its first rating, by author group.
-- Only notes that received at least one rating, same comparison window as query 02.
SELECT f.author_group,
       COUNT(*) AS notes,
       ROUND(median((r.first_rating_ms - f.created_ms) / 3600000.0), 2) AS median_hours,
       ROUND(quantile_cont((r.first_rating_ms - f.created_ms) / 3600000.0, 0.9), 2) AS p90_hours
FROM note_facts f
JOIN note_ratings r ON r.note_id = f.note_id
WHERE f.created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
  AND r.first_rating_ms >= f.created_ms
GROUP BY f.author_group
ORDER BY f.author_group;
