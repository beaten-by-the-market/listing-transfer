"""글로벌 상장 '회사' 마스터 (id_identify) — FactSet 단독 v1.

2011년 이후 NYSE·Nasdaq·JPX(도쿄)·KRX·TWSE에 (보통주 기준) 상장 상태였던
회사(법인)를 거래소별 레코드로 추출하고, 회사 기준 공통식별자
(ISIN=메인 보통주 / CUSIP / 티커 / LEI)와 상장·상폐 일자를 붙인다.

스코프(확정): 보통주(SHARE)만 · 본국 보통주 상장만(ADR 제외) · FactSet 단독(구간/연도)
· 2011-01-01 이후 한 번이라도 상장 상태였던 회사(이전 상장+이후 상폐 포함).

사용법:
    python build_master.py            # KOSPI/KOSDAQ(XKRX)만
    python build_master.py --konex    # KRX KONEX(XKON) 포함
출력: company_master.csv, summary는 stdout.
"""

import argparse
import os

import pandas as pd
import wrds
from dotenv import load_dotenv

# 루트 .env (이 파일은 projects/id_identify/factset/ 에 위치)
ROOT_ENV = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")

# FactSet listing exchange code → (MIC, 표기)
EXCHANGES = {
    "NYS": ("XNYS", "NYSE"),
    "NAS": ("XNAS", "Nasdaq"),
    "TKS": ("XTKS", "JPX(TSE)"),
    "KRX": ("XKRX", "KRX"),
    "TAI": ("XTAI", "TWSE"),
}
KONEX = {"KON": ("XKON", "KRX-KONEX")}

CUTOFF = "2011-01-01"


def isin_check_digit(body: str) -> str:
    """ISIN 체크디지트(Luhn). body = 국가2자 + NSIN9자 (11자)."""
    conv = "".join(str(ord(c) - 55) if c.isalpha() else c for c in body)
    total, dbl = 0, True
    for d in (int(x) for x in reversed(conv)):
        if dbl:
            d *= 2
            total += d - 9 if d > 9 else d
        else:
            total += d
        dbl = not dbl
    return str((10 - total % 10) % 10)


def derive_isin_from_cusip(cusip: str, country: str) -> str | None:
    """미국/캐나다 CUSIP → ISIN 파생 (FactSet은 US ISIN 미저장)."""
    _ok = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if (not isinstance(cusip, str) or len(cusip) != 9 or not set(cusip) <= _ok
            or not isinstance(country, str) or country not in ("US", "CA")):
        return None
    body = country + cusip
    return body + isin_check_digit(body)


def connect() -> wrds.Connection:
    load_dotenv(ROOT_ENV)
    u, p = os.getenv("WRDS_USERNAME"), os.getenv("WRDS_PASSWORD")
    if not u or not p:
        raise SystemExit("루트 .env에 WRDS_USERNAME / WRDS_PASSWORD 필요")
    return wrds.Connection(wrds_username=u, wrds_password=p)


def build_query(ex_codes: list[str]) -> str:
    codes = ",".join(f"'{c}'" for c in ex_codes)
    # grain = regional(-R) 레벨: 지역(국가)당 1행, 그 지역의 '대표 거래소'를 가짐.
    #   → 미국 종목이 NYSE/Nasdaq 중 진짜 주거래소로 분기, 호가-거래소 중복 제거.
    #   → 본국 보통주만(SHARE) 잡히고 ADR(다른 security)은 제외됨.
    # 식별자는 security(-S) 기준 scalar 서브쿼리로 1건씩 → 행 폭증 방지.
    return f"""
    WITH reg AS (
        SELECT c.fsym_id            AS reg_id,
               c.fsym_security_id   AS sec_id,
               c.proper_name,
               c.active_flag,
               c.fref_listing_exchange AS ex_code
        FROM factset.sym_coverage c
        WHERE c.regional_flag = '1'
          AND c.fref_security_type = 'SHARE'
          AND c.fref_listing_exchange IN ({codes})
    ),
    dates AS (
        SELECT fsym_id,
               MIN(start_date) AS listing_start,
               MAX(end_date)   AS listing_end
        FROM factset.sym_ticker_region_hist
        WHERE fsym_id IN (SELECT reg_id FROM reg)
        GROUP BY fsym_id
    )
    SELECT r.ex_code,
           se.factset_entity_id,
           ent.entity_proper_name              AS company_name,
           ent.iso_country                     AS company_country,
           ent.entity_type,
           r.proper_name                       AS security_name,
           r.active_flag,
           d.listing_start,
           d.listing_end,
           (SELECT xi.isin FROM factset.sym_xc_isin xi
              WHERE xi.fsym_id = r.sec_id ORDER BY xi.isin LIMIT 1)         AS main_isin,
           (SELECT cu.cusip FROM factset.sym_cusip cu
              WHERE cu.fsym_id = r.sec_id ORDER BY cu.cusip LIMIT 1)        AS main_cusip,
           (SELECT tr.ticker_region FROM factset.sym_ticker_region tr
              WHERE tr.fsym_id = r.reg_id LIMIT 1)                          AS main_ticker,
           (SELECT e.entity_id_value FROM factset_common.edm_standard_entity_identifiers e
              WHERE e.factset_entity_id = se.factset_entity_id
                AND e.entity_id_type = 'LEI' LIMIT 1)                       AS lei
    FROM reg r
    LEFT JOIN factset.sym_sec_entity se ON se.fsym_id = r.sec_id
    LEFT JOIN factset.sym_entity ent    ON ent.factset_entity_id = se.factset_entity_id
    LEFT JOIN dates d                   ON d.fsym_id = r.reg_id
    WHERE r.active_flag = '1'
       OR d.listing_end >= DATE '{CUTOFF}'
       OR d.listing_end IS NULL
    """


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--konex", action="store_true", help="KRX KONEX 포함")
    args = ap.parse_args()

    ex = dict(EXCHANGES)
    if args.konex:
        ex.update(KONEX)

    db = connect()
    try:
        df = db.raw_sql(build_query(list(ex.keys())),
                        date_cols=["listing_start", "listing_end"])
    finally:
        db.close()

    # 거래소 라벨/MIC 부여
    df["exchange_mic"] = df["ex_code"].map(lambda c: ex[c][0])
    df["exchange"] = df["ex_code"].map(lambda c: ex[c][1])
    df["is_active"] = df["active_flag"].eq("1")

    # 미국/캐나다 ISIN은 CUSIP에서 파생해 결측 보완
    df["isin_source"] = df["main_isin"].notna().map({True: "factset", False: None})
    need = df["main_isin"].isna() & df["main_cusip"].notna()
    derived = df.loc[need].apply(
        lambda r: derive_isin_from_cusip(r["main_cusip"], r["company_country"]), axis=1)
    df.loc[need, "main_isin"] = derived
    df.loc[need & df["main_isin"].notna(), "isin_source"] = "cusip_derived"
    df["listing_year"] = pd.to_datetime(df["listing_start"], errors="coerce").dt.year
    df["delisting_year"] = df.apply(
        lambda r: pd.NaT if r["is_active"] else pd.to_datetime(r["listing_end"], errors="coerce"),
        axis=1)
    df["delisting_year"] = pd.to_datetime(df["delisting_year"], errors="coerce").dt.year

    out_cols = ["exchange", "exchange_mic", "factset_entity_id", "company_name",
                "company_country", "main_isin", "isin_source", "main_cusip", "main_ticker",
                "lei", "listing_start", "listing_end",
                "listing_year", "delisting_year", "is_active",
                "security_name", "entity_type"]
    df = df[out_cols].sort_values(["exchange", "company_name"])

    out = os.path.join(os.path.dirname(__file__), "company_master.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")

    # ---- 요약 ----
    print(f"총 레코드(회사×거래소 상장): {len(df):,}")
    print(f"고유 회사(factset_entity_id): {df['factset_entity_id'].nunique():,}\n")
    print("거래소별 레코드 / 상장중 / 상폐:")
    g = df.groupby("exchange").agg(
        records=("factset_entity_id", "size"),
        companies=("factset_entity_id", "nunique"),
        active=("is_active", "sum"))
    g["delisted"] = g["records"] - g["active"]
    print(g.to_string())
    print("\n식별자 결측률(%):")
    for c in ["main_isin", "main_cusip", "main_ticker", "lei"]:
        print(f"  {c:14s} {df[c].isna().mean()*100:5.1f}")
    print(f"\n저장: {out}")


if __name__ == "__main__":
    main()
