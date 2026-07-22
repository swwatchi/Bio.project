CREATE OR REPLACE VIEW view_top_interventions AS
SELECT 
    interventions,
    COUNT(*) AS study_count,
    STRING_AGG(nct_id, ', ') AS related_nct_ids
FROM clinical_trials
WHERE interventions != 'None'
GROUP BY interventions
HAVING COUNT(*) >= 1
ORDER BY study_count DESC;

-- 뷰 조회 테스트
SELECT * FROM view_top_interventions;