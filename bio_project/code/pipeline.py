from urllib.parse import quote_plus
import requests
import pandas as pd
from sqlalchemy import create_engine, text

# ==========================================
# 1. 데이터베이스 접속 정보 설정
# ==========================================
DB_USER = "postgres"        # DB 사용자명 (기본값: postgres)
DB_PASSWORD = "1234" # ⚠️ 본인의 실제 PostgreSQL 비밀번호로 변경하세요!
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"        # 또는 DBeaver에서 생성한 데이터베이스 이름

# 비밀번호에 특수문자(@, !, # 등)나 한글이 있을 경우를 대비한 URL 인코딩
encoded_password = quote_plus(DB_PASSWORD)

# PostgreSQL 접속 URL 생성
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Engine 생성 (client_encoding='utf8' 옵션으로 인코딩 에러 방지)
engine = create_engine(
    DATABASE_URL,
    connect_args={'client_encoding': 'utf8'}
)


# ==========================================
# 2. ClinicalTrials API v2 데이터 수집 함수
# ==========================================
def fetch_clinical_trials(condition="Cancer", max_results=10):
    """
    NIH ClinicalTrials API에서 특정 질환(condition) 관련 임상 데이터를 수집하는 함수
    """
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.cond": condition,
        "pageSize": max_results,
        "format": "json"
    }
    
    print(f"🌐 [{condition}] 키워드로 ClinicalTrials.gov API 수집 중...")
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {e}")
        return []

    studies = response.json().get("studies", [])
    parsed_trials = []
    
    for item in studies:
        protocol = item.get("protocolSection", {})
        
        # 1. NCT ID 및 Title
        id_module = protocol.get("identificationModule", {})
        nct_id = id_module.get("nctId")
        title = id_module.get("briefTitle", "No Title")
        
        # 2. Status
        status_module = protocol.get("statusModule", {})
        status = status_module.get("overallStatus", "UNKNOWN")
        
        # 3. Phase & Enrollment
        design_module = protocol.get("designModule", {})
        phases = design_module.get("phases", ["UNKNOWN"])
        phase = phases[0] if phases else "UNKNOWN"
        enrollment = design_module.get("enrollmentInfo", {}).get("count", 0)
        
        # 4. Conditions
        cond_list = protocol.get("conditionsModule", {}).get("conditions", [])
        conditions = ", ".join(cond_list) if cond_list else "None"
        
        # 5. Interventions (약물/치료법)
        arms_module = protocol.get("armsInterventionsModule", {})
        interventions_list = [
            i.get("name", "") for i in arms_module.get("interventions", [])
        ]
        interventions = ", ".join(interventions_list) if interventions_list else "None"
        
        # 6. Summary (요약)
        summary = protocol.get("descriptionModule", {}).get("briefSummary", "")
        
        if nct_id:
            parsed_trials.append({
                "nct_id": nct_id,
                "title": title,
                "status": status,
                "conditions": conditions,
                "interventions": interventions,
                "phase": phase,
                "enrollment": enrollment,
                "summary": summary
            })
            
    print(f"✅ 총 {len(parsed_trials)}건의 임상시험 데이터 수집 및 정제 완료.")
    return parsed_trials


# ==========================================
# 3. PostgreSQL DB 적재 함수 (Upsert 적용)
# ==========================================
def load_to_postgresql(trials_data):
    """
    수집된 데이터를 PostgreSQL clinical_trials 테이블에 적재 (중복 ID 갱신 처리)
    """
    if not trials_data:
        print("⚠️ 적재할 데이터가 없습니다.")
        return

    # ON CONFLICT (nct_id): 이미 존재하는 NCT ID면 데이터를 최신 내용으로 UPDATE
    upsert_query = text("""
        INSERT INTO clinical_trials (
            nct_id, title, status, conditions, interventions, phase, enrollment, summary
        ) VALUES (
            :nct_id, :title, :status, :conditions, :interventions, :phase, :enrollment, :summary
        )
        ON CONFLICT (nct_id) DO UPDATE SET
            title = EXCLUDED.title,
            status = EXCLUDED.status,
            conditions = EXCLUDED.conditions,
            interventions = EXCLUDED.interventions,
            phase = EXCLUDED.phase,
            enrollment = EXCLUDED.enrollment,
            summary = EXCLUDED.summary,
            created_at = CURRENT_TIMESTAMP;
    """)

    try:
        with engine.begin() as connection:
            for trial in trials_data:
                connection.execute(upsert_query, trial)
                
        print(f"🚀 성공: {len(trials_data)}건의 데이터가 PostgreSQL DB에 적재되었습니다!")
        
    except Exception as e:
        print(f"❌ DB 적재 중 오류 발생: {e}")


# ==========================================
# 4. 파이프라인 실행
# ==========================================
if __name__ == "__main__":
    # 1. API 데이터 수집 (예: 암 관련 임상시험 10건)
    data = fetch_clinical_trials(condition="Cancer", max_results=100)
    
    # 2. PostgreSQL DB 적재
    load_to_postgresql(data)