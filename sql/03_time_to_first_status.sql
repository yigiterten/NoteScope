-- 03 Hours from note creation to its first status other than "Needs More Ratings".
-- Only notes that have left NMR, same comparison window as query 02.
SELECT author_group,
       first_non_nmr_status,
       COUNT(*) AS notes,
       ROUND(median(hours_to_first_status), 1) AS median_hours,
       ROUND(quantile_cont(hours_to_first_status, 0.9), 1) AS p90_hours
FROM note_facts
WHERE first_non_nmr_status IS NOT NULL
  AND hours_to_first_status >= 0
  AND created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
GROUP BY author_group, first_non_nmr_status
ORDER BY author_group, first_non_nmr_status;
