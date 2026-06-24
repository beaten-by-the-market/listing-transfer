# -*- coding: utf-8 -*-
"""
build_master.py  -- Compustat (S&P) version of the global listed-COMPANY master.

One of three independent source versions (FactSet / Compustat / Refinitiv-TR).

Goal
----
For NYSE, Nasdaq, JPX(Tokyo/TSE), KRX(KOSPI+KOSDAQ), TWSE: extract every
COMPANY (legal entity = GVKEY) that was in listed status at any time from
2011-01-01 onward (companies listed before 2011 but active or delisted after
2011 are kept; companies delisted before 2011 are excluded). Delisted companies
are included. One row per company x exchange.

Scope
-----
- Common / ordinary stock only (tpci='0'). Preferred/ETF/fund/REIT/ADR excluded.
- Home / primary common listing only. Uses the company's PRIMARY issue:
    * US (NYSE/Nasdaq)  -> comp.company.priusa  joined to comp.security
    * Asia (KRX/JPX/TWSE) -> comp.g_company.prirow joined to comp.g_security
- Company grain = GVKEY. GVKEY is unique across NA and Global universes.

Identifiers
-----------
- main_isin : Compustat Global ISIN for Asia (~98-99% coverage);
              for US, comp.security ISIN is sparse, so ISIN is DERIVED from CUSIP
              (isin_source='cusip_derived'); native ISIN used when present.
- main_cusip: present for US (~100%), absent for Compustat Global (Asia).
- main_ticker: comp.security.tic (US strong, Asia weak/empty).
- sedol     : from the security table.
- lei       : NOT available in Compustat -> left empty (known gap, documented).

Output: compustat/company_master.csv
"""
import os, sys
import pandas as pd
import wrds
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(HERE, "company_master.csv")

# ---------------------------------------------------------------------------
# Exchange mapping
# ---------------------------------------------------------------------------
EXCH_MAP = {
    11:  ("NYSE",     "XNYS"),
    14:  ("Nasdaq",   "XNAS"),
    248: ("KRX",      "XKRX"),   # Korea Exchange Stock Market (KOSPI)
    298: ("KRX",      "XKRX"),   # Korea Exchange KOSDAQ
    260: ("TWSE",     "XTAI"),   # Taiwan Stock Exchange
    264: ("JPX(TSE)", "XTKS"),   # Tokyo Stock Exchange
    293: ("JPX(TSE)", "XTKS"),   # Tokyo Stock Exchange JASDAQ
}
NA_EXCH = (11, 14)
G_EXCH  = (248, 298, 260, 264, 293)
COMMON_TPCI = "0"          # 'Common or ordinary' per comp.r_issuetyp
CUTOFF = "2011-01-01"


# ---------------------------------------------------------------------------
# ISIN check-digit (US/CA derivation from CUSIP)  -- VERIFIED in spec
# ---------------------------------------------------------------------------
def isin_check_digit(body):   # body = 2-char country + 9-char NSIN
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


_VALID = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def cusip_to_isin(cusip, country):
    """Build ISIN from a 9-char CUSIP for US/CA. Returns None if not derivable."""
    if not cusip or country not in ("US", "CA"):
        return None
    c = str(cusip).strip().upper()
    if len(c) != 9 or any(ch not in _VALID for ch in c):
        return None
    body = country + c
    return body + isin_check_digit(body)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
NA_SQL = """
    select s.gvkey, s.iid as primary_iid, s.isin, s.cusip, s.tic, s.sedol, s.exchg,
           c.conml, c.conm, c.loc, c.fic, c.ipodate, c.dldte, c.costat
    from comp.company c
    join comp.security s
      on c.gvkey = s.gvkey and c.priusa = s.iid
    where s.exchg in (11, 14)
      and s.tpci = '0'
      and (c.costat = 'A' or c.dldte >= '{cut}')
""".format(cut=CUTOFF)

G_SQL = """
    select s.gvkey, s.iid as primary_iid, s.isin, s.cusip, s.tic, s.sedol, s.exchg,
           c.conml, c.conm, c.loc, c.fic, c.ipodate, c.dldte, c.costat
    from comp.g_company c
    join comp.g_security s
      on c.gvkey = s.gvkey and c.prirow = s.iid
    where s.exchg in (248, 298, 260, 264, 293)
      and s.tpci = '0'
      and (c.costat = 'A' or c.dldte >= '{cut}')
""".format(cut=CUTOFF)


def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NaT:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    if not s or s.lower() in ("none", "nan", "nat", "<na>"):
        return None
    return s


def build_rows(df, is_us):
    rows = []
    for r in df.itertuples(index=False):
        exch, mic = EXCH_MAP[int(r.exchg)]
        loc = clean(r.loc) or clean(r.fic)
        country2 = None
        if loc:
            # Compustat loc is ISO-3 (USA, KOR, JPN, TWN, CAN). Map to 2-char
            # only for CUSIP->ISIN; keep 3-char in company_country to match source.
            country2 = {"USA": "US", "CAN": "CA"}.get(loc)

        isin = clean(r.isin)
        isin_src = "compustat" if isin else None
        cusip = clean(r.cusip)
        if not isin and is_us and cusip:
            derived = cusip_to_isin(cusip, country2)
            if derived:
                isin, isin_src = derived, "cusip_derived"

        ipod = clean(r.ipodate)
        dld  = clean(r.dldte)
        is_active = (clean(r.costat) == "A")
        listing_end = None if is_active else dld
        listing_year   = int(ipod[:4]) if ipod else None
        delisting_year = int(listing_end[:4]) if listing_end else None

        rows.append({
            "exchange":        exch,
            "exchange_mic":    mic,
            "gvkey":           clean(r.gvkey),
            "company_name":    clean(r.conml) or clean(r.conm),
            "company_country": loc,
            "main_isin":       isin,
            "isin_source":     isin_src,
            "main_cusip":      cusip,
            "main_ticker":     clean(r.tic),
            "sedol":           clean(r.sedol),
            "lei":             None,                # not in Compustat
            "listing_start":   ipod,
            "listing_end":     listing_end,
            "listing_year":    listing_year,
            "delisting_year":  delisting_year,
            "is_active":       is_active,
            "primary_iid":     clean(r.primary_iid),
        })
    return rows


def main():
    load_dotenv(r"c:\Users\Peter\Desktop\wrds\.env")
    db = wrds.Connection(wrds_username=os.getenv("WRDS_USERNAME"),
                         wrds_password=os.getenv("WRDS_PASSWORD"))
    try:
        na = db.raw_sql(NA_SQL)
        g  = db.raw_sql(G_SQL)
    finally:
        db.close()

    rows = build_rows(na, is_us=True) + build_rows(g, is_us=False)
    cols = ["exchange", "exchange_mic", "gvkey", "company_name", "company_country",
            "main_isin", "isin_source", "main_cusip", "main_ticker", "sedol", "lei",
            "listing_start", "listing_end", "listing_year", "delisting_year",
            "is_active", "primary_iid"]
    df = pd.DataFrame(rows, columns=cols)

    # one row per company x exchange (exchange = mapped label, not raw exchg code,
    # so KOSPI+KOSDAQ both = KRX). Dedup defensively on (gvkey, exchange).
    before = len(df)
    df = df.drop_duplicates(subset=["gvkey", "exchange"]).reset_index(drop=True)
    deduped = before - len(df)

    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    # -------------------- summary --------------------
    print("=" * 70)
    print("Compustat company_master built:", OUT_CSV)
    print("Total rows: %d   unique gvkey: %d   (deduped %d)"
          % (len(df), df["gvkey"].nunique(), deduped))

    print("\n-- per exchange (rows / unique gvkey / active / delisted) --")
    for ex in ["NYSE", "Nasdaq", "KRX", "JPX(TSE)", "TWSE"]:
        sub = df[df["exchange"] == ex]
        act = int(sub["is_active"].sum())
        print("  %-9s rows=%-6d gvkey=%-6d active=%-6d delisted=%-6d"
              % (ex, len(sub), sub["gvkey"].nunique(), act, len(sub) - act))

    print("\n-- identifier fill rates --")
    n = len(df)
    for c in ["main_isin", "main_cusip", "main_ticker", "sedol", "lei"]:
        filled = df[c].notna().sum()
        print("  %-12s %6d / %d  (%.1f%%)" % (c, filled, n, 100.0 * filled / n))
    print("  isin_source breakdown:",
          df["isin_source"].value_counts(dropna=False).to_dict())

    print("\n-- spot checks --")
    checks = [
        ("Samsung Electronics", "KR7005930003", "KRX"),
        ("SK hynix",            "KR7000660001", "KRX"),
        ("Toyota",              "JP3633400001", "JPX(TSE)"),
        ("TSMC",                "TW0002330008", "TWSE"),
        ("Apple",               "US0378331005", "Nasdaq"),
    ]
    for name, isin, exp_ex in checks:
        hit = df[df["main_isin"] == isin]
        if len(hit):
            r = hit.iloc[0]
            ok = "OK" if r["exchange"] == exp_ex else "EXCH-MISMATCH(%s)" % r["exchange"]
            print("  [%s] %-22s %s  gvkey=%s name=%s"
                  % (ok, name, isin, r["gvkey"], r["company_name"]))
        else:
            print("  [MISSING] %-22s %s (expected %s)" % (name, isin, exp_ex))
    print("=" * 70)


if __name__ == "__main__":
    main()
