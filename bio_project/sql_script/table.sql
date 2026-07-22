-- 기존 테이블이 있다면 삭제 (초기화용)
DROP TABLE IF EXISTS clinical_trials;

-- 임상시험 원천 데이터 테이블 생성
CREATE TABLE clinical_trials (
    nct_id          VARCHAR(20) PRIMARY KEY,      -- 임상시험 고유 ID (예: NCT04561234)
    title           TEXT NOT NULL,               -- 연구 제목
    status          VARCHAR(50),                 -- 진행 상태 (RECRUITING, COMPLETED 등)
    conditions      TEXT,                        -- 대상 질환/조건 (예: Diabetes Mellitus)
    interventions   TEXT,                        -- 치료법/약물명 (예: Metformin)
    phase           VARCHAR(20),                 -- 임상 단계 (PHASE1, PHASE2, PHASE3 등)
    enrollment      INTEGER,                     -- 참여 대상자 수
    start_date      DATE,                        -- 시작일
    completion_date DATE,                        -- 종료(예정)일
    summary         TEXT,                        -- 연구 요약 (향후 RAG 텍스트 벡터화 대상)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 데이터 적재 일시
);

-- 자주 검색되는 컬럼에 인덱스(Index) 생성 (조회 성능 최적화)
CREATE INDEX idx_trials_status ON clinical_trials(status);
CREATE INDEX idx_trials_phase ON clinical_trials(phase);

SELECT nct_id, title, status, phase, conditions 
FROM clinical_trials;

-- 1. pgvector 익스텐션 활성화
--CREATE EXTENSION IF NOT EXISTS vector;

-- 2. clinical_trials 테이블에 384차원 임베딩 벡터 컬럼 추가
-- (sentence-transformers/all-MiniLM-L6-v2 모델 기준)
--ALTER TABLE clinical_trials 
--ADD COLUMN IF NOT EXISTS summary_vector vector(384);

-- 3. 벡터 유사도 검색(Cosine Distance) 전용 HNSW 인덱스 생성
--CREATE INDEX IF NOT EXISTS idx_summary_vector 
--ON clinical_trials 
--USING hnsw (summary_vector vector_cosine_ops);