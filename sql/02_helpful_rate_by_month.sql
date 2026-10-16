-- 02 Share of notes currently rated Helpful, by creation month and author group.
-- Only months since the first AI note (the two groups are only comparable where both exist).
SELECT date_trunc('month', created_at) AS month,
       author_group,
       COUNT(*) AS notes,
       ROUND(100.0 * AVG(is_helpful_now::INTEGER), 2) AS pct_helpful_now
FROM note_facts
WHERE created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
GROUP BY month, author_group
ORDER BY month, author_group;
