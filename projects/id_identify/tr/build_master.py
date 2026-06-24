"""글로벌 상장 '회사' 마스터 — Refinitiv/Thomson Reuters(tr_common) 단독.

원천 독립 3-버전 중 #3 (TR). 회사 grain = PermID org(orgpermid).
경로(검증): permquoteref(exchcode, isprimary, status) + permquoteinfo(category='ORD'=보통주)
            + perminstrref(instr→org) 로 5개 거래소의 본국 보통주 대표상장 추출.
식별자: ISIN/CUSIP=org 대표상품(priinstrpermid), RIC/SEDOL=해당 거래소 호가,
        LEI=permorgref, IPO일=permorginfo. 상폐일=RIC 종료일(9999=상장중) 근사.

스코프: 보통주만 · 본국 대표상장만(isprimary) · 2011 이후 상장상태 · 상폐 포함.
사용법: python build_master.py
"""

import os
import pandas as pd
import wrds
from dotenv import load_dotenv

HERE = os.path.dirname(__file__)
ROOT_ENV = os.path.join(HERE, "..", "..", "..", ".env")
OUT = os.path.join(HERE, "company_master.csv")
CUTOFF = "2011-01-01"
CHUNK = 3000

# TR exchcode → (거래소, MIC)
# 주의: TR exchcode와 거래소가 1:1이 아님(노이즈). Nasdaq 대표상장은 NSM(최다)/NMS/NAS/NAQ로 분산
# (Apple=NSM). KOSPI=KSC, KOSDAQ=KOE. KONEX(KNX)·대만 TPEx(TWO)는 제외.
EXCH = {
    "NYS": ("NYSE", "XNYS"),
    "NSM": ("Nasdaq", "XNAS"), "NMS": ("Nasdaq", "XNAS"),
    "NAS": ("Nasdaq", "XNAS"), "NAQ": ("Nasdaq", "XNAS"),
    "KSC": ("KRX", "XKRX"), "KOE": ("KRX", "XKRX"),
    "TYO": ("JPX(TSE)", "XTKS"),
    "TAI": ("TWSE", "XTAI"),
}


def connect():
    load_dotenv(ROOT_ENV)
    return wrds.Connection(wrds_username=os.getenv("WRDS_USERNAME"),
                           wrds_password=os.getenv("WRDS_PASSWORD"))


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def fetch(db, sql_fn, ids):
    ids = [str(int(x)) for x in ids if pd.notna(x)]
    out = []
    for c in chunks(ids, CHUNK):
        out.append(db.raw_sql(sql_fn(",".join(c))))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def main():
    db = connect()
    try:
        codes = ",".join(f"'{c}'" for c in EXCH)
        # 1) 5개 거래소의 보통주 대표상장 (범위 좁힌 쿼리 → 빠름)
        base = db.raw_sql(f"""
            SELECT qr.quotepermid, qr.exchcode, qr.instrpermid, qr.status,
                   ir.orgpermid
            FROM tr_common.permquoteref qr
            JOIN tr_common.permquoteinfo qi
                 ON qi.quotepermid = qr.quotepermid AND qi.category = 'ORD'
            JOIN tr_common.perminstrref ir ON ir.instrpermid = qr.instrpermid
            WHERE qr.exchcode IN ({codes}) AND qr.isprimary = '1'
        """)
        print(f"대표 보통주 호가: {len(base):,}행, 고유 org {base['orgpermid'].nunique():,}")

        base["exchange"] = base["exchcode"].map(lambda c: EXCH[c][0])
        base["exchange_mic"] = base["exchcode"].map(lambda c: EXCH[c][1])
        base["is_ac"] = base["status"].eq("AC")
        # org×거래소 1행 (상장중 우선)
        base = (base.sort_values("is_ac", ascending=False)
                    .drop_duplicates(["orgpermid", "exchange"]))

        orgs = base["orgpermid"].dropna().unique().tolist()
        quotes = base["quotepermid"].dropna().unique().tolist()

        # 2) org 정보 (대표상품/대표호가/LEI/회사명/모회사)
        org = fetch(db, lambda v: f"""
            SELECT orgpermid, comname AS company_name, lei,
                   priinstrpermid, ultimateparentorgpermid AS uparent_id
            FROM tr_common.permorgref WHERE orgpermid IN ({v})
        """, orgs)
        info = fetch(db, lambda v: f"""
            SELECT DISTINCT ON (orgpermid) orgpermid, ipodate,
                   iso2cntrycode AS company_country
            FROM tr_common.permorginfo
            WHERE orgpermid IN ({v}) AND ipodate IS NOT NULL
            ORDER BY orgpermid, ipodate
        """, orgs)

        instrs = org["priinstrpermid"].dropna().unique().tolist()
        # 3) ISIN/CUSIP = 대표상품 기준 최신
        isin = fetch(db, lambda v: f"""
            SELECT DISTINCT ON (instrpermid) instrpermid, isin
            FROM tr_common.permisindata WHERE instrpermid IN ({v})
            ORDER BY instrpermid, enddate DESC
        """, instrs)
        cusip = fetch(db, lambda v: f"""
            SELECT DISTINCT ON (instrpermid) instrpermid, cusip
            FROM tr_common.permcusipdata WHERE instrpermid IN ({v})
            ORDER BY instrpermid, enddate DESC
        """, instrs)

        # 4) RIC/SEDOL = 해당 거래소 호가 기준 최신 (+ RIC 종료일 = 상폐 근사)
        ric = fetch(db, lambda v: f"""
            SELECT DISTINCT ON (quotepermid) quotepermid, ric, enddate AS ric_end
            FROM tr_common.permricdata WHERE quotepermid IN ({v})
            ORDER BY quotepermid, enddate DESC
        """, quotes)
        sedol = fetch(db, lambda v: f"""
            SELECT DISTINCT ON (quotepermid) quotepermid, sedol
            FROM tr_common.permsedoldata WHERE quotepermid IN ({v})
            ORDER BY quotepermid, enddate DESC
        """, quotes)

        parents = org["uparent_id"].dropna().unique().tolist()
        pname = fetch(db, lambda v: f"""
            SELECT orgpermid AS uparent_id, comname AS ultimate_parent
            FROM tr_common.permorgref WHERE orgpermid IN ({v})
        """, parents) if parents else pd.DataFrame(columns=["uparent_id", "ultimate_parent"])
    finally:
        db.close()

    # ---- 머지 ----
    df = (base.merge(org, on="orgpermid", how="left")
              .merge(info, on="orgpermid", how="left")
              .merge(isin, left_on="priinstrpermid", right_on="instrpermid", how="left")
              .merge(cusip, left_on="priinstrpermid", right_on="instrpermid",
                     how="left", suffixes=("", "_c"))
              .merge(ric, on="quotepermid", how="left")
              .merge(sedol, on="quotepermid", how="left")
              .merge(pname, on="uparent_id", how="left"))

    df = df.rename(columns={"isin": "main_isin", "cusip": "main_cusip", "ric": "main_ticker"})
    df["is_active"] = df["is_ac"]

    # ⚠️ TR(tr_common)에는 신뢰할 수 있는 상폐일이 없음(RIC 종료일=9999 sentinel,
    #    Datastream secmapx enddate=벤더 갱신일). → listing_end 미제공(불명).
    df["listing_start"] = pd.to_datetime(df["ipodate"], errors="coerce")
    df["listing_end"] = pd.NaT
    df["listing_year"] = df["listing_start"].dt.year.astype("Int64")
    df["delisting_year"] = pd.Series([pd.NA] * len(df), dtype="Int64")

    # 2011 필터는 상폐일이 없어 적용 불가:
    #   상장중(status=AC)은 전부 포함(현재 상장이므로 2011+ 충족),
    #   상폐(DC)는 시점을 알 수 없어 '전기간' 포함(주의: 2011 한정 아님 — README 참조).

    df["ric"] = df["main_ticker"]
    out_cols = ["exchange", "exchange_mic", "orgpermid", "company_name", "company_country",
                "main_isin", "main_cusip", "main_ticker", "ric", "sedol", "lei",
                "ultimate_parent", "listing_start", "listing_end",
                "listing_year", "delisting_year", "is_active"]
    df["orgpermid"] = df["orgpermid"].astype("Int64")
    df = df[out_cols].sort_values(["exchange", "company_name"])
    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    # ---- 요약 ----
    print(f"\n총 레코드: {len(df):,} / 고유 org {df['orgpermid'].nunique():,}")
    g = df.groupby("exchange").agg(records=("orgpermid", "size"),
                                   active=("is_active", "sum"))
    g["delisted"] = g["records"] - g["active"]
    print(g.to_string())
    print("\n식별자 채움률(%):")
    for c in ["main_isin", "main_cusip", "main_ticker", "sedol", "lei"]:
        print(f"  {c:12s}{df[c].notna().mean()*100:5.1f}")
    print(f"\n저장: {OUT}")


if __name__ == "__main__":
    main()
