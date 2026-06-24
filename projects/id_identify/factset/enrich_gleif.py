"""v2 보강 (2/2): GLEIF 공개 ISIN→LEI 매핑으로 LEI 결측 보완.

company_master_v2.csv(이미 TR 보강됨) → 최종 LEI 확정.
최종 lei = FactSet → Refinitiv(tr_lei) → GLEIF 우선순위, lei_source로 출처 표기.

GLEIF 파일은 무료 공개본:
  https://www.gleif.org/en/lei-data/lei-mapping/download-isin-to-lei-relationship-files
  (다운로드 zip 안에 lei-isin-*.csv, 컬럼 LEI,ISIN)
사용법:
  python enrich_gleif.py <gleif_isin_lei.zip>
"""

import os
import sys
import zipfile

import pandas as pd

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "company_master_v2.csv")


def load_gleif_map(zip_path: str, want: set[str]) -> dict:
    """zip 내 CSV를 청크로 스트리밍하며 want에 든 ISIN만 isin→lei로 수집."""
    z = zipfile.ZipFile(zip_path)
    name = z.namelist()[0]
    mp = {}
    with z.open(name) as f:
        for chunk in pd.read_csv(f, usecols=["LEI", "ISIN"], chunksize=1_000_000,
                                 dtype=str):
            hit = chunk[chunk["ISIN"].isin(want)]
            for isin, lei in zip(hit["ISIN"], hit["LEI"]):
                mp.setdefault(isin, lei)
    return mp


def main():
    if len(sys.argv) < 2:
        raise SystemExit("사용법: python enrich_gleif.py <gleif_isin_lei.zip>")
    zip_path = sys.argv[1]

    df = pd.read_csv(SRC)
    want = set(df["main_isin"].dropna().unique())
    print(f"master {len(df):,}행 / 조회 ISIN {len(want):,}개 — GLEIF 스캔 중...")

    gmap = load_gleif_map(zip_path, want)
    print(f"GLEIF 매칭: {len(gmap):,} ISIN")

    df["gleif_lei"] = df["main_isin"].map(gmap)

    # 최종 LEI: FactSet → TR → GLEIF
    df["lei_final"] = df["lei"].fillna(df["tr_lei"]).fillna(df["gleif_lei"])

    def src(r):
        if isinstance(r["lei"], str):
            return "factset"
        if isinstance(r["tr_lei"], str):
            return "refinitiv"
        if isinstance(r["gleif_lei"], str):
            return "gleif"
        return None
    df["lei_source"] = df.apply(src, axis=1)

    # 교차검증: 기존(FactSet/TR) LEI vs GLEIF 둘 다 있을 때 일치율
    prior = df["lei"].fillna(df["tr_lei"])
    both = prior.notna() & df["gleif_lei"].notna()
    agree = (prior[both] == df.loc[both, "gleif_lei"]).sum()

    # 최종 정리: lei 컬럼을 lei_final로 대체, 보조 컬럼 정돈
    df["lei"] = df["lei_final"]
    drop = ["tr_lei", "gleif_lei", "lei_final"]
    df = df.drop(columns=[c for c in drop if c in df.columns])

    out = os.path.join(HERE, "company_master_v2.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")

    # ---- 요약 ----
    print("\nLEI 결측률 by 거래소 (최종):")
    g = df.groupby("exchange").apply(
        lambda x: pd.Series({"n": len(x),
                             "lei_miss%": round(x["lei"].isna().mean()*100, 1)}),
        include_groups=False)
    print(g.to_string())
    print("\nLEI 출처 분포:")
    print(df["lei_source"].value_counts(dropna=False).to_string())
    print(f"\n전체 LEI 결측: {df['lei'].isna().mean()*100:.1f}%")
    print(f"교차검증: 기존vsGLEIF 양쪽보유 {both.sum():,}건 중 일치 {agree:,} "
          f"({agree/max(both.sum(),1)*100:.1f}%)")
    print(f"저장: {out}")


if __name__ == "__main__":
    main()
