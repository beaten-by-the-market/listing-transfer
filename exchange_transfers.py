"""
NYSE <-> NASDAQ 이전상장(거래소 이동) 내역 추출.

CRSP의 crsp.stocknames에서 PERMNO를 고정하고 거래소 코드(exchcd)가
시간에 따라 바뀌는 지점을 이전상장으로 식별한다.

exchcd: 1=NYSE, 2=NYSE American(AMEX), 3=NASDAQ

출력:
  - transfers_detail.csv : 개별 이전상장 건별 리스트
  - transfers_yearly.csv : 연도 x 방향별 집계
사용:
  python exchange_transfers.py            # NYSE<->NASDAQ만
  python exchange_transfers.py --amex     # AMEX(2) 경유 포함
"""

import argparse
import os

import pandas as pd
import wrds
from dotenv import load_dotenv

EXCH_MAP = {1: "NYSE", 2: "AMEX", 3: "NASDAQ"}


def connect() -> wrds.Connection:
    """.env의 WRDS_USERNAME/WRDS_PASSWORD로 프롬프트 없이 접속한다."""
    load_dotenv()
    username = os.getenv("WRDS_USERNAME")
    password = os.getenv("WRDS_PASSWORD")
    if not username or not password:
        raise SystemExit(
            ".env에 WRDS_USERNAME / WRDS_PASSWORD를 설정하세요. "
            "(.env.example 참고)"
        )
    # username+password를 모두 넘기면 .pgpass 없이 첫 시도에서 바로 연결된다.
    return wrds.Connection(wrds_username=username, wrds_password=password)


def get_transfers(include_amex: bool = False) -> pd.DataFrame:
    exch_codes = (1, 2, 3) if include_amex else (1, 3)

    db = connect()
    try:
        names = db.raw_sql(
            f"""
            SELECT permno, namedt, nameenddt, exchcd, ticker, comnam, ncusip
            FROM crsp.stocknames
            WHERE exchcd IN {exch_codes}
            ORDER BY permno, namedt
            """,
            date_cols=["namedt", "nameenddt"],
        )
    finally:
        db.close()

    # 같은 거래소가 연속된 구간을 하나로 합친다(티커/회사명 변경으로 쪼개진 구간 정리).
    names["block"] = (
        names.groupby("permno")["exchcd"]
        .transform(lambda s: (s != s.shift()).cumsum())
    )
    collapsed = (
        names.groupby(["permno", "block"], as_index=False)
        .agg(
            exchcd=("exchcd", "first"),
            start=("namedt", "min"),
            end=("nameenddt", "max"),
            ticker=("ticker", "last"),
            comnam=("comnam", "last"),
            ncusip=("ncusip", "last"),
        )
        .sort_values(["permno", "start"])
    )

    # 거래소가 바뀌는 지점만 추출.
    collapsed["prev_exch"] = collapsed.groupby("permno")["exchcd"].shift()
    transfers = collapsed[
        collapsed["prev_exch"].notna()
        & (collapsed["exchcd"] != collapsed["prev_exch"])
    ].copy()

    transfers["from"] = transfers["prev_exch"].map(EXCH_MAP)
    transfers["to"] = transfers["exchcd"].map(EXCH_MAP)
    transfers["change_date"] = transfers["start"]
    transfers["year"] = transfers["change_date"].dt.year
    transfers["direction"] = transfers["from"] + " -> " + transfers["to"]

    return transfers[
        ["permno", "comnam", "ticker", "ncusip",
         "change_date", "year", "from", "to", "direction"]
    ].reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--amex", action="store_true", help="AMEX(2) 경유 이동 포함")
    args = parser.parse_args()

    transfers = get_transfers(include_amex=args.amex)

    # 1) 개별 건별 리스트
    transfers.to_csv("transfers_detail.csv", index=False, encoding="utf-8-sig")

    # 2) 연도 x 방향별 집계
    yearly = (
        transfers.groupby(["year", "direction"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    yearly["total"] = yearly.sum(axis=1)
    yearly.to_csv("transfers_yearly.csv", encoding="utf-8-sig")

    print(f"총 이전상장 건수: {len(transfers)}")
    print("\n방향별 합계:")
    print(transfers["direction"].value_counts().to_string())
    print("\n연도별 집계(상위/최근 일부):")
    print(yearly.tail(15).to_string())
    print("\n저장: transfers_detail.csv, transfers_yearly.csv")


if __name__ == "__main__":
    main()
