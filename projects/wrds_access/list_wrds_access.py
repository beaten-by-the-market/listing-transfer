"""WRDS 계정에 권한 있는 라이브러리(DB) 목록을 조회·분류해서 출력한다.

사용법:
    python list_wrds_access.py

리포지토리 루트의 .env(WRDS_USERNAME / WRDS_PASSWORD)로 프롬프트 없이 접속한다.
list_libraries()가 돌려주는 "접근 가능한 스키마"를 샘플/트라이얼과 실제 구독으로
나누고, 각 스키마의 테이블 수를 함께 보여준다.
"""

import os
import re

import wrds
from dotenv import find_dotenv, load_dotenv

# 샘플/트라이얼로 판단되는 스키마 이름 패턴 (모든 WRDS 회원이 공통으로 봄)
SAMPLE_PAT = re.compile(r"(samp|smp|sample|trial)$|samp_|smp_|sample_|_trial")


def connect() -> wrds.Connection:
    """상위 디렉터리를 거슬러 올라가며 찾은 .env로 프롬프트 없이 접속한다."""
    load_dotenv(find_dotenv())  # 어느 폴더에서 실행해도 루트 .env를 찾는다
    username = os.getenv("WRDS_USERNAME")
    password = os.getenv("WRDS_PASSWORD")
    if not username or not password:
        raise SystemExit(
            ".env에 WRDS_USERNAME / WRDS_PASSWORD를 설정하세요. (.env.example 참고)"
        )
    return wrds.Connection(wrds_username=username, wrds_password=password)


def main() -> None:
    db = connect()
    try:
        libs = sorted(db.list_libraries())
        counts = _table_counts(db)
    finally:
        db.close()

    subscribed = [l for l in libs if not SAMPLE_PAT.search(l)]
    samples = [l for l in libs if SAMPLE_PAT.search(l)]

    print(f"전체 접근 가능 스키마: {len(libs)}개 "
          f"(구독 {len(subscribed)} / 샘플·트라이얼 {len(samples)})\n")

    print("== 구독(전체 접근으로 보이는) 라이브러리 ==")
    for lib in subscribed:
        print(f"  {lib:32s} tables={counts.get(lib, 0)}")

    print("\n== 샘플·트라이얼 라이브러리 (제한된 표본) ==")
    for lib in samples:
        print(f"  {lib:32s} tables={counts.get(lib, 0)}")


def _table_counts(db) -> dict:
    rows = db.raw_sql(
        """
        SELECT table_schema, COUNT(*) AS n
        FROM information_schema.tables
        GROUP BY table_schema
        """
    )
    return dict(zip(rows["table_schema"], rows["n"].astype(int)))


if __name__ == "__main__":
    main()
