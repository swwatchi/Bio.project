import os
import sys

# Windows 환경 인코딩 설정
os.environ["PGCLIENTENCODING"] = "utf-8"

import textwrap  # 긴 텍스트 줄바꿈 처리 라이브러리
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine, text

# ==========================================
# 1. DB 접속 설정
# ==========================================
DB_USER = "postgres"
DB_PASSWORD = "1234"  # ⚠️ 실제 본인의 비밀번호로 수정하세요
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"options": "-c client_encoding=UTF8 -c lc_messages=C"},
    )

    with engine.connect() as conn:
        df_stats = pd.read_sql(
            text("SELECT * FROM view_trial_summary_stats;"), conn
        )
        df_drugs = pd.read_sql(
            text("SELECT * FROM view_top_interventions LIMIT 10;"), conn
        )

except Exception as e:
    print("❌ DB 연결 실패:", e)
    sys.exit(1)

# ==========================================
# 2. 대시보드 시각화 (레이아웃 최적화)
# ==========================================
plt.style.use("seaborn-v0_8-whitegrid")

# 캔버스 크기 확충 및 서브플롯 간격 확보
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle(
    "🧬 NIH Clinical Trials Data Mart Analytics Dashboard",
    fontsize=20,
    fontweight="bold",
    y=0.98,
)

# ------------------------------------------
# 차트 1: 임상 단계별(Phase) 분포 (Pie Chart)
# ------------------------------------------
if not df_stats.empty and "phase" in df_stats.columns:
    phase_counts = (
        df_stats.groupby("phase")["total_trials"].sum().reset_index()
    )
    phase_counts = phase_counts[phase_counts["phase"] != "NA"]

    axes[0].pie(
        phase_counts["total_trials"],
        labels=phase_counts["phase"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("pastel"),
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        pctdistance=0.75,
    )
    axes[0].set_title(
        "Distribution by Clinical Trial Phase", fontsize=14, fontweight="bold"
    )

# ------------------------------------------
# 차트 2: 상위 10개 주요 치료법/약물 빈도 (Horizontal Bar Chart)
# ------------------------------------------
if not df_drugs.empty:
    # 뷰의 실제 컬럼명 가져오기
    cols = list(df_drugs.columns)

    # 약물명/치료법 컬럼과 수치 컬럼 명확히 할당
    name_col = cols[0]  # 첫 번째 컬럼 (약물/치료법 이름)
    count_col = cols[1]  # 두 번째 컬럼 (건수)

    # Y축 텍스트가 너무 길 경우 30자 단위로 줄바꿈 처리
    df_drugs["short_name"] = df_drugs[name_col].apply(
        lambda x: textwrap.fill(str(x), width=30)
    )

    # 수치형 데이터 변환
    df_drugs[count_col] = pd.to_numeric(df_drugs[count_col], errors="coerce")

    # 가로 바 차트 (X: 건수, Y: 약물명)
    barplot = sns.barplot(
        ax=axes[1],
        x=count_col,
        y="short_name",
        data=df_drugs,
        palette="Blues_r",
    )
    axes[1].set_title(
        "Top 10 Frequently Used Interventions / Drugs",
        fontsize=14,
        fontweight="bold",
    )
    axes[1].set_xlabel("Number of Clinical Trials", fontsize=12)
    axes[1].set_ylabel("Intervention Name", fontsize=12)

    # 수치 데이터 레이블 표시
    for p in barplot.patches:
        width = p.get_width()
        if not pd.isna(width) and width > 0:
            axes[1].annotate(
                f"{int(width)}",
                (width + 0.1, p.get_y() + p.get_height() / 2.0),
                ha="left",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="black",
            )

# 여백 자동 조정
plt.tight_layout(rect=[0, 0, 1, 0.95])

# 파일 저장 및 출력
output_filename = "datamart_dashboard.png"
plt.savefig(output_filename, dpi=300, bbox_inches="tight")
print(f"🚀 최적화된 시각화 대시보드가 '{output_filename}'으로 저장되었습니다!")

plt.show()