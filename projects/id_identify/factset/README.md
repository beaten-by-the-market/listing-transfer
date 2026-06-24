# id_identify — 글로벌 상장 "회사" 마스터 (식별자 통합)

## 목표

2011년 이후 **NYSE · Nasdaq · JPX(도쿄) · KRX(한국) · TWSE(대만)** 에 상장된
**회사(법인) 기준** 목록을 구축한다.

- 종목(증권)이 아닌 **회사 단위** (한 회사가 여러 거래소에 상장되면 거래소별 레코드)
- **상장폐지된 회사도 포함**, 상장일/상장폐지일(불가 시 연도)
- 범용 공통식별자: **티커, ISIN(회사 기준 = 메인 보통주의 ISIN), LEI, CUSIP**

## 결론: 주력 DB = **FactSet** (WRDS `factset` / `factset_common`)

FactSet은 5개 거래소를 **하나의 일관된 스키마**로 덮고, 회사(entity) ↔ 증권 ↔
식별자 그래프와 **메인 보통주 지정**, 그리고 **LEI까지** 가진 유일한 구독 소스다.
(다른 DB는 아래 비교표 참조 — 특히 LEI는 FactSet에만 있음.)

| 요건 | FactSet | Compustat | Capital IQ | CRSP |
|---|---|---|---|---|
| 회사(법인) 키 | `factset_entity_id` | GVKEY | companyid | PERMCO(미국만) |
| 5개 거래소 | ✅ 전부 | ✅ 전부 | ✅ 전부 | ❌ 미국만 |
| 메인 보통주 | `fsym_primary_equity_id` | prirow/priusa/prican | primaryflag | PERMNO |
| ISIN / CUSIP / 티커 | ✅ / ✅ / ✅ | ✅ / ✅ / △ | ✅ / ✅ / ✅ | 파생 / ✅ / ✅ |
| **LEI** | ✅ **138,892건** | ❌ | ❌ | ❌ |
| 상장/폐지 일자 | hist start/end + active | ipodate/dldte/dldtei | start/end + status | 미국 최정밀 |

→ **FactSet 단일 소스로 v1 구축**, 일자 정밀도는 Compustat(글로벌 `ipodate/dldte`)와
CRSP(미국)로 **선택 보강**.

---

## 검증된 FactSet 스키마 (2026-06-24 직접 확인)

### 회사 ↔ 증권 ↔ 식별자
- `factset.sym_coverage` — 증권 마스터. 핵심 컬럼:
  `fsym_id, proper_name, fsym_primary_equity_id, fsym_primary_listing_id,`
  `active_flag, fref_security_type, fref_listing_exchange, listing_flag,`
  `regional_flag, security_flag, fsym_security_id, fsym_regional_id`
- `factset.sym_sec_entity` — `fsym_id → factset_entity_id` (증권 → **회사**).
  ⚠️ **`fsym_security_id`(–S 레벨)로 조인**해야 함 (listing –L 레벨로는 매칭 안 됨, 검증 완료)
- `factset.sym_entity` — `factset_entity_id, entity_proper_name, iso_country, entity_type`
- **ISIN: `factset.sym_xc_isin` (fsym_id→isin)** — ⚠️ `sym_isin`(36만 건)은 아시아 커버리지가
  희박해 **사용 금지**. `sym_xc_isin`(3,064만 건, KR 15.8만·TW 61.7만 보유)을 **security 레벨
  (`fsym_security_id`/`fsym_primary_equity_id`)** 로 조인. (검증: 삼성전자→KR7005930003 ✅)
- `factset.sym_cusip`, `factset.sym_ticker_exchange`, `factset.sym_ticker_region`
- 이력(일자): `sym_ticker_region_hist` `(start_date, end_date, most_recent)` →
  **상장/폐지 구간 도출** (regional 레벨 `fsym_id` 기준 — 아래 grain 참고)

### LEI (회사 기준)
- `factset_common.edm_standard_entity_identifiers`
  `(factset_entity_id, entity_id_type, entity_id_value)`
  — `entity_id_type='LEI'` 138,892건. `factset_entity_id`로 회사에 직접 결합.

### 거래소(MIC) 매핑 — 5개 venue 확정
- `factset.fref_sec_exchange_map` `(fref_exchange_code, fref_exchange_desc, iso_mic, ...)`

| Venue | iso_mic | FactSet code | 비고 |
|---|---|---|---|
| NYSE | `XNYS` | NYS | New York Stock Exchange |
| Nasdaq | `XNAS` | NAS | NASDAQ |
| JPX(도쿄) | `XTKS` | TKS | Tokyo Stock Exchange |
| KRX | `XKRX` | KRX | Korea KRX Exchange (KOSPI/KOSDAQ 포함 추정) |
| KRX(KONEX) | `XKON` | KON | Korea KRX KONEX (별도, 포함 여부 결정) |
| TWSE | `XTAI` | TAI | Taiwan Stock Exchange |

### 보통주 타입 코드 (`fref_security_type`)
- `SHARE` = Share/Common/Ordinary ← **회사 보통주**
- 참고 제외 후보: `PREF/PREFEQ`(우선주), `ETF_*`, `MF_O/MF_C`(펀드),
  `ADR/GDR/DR/NVDR`(예탁증서), `RIGHT/WARRANT/UNIT` 등

---

## 데이터 모델 (회사 기준)

```
factset_entity_id (회사)
   ├─ entity_proper_name, iso_country (본사 소재국)
   ├─ LEI                         ← edm_standard_entity_identifiers
   ├─ 메인 보통주 (primary equity) ← fsym_primary_equity_id
   │     ├─ ISIN  (sym_isin)      ← "회사 기준 ISIN"
   │     ├─ CUSIP (sym_cusip)
   │     └─ 티커  (sym_ticker_region / _exchange)
   └─ 상장(listing) [거래소별 N개]  ← listing_flag, fref_listing_exchange ∈ 5 MIC
         ├─ 거래소 (XNYS/XNAS/XTKS/XKRX/XTAI)
         ├─ 상장일  ← MIN(start_date)  (sym_ticker_exchange_hist)
         ├─ 상폐일  ← active=false면 MAX(end_date), 아니면 NULL(상장중)
         └─ 티커(해당 거래소)
```

핵심: **"회사 기준 ISIN"은 상장 거래소가 아니라 법인의 메인 보통주에서** 가져온다.
→ 예: 한국 회사가 KRX 보통주 + NYSE ADR로 동시 상장이어도, ISIN은 KR... (홈 보통주)로
고정되고 NYSE는 "상장 레코드"로만 잡힌다. (사용자 요건과 일치)

---

## 제안 산출물 스키마 (CSV)

| 컬럼 | 설명 | 소스 |
|---|---|---|
| `factset_entity_id` | 회사 키(스파인) | sym_entity |
| `company_name` | 회사명 | sym_entity.entity_proper_name |
| `iso_country` | 본사 소재국 | sym_entity.iso_country |
| `lei` | LEI | edm_standard_entity_identifiers |
| `main_isin` | 메인 보통주 ISIN | sym_xc_isin (security) + US/CA는 CUSIP 파생 |
| `isin_source` | ISIN 출처(`factset`/`cusip_derived`) | 파생 |
| `main_cusip` | 메인 보통주 CUSIP | sym_cusip |
| `main_ticker` | 홈 시장 티커(예: `005930-KR`, `AAPL-US`) | sym_ticker_region |
| `exchange_mic` | 상장 거래소 | XNYS/XNAS/XTKS/XKRX/XTAI |
| `listing_start` | 상장일(또는 연도) | sym_ticker_region_hist.start_date |
| `listing_end` | 상폐일(상장중이면 NULL) | sym_ticker_region_hist.end_date |
| `is_active` | 현재 상장 여부 | sym_coverage.active_flag |
| `listing_year` / `delisting_year` | 상장/상폐 연도(파생) | derived |
| `security_name`, `entity_type` | 증권명/엔티티유형 | sym_coverage / sym_entity |

필터: **5개 거래소 중 하나가 홈(대표) 거래소 + 상장구간이 2011-01-01 이후와 겹침**(상폐 포함).

---

## 처리 단계 (파이프라인) — 구현: [build_master.py](build_master.py)

**Grain = regional(-R) 레벨** (핵심 결정). FactSet은 한 보통주(-S)가 호가되는 *모든*
거래소를 listing(-L) 행으로 둬서(예: Apple 109개 venue) listing 레벨로 잡으면 중복 폭증.
반면 **regional 행은 지역(국가)당 1개**이고 그 지역의 **대표 거래소**를 가지므로,
미국 종목이 NYSE/Nasdaq 중 진짜 주거래소로 자동 분기되고 ADR(다른 -S)은 SHARE 필터로 제외된다.

1. **regional 추출**: `sym_coverage` `regional_flag='1'` + `fref_security_type='SHARE'`
   + `fref_listing_exchange ∈ {NYS,NAS,TKS,KRX,TAI}`.
2. **회사 결합**: `sym_sec_entity`(on `fsym_security_id`) → `factset_entity_id` → `sym_entity`.
3. **식별자**: ISIN=`sym_xc_isin`(security), CUSIP=`sym_cusip`, 티커=`sym_ticker_region`.
   미국/캐나다 ISIN 결측은 **CUSIP→ISIN 체크디지트 파생**으로 보완.
4. **상장구간/일자**: `sym_ticker_region_hist` start/end + `active_flag`. **2011 이후 필터**.
5. **LEI 결합**: `edm_standard_entity_identifiers (type='LEI')`.
6. **검증**: 거래소별 상장중 회사 수 sanity check, 스팟체크, 결측률 점검.

---

## 확정된 스코프 (2026-06-24)

1. **상장 단위**: 회사를 거래소별로 중복 허용(같은 회사가 NYSE+KRX면 2행).
2. **증권 범위**: **보통주(`SHARE`)만**. 우선주/REIT/ETF/펀드/예탁증서 제외.
3. **ADR/교차상장**: **본국 보통주 상장만** 포함(외국기업 ADR 제외 — SHARE 필터로 자연 제외).
4. **KRX 범위**: 기본 `XKRX`(KOSPI+KOSDAQ). KONEX는 `--konex` 옵션으로 선택 포함.
5. **일자 정밀도**: **FactSet 단독**(구간/연도). Compustat/CRSP 보강은 보류.
6. **2011 기준**: 2011-01-01 이후 **한 번이라도 상장 상태였던 회사**(이전 상장+이후 상폐 포함).

## v1 결과 (2026-06-24) — `company_master.csv`

- 총 **19,759** 레코드(회사×거래소) / 고유 회사 **18,369**.
- 상장중 회사 수(현실과 부합): JPX 3,997 · KRX 2,668 · Nasdaq 3,213 · NYSE 1,733 · TWSE 1,084.
- 식별자 결측: ISIN **10.7%**(US는 CUSIP 파생으로 보완) · CUSIP 5.0% · 티커 7.2% · **LEI 71.4%**.
- 스팟체크 정확: 삼성전자 `KR7005930003` · SK하이닉스 `KR7000660001` · 토요타 `JP3633400001`
  · TSMC `TW0002330008` (LEI 포함). Apple은 Nasdaq 단일행 `US0378331005`(CUSIP 파생).

## v2 보강 (2026-06-24) — `company_master_v2.csv`

v1(FactSet)에 **Refinitiv/TR + GLEIF**를 더해 식별자·상장일을 보강.
파이프라인: `build_master.py` → `enrich_tr.py` → `enrich_gleif.py`.

- **TR(`tr_common`) 추가**: `ric`·`sedol`·`ultimate_parent`·`worldscope_id`,
  그리고 **`ipo_date`(정밀 IPO일)** → `listing_year_refined`.
  브리지: `main_isin → permisindata → permorgref(priinstrpermid)`. LEI 교차검증 일치 99%.
- **GLEIF ISIN↔LEI**: `main_isin` 기준 조인으로 LEI 보완(+출처 `lei_source`).
- **최종 LEI 우선순위**: FactSet → Refinitiv → GLEIF.

**v2 종합 식별자 채움률**: ISIN **89.3%** · CUSIP 95.0% · 티커 92.8% ·
**RIC 71.5%** · SEDOL 70.8% · **IPO일 49.2%** · 최종모회사 71.6% · **LEI 30.7%**.

스팟체크: 삼성 `005930.KS`/IPO 1975-06-11 · 토요타 `7203.T`/1949 · TSMC `2330.TW`/1994.
(FactSet은 IPO를 심볼생성연도로 잡았으나 TR로 실제 IPO 연도 교정됨.)

## ⚠️ 알려진 한계 / 다음 단계

- **LEI는 근본적으로 채우기 어려움(최종 결측 69%)**. 실측 결과:
  FactSet 13.9만·TR 한국 org 1.5%·**GLEIF 공개 ISIN-LEI 파일엔 KR=0/TW=0건**(일본 3,607).
  KRX·TWSE가 ISIN-LEI 매핑을 GLEIF 공개본에 제공하지 않기 때문 → ISIN 경로로는 한계.
  → **한국 기업 LEI는 KRX 사내 LEI 레지스트리(KRX가 LOU)가 최상위 소스**. 이것으로
  `company_name`/종목코드 기준 결합이 현실적인 v3 경로. (해외분은 GLEIF 법인명 매칭 보조)
- **`listing_end`의 의미**: `sym_ticker_region_hist`의 end_date는 진짜 상폐뿐 아니라
  **티커/심볼 변경** 시점일 수도 있음. `is_active=False`인 행만 실제 상폐로 신뢰하고,
  정밀 상폐일이 필요하면 Compustat `dldte`(글로벌)·CRSP(미국)로 교차검증.
- **ISIN 잔여 결측 2,123건**: FactSet ISIN·CUSIP 둘 다 없는 비미국/비표준 종목.
- 정밀 IPO일이 필요하면 Compustat `ipodate`(아시아 ISIN 98% 커버) 보강 옵션 존재.

## 환경 / 실행
- 접속: 리포지토리 루트 `.env` (`WRDS_USERNAME`/`WRDS_PASSWORD`)
- v1: `python build_master.py` (KONEX 포함은 `--konex`) → `company_master.csv`
- v2: `python enrich_tr.py` → `company_master_v2.csv`
  그다음 GLEIF zip 받아서 `python enrich_gleif.py <gleif_isin_lei.zip>`
  (GLEIF 다운로드: gleif.org → ISIN-to-LEI relationship files, 무료)
