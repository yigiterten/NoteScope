-- 04 Data quality checks. Row counts and gaps to keep in mind (and to list under Limitations in the README).
SELECT 'note_status rows' AS metric, COUNT(*) AS value FROM note_status
UNION ALL SELECT 'enrollment rows', COUNT(*) FROM enrollment
UNION ALL SELECT 'notes rows (note files present)', COUNT(*) FROM notes
UNION ALL SELECT 'AI writer accounts (apiEarnedIn)', COUNT(*) FROM enrollment WHERE enrollment_state = 'apiEarnedIn'
UNION ALL SELECT 'note_status rows without a notes row (deleted or file missing)', COUNT(*)
          FROM note_status s WHERE NOT EXISTS (SELECT 1 FROM notes n WHERE n.note_id = s.note_id)
UNION ALL SELECT 'note_status authors missing from enrollment', COUNT(*)
          FROM note_status s WHERE NOT EXISTS (SELECT 1 FROM enrollment e WHERE e.participant_id = s.author_id)
UNION ALL SELECT 'negative hours to first status', COUNT(*) FROM note_facts WHERE hours_to_first_status < 0;
