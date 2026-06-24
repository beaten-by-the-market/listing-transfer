"""뉴스·transcript 관련 WRDS 라이브러리의 '카탈로그 가시성'과 '실제 SELECT 권한'을 검증한다.

사용법:
    python check_news_transcript.py

리포지토리 루트의 .env(WRDS_USERNAME / WRDS_PASSWORD)로 프롬프트 없이 접속한다.
WRDS는 list_libraries()에 이름이 보여도 실제 조회 시 권한이 거부되는 경우가 많으므로
(예: ciq_transcripts, reprisk, ravenpack_full), 대표 테이블 1행 SELECT로 직접 확인한다.
재현 결과 정리: WRDS_뉴스_Transcript.md
"""

import os
import re
import sys

import wrds
from dotenv import find_dotenv, load_dotenv

# 이름만으로 뉴스/transcript/텍스트 후보로 보이는 라이브러리 패턴
NAME_PAT = re.compile(
    r"(?i)transcript|raven|reprisk|lexis|metabase|pitchbk|revelio|nlpsa|"
    r"computext|news|sentiment|djones"
)

# (스키마, 대표 테이블) — None이면 list_tables 첫 테이블로 시도
PERMISSION_TESTS = [
    ("ciq_transcripts", "ciqtranscript"),          # S&P Capital IQ Events Transcripts
    ("ciq", "ciqtranscript"),                       # 동일 본문(물리 스키마=ciq_transcripts)
    ("ciqsamp_transcripts", "wrds_transcript_detail"),  # 샘플
    ("lexisnexis_metabase", "article_vw"),          # LexisNexis Metabase 뉴스 기사
    ("reprisk", "std_news_data"),                   # RepRisk ESG 뉴스/인시던트
    ("reprisk_sample", "pm_news_data"),             # 샘플
    ("ravenpack_full", "rp_equities"),              # RavenPack 뉴스 분석
    ("ravenpack_dj", "dj_equities"),
    ("ravenpack_trial", "rpa_full_equities"),       # 트라이얼
    ("compsamp_computext", "computext_us"),         # Compustat ComputexT 텍스트(샘플)
    ("pitchbk", "companynewsrelation"),             # PitchBook 뉴스 릴레이션
    ("revelio", "sentiment_scores"),                # Revelio 직원 리뷰 감성(금융뉴스 아님)
    ("djones", "djdaily"),                          # 다우 '지수' — 뉴스 아님(대조용)
]


def connect() -> wrds.Connection:
    load_dotenv(find_dotenv())
    username = os.getenv("WRDS_USERNAME")
    password = os.getenv("WRDS_PASSWORD")
    if not username or not password:
        raise SystemExit(".env에 WRDS_USERNAME / WRDS_PASSWORD를 설정하세요.")
    return wrds.Connection(wrds_username=username, wrds_password=password)


def out(line: str = "") -> None:
    """Windows 콘솔 인코딩과 무관하게 UTF-8로 출력."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8"))


def main() -> None:
    db = connect()
    try:
        libs = set(db.list_libraries())

        out("== list_libraries()에 보이는 뉴스/transcript 관련 라이브러리 ==")
        for lib in sorted(l for l in libs if NAME_PAT.search(l)):
            out(f"   {lib}")

        out("\n== 실제 SELECT 권한 (LIMIT 1) ==")
        for lib, tbl in PERMISSION_TESTS:
            visible = lib in libs
            try:
                db.raw_sql(f"SELECT * FROM {lib}.{tbl} LIMIT 1")
                out(f"   OK   {lib}.{tbl}  (visible={visible})")
            except Exception as exc:  # noqa: BLE001 — 권한/존재 여부를 그대로 보고
                msg = str(exc).splitlines()[0][:110]
                out(f"   DENY {lib}.{tbl}  (visible={visible})  -> {msg}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
