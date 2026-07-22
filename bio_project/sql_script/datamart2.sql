CREATE OR REPLACE VIEW view_trial_summary_stats AS
SELECT 
    phase,
    status,
    COUNT(*) AS total_trials,
    SUM(enrollment) AS total_patients,
    ROUND(AVG(enrollment), 0) AS avg_patients_per_trial
FROM clinical_trials
GROUP BY phase, status
ORDER BY phase, total_trials DESC;

-- 뷰 조회 테스트
SELECT * FROM view_trial_summary_stats;