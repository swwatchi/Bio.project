# Bio.project

NIH ClinicalTrials 데이터 엔지니어링 & AI RAG 검색 파이프라인미국 국립보건원(NIH) 임상시험 API 데이터를 활용한 자동화 ETL, 데이터 마트 구축 및 AI 기반 자연어 검색 시스템

🛠️ 1. 프로젝트 개요 (Overview)본 프로젝트는 미국 NIH(ClinicalTrials.gov)의 Open API 데이터를 바탕으로, 수집(Extract) ➔ 가공(Transform) ➔ 적재(Load) ➔ 데이터 분석 마트(View) ➔ AI RAG 자연어 검색 ➔ 대시보드 시각화까지 완결된 흐름을 갖춘 End-to-End 데이터 파이프라인 구축 프로젝트입니다.개발 기간: 2026.03 ~ 2026.04담당 역할: 데이터 엔지니어링 (개인 100%)주요 목적: 대용량 텍스트/통계 데이터의 자동 수집 및 파이프라인 안정성 확보, AI 모델 연동을 통한 자연어 질의 응답 시스템 구축

💡 2. 핵심 기능 및 과업 내용 (Key Features)구 분과업 내용 및 적용 기술
ETL Pipeline• REST API 연동을 통한 100건+ 임상 연구 데이터 자동 수집• ON CONFLICT (nct_id) DO UPDATE (Upsert) 로직 구현으로 중복 데이터 방지• Windows/PostgreSQL 환경 간 인코딩 충돌(CP949/UTF-8) 완벽 처리

Data Mart• View 1: 주요 3상(Phase 3) 모집 중인 임상 연구 전용 마트• View 2: 임상 단계(Phase) 및 모집 상태(Status)별 요약 통계 마트• View 3: 자주 활용되는 주요 약물/치료법(Interventions) 순위 분석 마트

Automation• Python schedule 패키지를 활용한 주기적 배치(Batch) 수집 스케줄링• pipeline.log 로깅 구축을 통한 시스템 장애 감지 및 수행 이력 관리

AI RAG Search• HuggingFace sentence-transformers 모델 기반 384차원 텍스트 임베딩• FAISS Vector DB 구축으로 자연어 질문에 대한 유사 임상 연구 Top 3 탐색 시스템 구현

Dashboard• matplotlib / seaborn 라이브러리를 활용한 데이터 마트 시각화• 임상 단계별 비율(Pie Chart) 및 주요 약물 빈도(Bar Chart) 통합 대시보드 생성

⚙️ 3. 시스템 아키텍처 (System Architecture)
Plaintext[ NIH REST API ]
       │
       ▼ (Extract & Transform)
[ Python ETL Engine ] ───► [ Batch Scheduler & Log System ]
       │
       ▼ (Load / Upsert)
[ PostgreSQL Database ]
       │
       ├─► [ SQL Data Marts (Views) ] ───► [ Analytics Dashboard ]
       │
       └─► [ LangChain + FAISS Vector DB ] ───► [ AI Natural Language RAG ]

🖥️ 4. 주요 결과물 및 시각화 (Results & Visualization)
① 데이터 마트 분석 대시보드 (datamart_dashboard.png)PostgreSQL 데이터 마트에서 정제된 데이터를 추출하여 임상 단계별 분포와 상위 치료법/약물 빈도를 대시보드로 시각화하였습니다.임상 단계별 분포: PHASE2 (32.5%), PHASE1 (20.5%), PHASE3 (7.2%) 등 초기/중기 임상 비중 파악주요 치료법 분석: 임상시험에서 가장 자주 활용된 약물 및 바이오마커 분석 기법 시각화

② AI RAG 자연어 검색 출력 (rag.py)사용자의 자연어 질문(예: "cancer target therapy trials")을 벡터화하여, FAISS DB에서 가장 관련성이 높은 임상 연구 3건과 코사인 유사도 거리 점수를 도출합니다.

🧰 5. 사용 기술 스택 (Tech Stack)
언어 (Language): Python 3.13
데이터베이스 (DB): PostgreSQL, DBeaver
데이터 엔지니어링 / ETL: SQLAlchemy, psycopg2, pandas, Requests, Schedule
AI / RAG / Vector DB: LangChain, FAISS, HuggingFace (sentence-transformers)
시각화 (Visualization): matplotlib, seaborn
