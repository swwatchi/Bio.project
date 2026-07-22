import logging
import time
from datetime import datetime
import schedule

# 기존에 작성한 pipeline.py에서 핵심 함수 가져오기
from pipeline import fetch_clinical_trials, load_to_postgresql

# ==========================================
# 1. 로깅(Logging) 설정
# ==========================================
# 콘솔 출력과 동시에 pipeline.log 파일에 기록이 저장됩니다.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


# ==========================================
# 2. 주기적으로 실행할 작업(Job) 정의
# ==========================================
def run_daily_pipeline():
    logging.info("=" * 50)
    logging.info("🚀 [배치 작업 시작] 임상시험 데이터 수집 및 DB 적재 파이프라인")

    try:
        # 1. API 데이터 수집 (예: 암 관련 최신 데이터 100건)
        trials = fetch_clinical_trials(condition="Cancer", max_results=100)

        if trials:
            # 2. PostgreSQL 적재
            load_to_postgresql(trials)
            logging.info(
                f"✅ [배치 성공] 총 {len(trials)}건의 데이터가 DB에 정상 업데이트되었습니다."
            )
        else:
            logging.warning("⚠️ [배치 경고] 수집된 데이터가 없습니다.")

    except Exception as e:
        logging.error(f"❌ [배치 에러] 파이프라인 실행 중 오류 발생: {e}")

    logging.info("🏁 [배치 작업 완료]")
    logging.info("=" * 50)


# ==========================================
# 3. 스케줄러 등록 및 대기 실행
# ==========================================
if __name__ == "__main__":
    logging.info("⏰ 임상시험 데이터 자동 수집 스케줄러가 시작되었습니다.")

    # [테스트용] 프로그램 켜자마자 최초 1회 즉시 실행
    run_daily_pipeline()

    # [스케줄 설정 방법 예시]
    # 1) 1분마다 실행 (테스트용)
    # schedule.every(1).minutes.do(run_daily_pipeline)

    # 2) 매일 새벽 3시에 실행 (실무 운영용)
    schedule.every().day.at("03:00").do(run_daily_pipeline)

    logging.info(
        "📅 스케줄러 대기 중... (매일 03:00에 자동 실행됩니다. 종료: Ctrl+C)"
    )

    # 무한 루프를 돌며 정해진 시간이 되면 작업 실행
    while True:
        schedule.run_pending()
        time.sleep(1)