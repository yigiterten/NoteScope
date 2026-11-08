-- 07 Quality checks for the ratings summary.
SELECT 'notes with ratings' AS metric, COUNT(*) AS value FROM note_ratings
UNION ALL
SELECT 'ratings in total', SUM(n_ratings)::BIGINT FROM note_ratings
UNION ALL
SELECT 'rated notes missing in note_status', COUNT(*)
FROM note_ratings r LEFT JOIN note_status s ON s.note_id = r.note_id WHERE s.note_id IS NULL
UNION ALL
SELECT 'notes where ratings far exceed approx raters (possible repeat ratings)', COUNT(*)
FROM note_ratings WHERE n_ratings > 1.1 * n_raters_approx + 5
UNION ALL
SELECT 'ratings before note creation', COUNT(*)
FROM note_ratings r JOIN note_status s ON s.note_id = r.note_id WHERE r.first_rating_ms < s.created_ms;
