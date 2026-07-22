CREATE OR REPLACE VIEW view_phase3_trials AS
SELECT 
    nct_id,
    title,
    status,
    conditions,
    interventions,
    enrollment,
    start_date,
    summary
FROM clinical_trials
WHERE phase IN ('PHASE3', 'PHASE2/PHASE3')
  AND status = 'RECRUITING'
ORDER BY enrollment DESC;

-- 뷰 조회 테스트
SELECT * FROM view_phase3_trials;