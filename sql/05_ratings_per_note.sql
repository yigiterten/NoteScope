-- 05 How many ratings does a note receive? By author group (comparison window as in query 02).
-- Notes without any rating count as 0 ratings.
SELECT f.author_group,
       COUNT(*) AS notes,
       ROUND(100.0 * AVG((r.note_id IS NOT NULL)::INTEGER), 1) AS pct_with_any_rating,
       median(COALESCE(r.n_ratings, 0)) AS median_ratings,
       median(COALESCE(r.n_raters_approx, 0)) AS median_raters,
       quantile_cont(COALESCE(r.n_ratings, 0), 0.9) AS p90_ratings,
       ROUND(100.0 * AVG((COALESCE(r.n_ratings, 0) >= 5)::INTEGER), 1) AS pct_5_plus,
       ROUND(100.0 * AVG((COALESCE(r.n_ratings, 0) >= 10)::INTEGER), 1) AS pct_10_plus,
       ROUND(100.0 * AVG((COALESCE(r.n_ratings, 0) > 1.1 * COALESCE(r.n_raters_approx, 0) + 5)::INTEGER), 1) AS pct_repeat_suspect
FROM note_facts f
LEFT JOIN note_ratings r ON r.note_id = f.note_id
WHERE f.created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
GROUP BY f.author_group
ORDER BY f.author_group;

-- 05b Same, split by the note's current status.
SELECT f.author_group,
       f.current_status,
       COUNT(*) AS notes,
       median(COALESCE(r.n_ratings, 0)) AS median_ratings,
       ROUND(100.0 * AVG((COALESCE(r.n_ratings, 0) >= 5)::INTEGER), 1) AS pct_5_plus
FROM note_facts f
LEFT JOIN note_ratings r ON r.note_id = f.note_id
WHERE f.created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
GROUP BY f.author_group, f.current_status
ORDER BY f.author_group, f.current_status;

-- 05c Median ratings per note by creation month and author group.
-- Comparing notes of the same age avoids the bias that newer notes had less time to collect ratings.
SELECT date_trunc('month', f.created_at) AS month,
       f.author_group,
       COUNT(*) AS notes,
       median(COALESCE(r.n_ratings, 0)) AS median_ratings,
       ROUND(100.0 * AVG((COALESCE(r.n_ratings, 0) >= 10)::INTEGER), 1) AS pct_10_plus
FROM note_facts f
LEFT JOIN note_ratings r ON r.note_id = f.note_id
WHERE f.created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
GROUP BY month, f.author_group
ORDER BY month, f.author_group;
