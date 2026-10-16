-- 01 Overview: notes per author group and current status
SELECT author_group,
       current_status,
       COUNT(*) AS notes,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY author_group), 2) AS pct_of_group
FROM note_facts
GROUP BY author_group, current_status
ORDER BY author_group, current_status;
