# WRDS 주요 제품군 상세 — CRSP · Compustat · Capital IQ · FactSet · Refinitiv

- **계정**: `data01@krx.co.kr`
- **확인일**: 2026-06-24
- **출처**: [WRDS_권한_DB목록.md](WRDS_권한_DB목록.md)의 구독(전체 접근) 라이브러리 중
  5개 제품군만 추려 스키마별 수록 내용·주요 테이블·활용처를 정리.
- **표기**: 스키마명 뒤 `(숫자)`는 2026-06-24 기준 해당 스키마의 테이블 수.
- ✅ = 실데이터 조회로 직접 검증된 라이브러리(`crsp`, `comp`, `factset`).

> ⚠️ 목록·테이블 정의가 보여도 실제 `SELECT` 권한이 다를 수 있습니다.
> 아래 "주요 테이블"은 각 WRDS 제품의 대표 구성이며, 사용 전
> `db.list_tables(library=...)` / `db.describe_table(...)`로 실제 보유 여부와
> 컬럼을 확인하는 것을 권장합니다(맨 아래 [확인 방법](#확인-방법) 참고).

---

## 1. CRSP — 미국 주가·지수·뮤추얼펀드 ✅

미국 상장주식(NYSE/NYSE American/NASDAQ/Arca)의 일·월별 시세, 수익률, 상장폐지,
배당·분할 조정, 시장지수, 국채, 뮤추얼펀드를 다루는 학술 표준 데이터. **이 프로젝트의 주력.**

| 스키마 | 테이블 수 | 내용 |
|--------|----------|------|
| `crsp` ✅ | 433 | CRSP 전체(통합) — 주식·지수·국채·CCM·펀드가 한 스키마에 모인 메인 라이브러리 |
| `crsp_a_stock` | 95 | 연간 갱신(Annual) 주식 파일 — 일·월별 시세·수익률·종목명·배당 |
| `crsp_a_indexes` | 113 | CRSP 시장지수·S&P500·NASDAQ 등 지수 시계열 |
| `crsp_a_treasuries` | 64 | CRSP US Treasury — 국채 일·월별 시세, 무위험수익률 |
| `crsp_a_ccm` | 12 | CRSP/Compustat Merged 링크(주가↔재무 연결) |
| `crsp_q_mutualfunds` | 29 | Survivor-Bias-Free 미국 뮤추얼펀드 — 수익률·보수·보유내역 |

**주요 테이블(대표 구성)**
- 시세·수익률: `dsf`(일별), `msf`(월별) — `prc`, `ret`, `vol`, `shrout`, `cfacpr`/`cfacshr`(조정계수)
- 종목 식별: `stocknames`, `dsenames`/`msenames`(PERMNO·PERMCO·CUSIP·TICKER·거래소·SIC)
- 이벤트: `dsedist`(배당·분할), `dsedelist`(상장폐지·`dlret`), `dseexchdates`(거래소 이전 이력)
- 지수: `dsi`/`msi`(시장 종합), `dsp500`/`msp500`(S&P500)
- 국채: `tfz_dly`/`tfz_mth`(액면별), `tfz_dly_rf`(무위험수익률)
- CCM 링크: `ccmxpf_lnkhist`(`gvkey`↔`permno`, `linktype`/`linkprim`/링크기간)
- 펀드: `fund_hdr`, `monthly_returns`, `fund_fees`, `holdings`

**활용처**: 장기 수익률·이벤트 스터디, 시장/규모/가치 포트폴리오, 거래소 이전상장 분석,
무위험수익률 기준선, 펀드 성과 평가. **PERMNO**가 핵심 키.

---

## 2. Compustat (S&P Global) — 재무제표·기업정보 ✅

상장기업 재무제표(연·분기), 기업 메타데이터, 일별 시세, 사업/지역 부문, 은행 특화 데이터.

| 스키마 | 테이블 수 | 내용 |
|--------|----------|------|
| `comp` ✅ | 293 | Compustat 메인 — 북미·글로벌 펀더멘털·시세·기업정보 통합 |
| `comp_na_daily_all` | 206 | 북미(North America) 일별 갱신 전체 |
| `comp_global_daily` | 125 | 글로벌(북미 외) 일별 갱신 — `g_` 접두 테이블 |
| `comp_snapshot` / `compsnap` | 125 | Point-in-Time 스냅샷(발표 시점 그대로, 사후수정 미반영) |
| `comp_bank_daily` | 20 | 은행 산업 특화 재무 항목 |
| `comp_segments_hist_daily` / `compseg` | 14 | 사업부문·지역부문 매출/자산 |

**주요 테이블(대표 구성)**
- 재무제표: `funda`(연간), `fundq`(분기) — `at`, `sale`, `ni`, `ceq`, `dltt`, `ib` 등 수백 항목
- 기업정보: `company`(`gvkey`·`conm`·`sic`·`gics`·`loc`), `names`
- 시세: `secd`(일별 `prccd`·`cshoc`), `secm`(월별), `sec_dprc`
- 글로벌: `g_funda`/`g_fundq`/`g_secd`(국제 기업)
- 부문: `wrds_segmerged`(세그먼트 통합), `seg_annual`
- 식별 키: **`gvkey`**(기업) + `iid`(증권) + `datadate`(회계기준일)

**활용처**: 재무비율·밸류에이션, 회계 기반 팩터(수익성·투자·발생액), 산업분류(GICS/SIC),
글로벌 비교. CRSP와는 `crsp_a_ccm`의 `ccmxpf_lnkhist`로 연결(`gvkey`↔`permno`).

> 📌 `comp_snapshot`은 "그 시점에 실제 보였던 값"이라 백테스트의 **look-ahead bias** 방지에 유용.

---

## 3. Capital IQ (S&P Global Market Intelligence)

기업·증권 식별 체계, 자본구조(부채·신용), 기업 이벤트 등 S&P Capital IQ 데이터.

| 스키마 | 테이블 수 | 내용 |
|--------|----------|------|
| `ciq` | 258 | Capital IQ 메인 — 기업·증권·재무·이벤트 |
| `ciq_common` | 59 | 공통 참조 — 식별자 매핑(`companyid`·`gvkey`·`securityid`), 기업/증권 마스터 |
| `ciq_capstrct` | 43 | Capital Structure — 부채 내역·신용등급·자본구성 |

**주요 테이블(대표 구성)**
- 식별·매핑: `ciqcompany`, `ciqsecurity`, `wrds_gvkey`(Compustat `gvkey` 연결), `ciqsymbol`
- 자본구조: `ciqcapitalstructuresummary`, `ciqcapstructuredebt`, `ciqcreditratings`
- 이벤트: `ciqkeydev`(Key Developments — M&A·실적발표·경영진 변동 등 이벤트 코드)
- 식별 키: **`companyid`**(Capital IQ 기업 ID), `securityid`, `tradingitemid`

**활용처**: 자본구조·신용 분석, 기업 이벤트(Key Developments) 추출, S&P 식별 체계와
Compustat(`gvkey`) 연계. ⚠️ 직접 조회 미검증 — 사용 전 대표 테이블 1행 확인 권장.

---

## 4. FactSet ✅

FactSet의 펀더멘털·시세·심볼로지(식별 체계)·소유구조 데이터. 글로벌 커버리지 강점.

| 스키마 | 테이블 수 | 내용 |
|--------|----------|------|
| `factset` ✅ | 378 | FactSet 메인 — 펀더멘털·시세·심볼로지·엔티티 등 통합 |
| `factset_common` | 196 | 공통 참조 — 엔티티/증권 마스터, 식별자 매핑 |
| `factset_own` | 34 | Ownership — 기관·펀드·내부자 보유 지분 |

**주요 테이블(대표 구성)**
- 심볼로지: `sym_coverage`, `sym_ticker_region`, `sym_isin`, `sym_cusip`(식별자 상호변환)
- 엔티티: `ent_entity_coverage`, `ent_entity_structure`(기업 지배구조·자회사)
- 펀더멘털: `ff_basic_af`/`ff_basic_qf`(연·분기 재무), `ff_advanced_*`
- 시세: `fp_basic_prices`(가격·수익률), 거래량·시가총액
- 소유구조: `own_basic`(기관 보유), `own_inst_holdings`, `own_fund_holdings`
- 식별 키: **`fsym_id`**(FactSet Symbol), `factset_entity_id`

**활용처**: 글로벌 기업·증권 식별 통합(ISIN/CUSIP/SEDOL 매핑 허브), 기관 소유구조 분석,
글로벌 펀더멘털·시세. 여러 벤더 식별자를 잇는 **심볼로지 허브**로 특히 유용.

---

## 5. Thomson Reuters / Refinitiv

Datastream(글로벌 시계열: 주식·선물·상품·경제지표)과 SDC(M&A·신규발행) 계열.

| 스키마 | 테이블 수 | 내용 |
|--------|----------|------|
| `trdstrm` | 82 | Datastream 메인 — 글로벌 시계열 데이터 |
| `tr_ds_equities` | 43 | Datastream 주식 — 글로벌 주가·수익률·시가총액 |
| `tr_ds_fut` | 20 | Datastream 선물 |
| `tr_ds_comds` | 11 | Datastream 상품(commodities) |
| `tr_ds_econ` | 8 | Datastream 경제지표(거시 시계열) |
| `tr_common` / `trcommon` | 30 | 공통 참조 — 종목 마스터·식별자 매핑 |
| `tr_sdc_samples` | 12 | SDC Platinum 표본 — M&A·신규발행 등(제한 표본) |

**주요 테이블(대표 구성)**
- 주식: `wrds_ds2dsf`(일별 시세·수익률), 시가총액·거래량
- 식별: `ds2ctryqtinfo`/마스터 테이블(`infocode`·`dscode`·ISIN·국가)
- 선물·상품·경제: 각 스키마의 시계열 테이블(`tr_ds_fut`/`tr_ds_comds`/`tr_ds_econ`)
- SDC: `tr_sdc_samples`의 M&A·발행 딜 표본
- 식별 키: **`infocode`**(Datastream 내부 코드), `dscode`

**활용처**: 미국 외 글로벌 시장 시세(Datastream이 국제 커버리지 강점), 선물·상품·거시
시계열, M&A/신규발행 이벤트(SDC). ⚠️ `tr_sdc_samples`는 전체가 아닌 표본이며,
Datastream 계열도 직접 조회 미검증 — 사용 전 1행 확인 권장.

---

## 제품군 한눈에 — 식별 키와 연결

| 제품군 | 핵심 식별 키 | 강점 영역 | 타 제품 연결 |
|--------|-------------|----------|-------------|
| CRSP | `permno`, `permco` | 미국 주가·수익률·지수 | `crsp_a_ccm` → Compustat `gvkey` |
| Compustat | `gvkey`, `iid` | 재무제표·산업분류 | CCM으로 CRSP, `ciq_common`으로 Capital IQ |
| Capital IQ | `companyid` | 자본구조·신용·이벤트 | `wrds_gvkey`로 Compustat |
| FactSet | `fsym_id` | 글로벌 식별·소유구조 | 심볼로지로 ISIN/CUSIP 등 전방위 |
| Refinitiv | `infocode` | 글로벌 시세·선물·상품·M&A | `tr_common` 마스터 |

**전형적 연결 흐름**: 미국 분석은 `permno`(CRSP) ↔ `gvkey`(Compustat)를
`ccmxpf_lnkhist`로 잇고, 글로벌·식별 확장이 필요하면 FactSet 심볼로지(`fsym_id`)나
Capital IQ(`companyid`)를 경유.

---

## 확인 방법

```python
from exchange_transfers import connect
db = connect()

# 스키마 안의 테이블 목록
db.list_tables(library="crsp")
db.list_tables(library="factset")

# 특정 테이블 컬럼 스키마
db.describe_table("comp", "funda")

# 권한·존재 확인용 1행 조회
db.raw_sql("SELECT * FROM crsp.dsf LIMIT 1")

db.close()
```

전체 접근 가능 스키마(243개)와 샘플·트라이얼 구분은
[WRDS_권한_DB목록.md](WRDS_권한_DB목록.md), 재현 스크립트는
[list_wrds_access.py](list_wrds_access.py) 참고.
