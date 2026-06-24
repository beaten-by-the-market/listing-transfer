"""v2 보강 (1/2): Refinitiv/Thomson Reuters(tr_common)로 식별자·IPO일 추가.

company_master.csv → company_master_v2.csv
추가 컬럼: ric, sedol, cik, worldscope_id, ultimate_parent, ipo_date,
          listing_year_refined, tr_lei(교차검증용)

브리지: main_isin → permisindata(instrpermid) → permorgref(priinstrpermid=instrpermid)
        → org(orgpermid, valquotepermid, lei, cik, ...) ; 한 ISIN당 1건(DISTINCT ON).
RIC/SEDOL = org 대표호가(valquotepermid) 기준 최신, IPO일 = permorginfo.ipodate.
"""

import os
import pandas as pd
import wrds
from dotenv import load_dotenv

HERE = os.path.dirname(__file__)
ROOT_ENV = os.path.join(HERE, "..", "..", "..", ".env")
SRC = os.path.join(HERE, "company_master.csv")
OUT = os.path.join(HERE, "company_master_v2.csv")
CHUNK = 4000


def connect() -> wrds.Connection:
    load_dotenv(ROOT_ENV)
    return wrds.Connection(wrds_username=os.getenv("WRDS_USERNAME"),
                           wrds_password=os.getenv("WRDS_PASSWORD"))


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def fetch_concat(db, sql_for_values, values):
    """values를 CHUNK로 나눠 SQL 실행 후 concat."""
    out = []
    for c in chunks(values, CHUNK):
        vals = ",".join("'" + str(v) + "'" for v in c)
        out.append(db.raw_sql(sql_for_values(vals)))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def main():
    m = pd.read_csv(SRC)
    isins = [i for i in m["main_isin"].dropna().unique() if isinstance(i, str) and len(i) == 12]
    print(f"master {len(m):,}행 / 고유 ISIN {len(isins):,}개 보강 시작")

    db = connect()
    try:
        # 1) ISIN → org 브리지 (한 ISIN당 1건)
        bridge = fetch_concat(db, lambda v: f"""
            SELECT DISTINCT ON (i.isin)
                   i.isin,
                   o.orgpermid, o.valquotepermid, o.lei AS tr_lei,
                   o.worldscopecmpid AS worldscope_id,
                   o.ultimateparentorgpermid AS uparent_id
            FROM tr_common.permisindata i
            JOIN tr_common.permorgref o ON o.priinstrpermid = i.instrpermid
            WHERE i.isin IN ({v})
            ORDER BY i.isin, (o.lei IS NOT NULL) DESC, (o.status='Act') DESC, o.orgpermid
        """, isins)
        print(f"  org 매칭: {bridge['isin'].nunique():,} ISIN")

        orgs = bridge["orgpermid"].dropna().unique().tolist()
        quotes = bridge["valquotepermid"].dropna().unique().tolist()
        parents = bridge["uparent_id"].dropna().unique().tolist()

        # 2) IPO일 (org 기준)
        ipo = fetch_concat(db, lambda v: f"""
            SELECT DISTINCT ON (orgpermid) orgpermid, ipodate
            FROM tr_common.permorginfo
            WHERE orgpermid IN ({v}) AND ipodate IS NOT NULL
            ORDER BY orgpermid, ipodate
        """, orgs)

        # 3) RIC (대표호가 최신)
        ric = fetch_concat(db, lambda v: f"""
            SELECT DISTINCT ON (quotepermid) quotepermid, ric
            FROM tr_common.permricdata
            WHERE quotepermid IN ({v})
            ORDER BY quotepermid, enddate DESC
        """, quotes)

        # 4) SEDOL (대표호가 최신)
        sedol = fetch_concat(db, lambda v: f"""
            SELECT DISTINCT ON (quotepermid) quotepermid, sedol
            FROM tr_common.permsedoldata
            WHERE quotepermid IN ({v})
            ORDER BY quotepermid, enddate DESC
        """, quotes)

        # 5) 최종모회사명
        pname = fetch_concat(db, lambda v: f"""
            SELECT orgpermid AS uparent_id, comname AS ultimate_parent
            FROM tr_common.permorgref WHERE orgpermid IN ({v})
        """, parents) if parents else pd.DataFrame(columns=["uparent_id", "ultimate_parent"])
    finally:
        db.close()

    # ---- 머지 ----
    ric = ric.rename(columns={"quotepermid": "valquotepermid"})
    sedol = sedol.rename(columns={"quotepermid": "valquotepermid"})
    b = bridge.merge(ipo, on="orgpermid", how="left") \
              .merge(ric, on="valquotepermid", how="left") \
              .merge(sedol, on="valquotepermid", how="left") \
              .merge(pname, on="uparent_id", how="left")
    keep = ["isin", "ric", "sedol", "worldscope_id", "ultimate_parent",
            "ipodate", "tr_lei"]
    b = b[keep].rename(columns={"isin": "main_isin", "ipodate": "ipo_date"})

    df = m.merge(b, on="main_isin", how="left")

    # IPO일로 상장연도 정밀화 (TR ipodate 우선, 없으면 FactSet listing_start)
    ipo_y = pd.to_datetime(df["ipo_date"], errors="coerce").dt.year
    df["listing_year_refined"] = ipo_y.fillna(df["listing_year"]).astype("Int64")

    # LEI 교차검증 (FactSet vs TR 둘 다 있을 때 불일치 점검)
    both = df["lei"].notna() & df["tr_lei"].notna()
    mismatch = (df.loc[both, "lei"] != df.loc[both, "tr_lei"]).sum()

    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    # ---- 요약 ----
    n = len(df)
    print("\n보강 컬럼 채움률(%):")
    for c in ["ric", "sedol", "ipo_date", "ultimate_parent"]:
        print(f"  {c:16s} {df[c].notna().mean()*100:5.1f}")
    print(f"\nLEI 교차검증: 양쪽 보유 {both.sum():,}건 중 불일치 {mismatch}건")
    print(f"상장연도 정밀화: ipo_date로 채워진 행 {ipo_y.notna().sum():,} / {n:,}")
    print(f"저장: {OUT}")


if __name__ == "__main__":
    main()
