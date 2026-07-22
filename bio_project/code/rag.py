import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# ==========================================
# 1. DB 접속 설정 (인코딩 에러 완벽 방지)
# ==========================================
DB_USER = "postgres"
DB_PASSWORD = "1234" # ⚠️ 실제 비밀번호 입력
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

encoded_password = quote_plus(DB_PASSWORD)

# client_encoding=utf8 옵션을 URL 파라미터로 명시
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

# SQLAlchemy Engine 생성 (isolation_level 추가)
engine = create_engine(
    DATABASE_URL,
    execution_options={"isolation_level": "AUTOCOMMIT"}
)


# ==========================================
# 2. 임베딩 모델 로드 (384차원 무료 오픈소스)
# ==========================================
print("🔄 임베딩 모델 로딩 중...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# ==========================================
# 3. PostgreSQL 데이터 기반 Vector DB(FAISS) 생성
# ==========================================
def build_vector_store():
    print("🔍 PostgreSQL에서 임상시험 요약문(summary) 데이터 읽어오는 중...")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT nct_id, title, phase, status, conditions, summary 
            FROM clinical_trials 
            WHERE summary IS NOT NULL AND summary != '';
        """))
        rows = result.fetchall()

    if not rows:
        print("⚠️ Vector DB를 생성할 임상 데이터가 DB에 없습니다.")
        return None

    print(f"⚡ 총 {len(rows)}건의 텍스트 데이터를 Vector DB(FAISS)에 적재 중...")
    
    documents = []
    for row in rows:
        doc = Document(
            page_content=row.summary, # 벡터화 대상 (요약문)
            metadata={
                "nct_id": row.nct_id,
                "title": row.title,
                "phase": row.phase,
                "status": row.status,
                "conditions": row.conditions
            }
        )
        documents.append(doc)

    # FAISS 벡터 스토어 생성
    vector_store = FAISS.from_documents(documents, embeddings)
    print("🚀 Vector DB 구축 완료!")
    return vector_store


# ==========================================
# 4. RAG 유사도 검색 (Similarity Search)
# ==========================================
def search_clinical_trials(vector_store, user_query: str, top_k: int = 3):
    print(f"\n🔎 [질문]: '{user_query}' 관련 임상 연구 검색 중...")
    
    # 코사인/L2 거리를 기반으로 질문과 가장 유사한 상위 K개 문서 추출
    results_with_scores = vector_store.similarity_search_with_score(user_query, k=top_k)
    
    print(f"\n🎯 [검색 결과 Top {len(results_with_scores)}]")
    print("=" * 60)
    for i, (doc, score) in enumerate(results_with_scores, 1):
        meta = doc.metadata
        print(f"{i}. [{meta['nct_id']}] {meta['title']}")
        print(f"   - 거리 점수(Distance): {score:.4f} (낮을수록 밀접함)")
        print(f"   - 임상 단계/상태: {meta['phase']} | {meta['status']}")
        print(f"   - 대상 질환: {meta['conditions']}")
        print(f"   - 요약: {doc.page_content[:100]}...\n")


# ==========================================
# 5. 실행 테스트
# ==========================================
if __name__ == "__main__":
    # 1. DB 데이터를 바탕으로 Vector DB 생성
    vector_db = build_vector_store()
    
    # 2. 자연어 유사도 검색 실행
    if vector_db:
        search_clinical_trials(vector_db, "cancer target therapy trials", top_k=3)