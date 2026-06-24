# WRDS 접근 권한 DB(라이브러리) 목록

- **계정**: `data01@krx.co.kr`
- **확인일**: 2026-06-24
- **확인 방법**: `wrds.Connection.list_libraries()` + `information_schema.tables` 테이블 수 집계
  (재현 스크립트: [list_wrds_access.py](list_wrds_access.py))

## 요약

`list_libraries()`가 돌려준 **접근 가능한 스키마는 총 243개**입니다. 단, 이 안에는 두 종류가 섞여 있습니다.

| 구분 | 개수 | 의미 |
|------|------|------|
| **구독(전체 접근)** | 111 | 우리 기관이 구독해서 전체 데이터를 조회할 수 있는 라이브러리 |
| **샘플·트라이얼** | 132 | 모든 WRDS 회원에게 공통 제공되는 제한된 표본(`*samp`, `*smp`, `*sample`, `*trial`) |

> ⚠️ **주의**: 목록에 보이고 테이블 정의가 있어도, 실제 `SELECT` 시 권한이 거부되는
> 하위 스키마가 있을 수 있습니다. 예) `risk`(거버넌스)는 조회 시
> `permission denied for schema risk_govern` 발생. 목록 = "보인다"이지 "모두 조회된다"가
> 항상 보장되는 것은 아니므로, 실제 사용 전 대표 테이블 1행 조회로 확인을 권장합니다.
>
> ✅ 실데이터 조회로 직접 검증한 라이브러리: `crsp`, `comp`, `factset`, `contrib_global_factor`.

---

## 구독(전체 접근) 라이브러리 — 제품군별

괄호 안은 스키마별 테이블 수.

### CRSP (주가·지수·뮤추얼펀드) — 이 프로젝트의 주력
- `crsp` (433), `crsp_a_stock` (95), `crsp_a_indexes` (113), `crsp_a_treasuries` (64)
- `crsp_a_ccm` (12, CRSP/Compustat 링크), `crsp_q_mutualfunds` (29)

### Compustat (S&P, 재무제표)
- `comp` (293), `comp_na_daily_all` (206), `comp_global_daily` (125)
- `comp_snapshot` (125) / `compsnap` (125), `comp_bank_daily` (20)
- `comp_segments_hist_daily` (14) / `compseg` (14)

### Capital IQ (S&P)
- `ciq` (258), `ciq_common` (59), `ciq_capstrct` (43)

### FactSet
- `factset` (378), `factset_common` (196), `factset_own` (34, 소유구조)

### Audit Analytics (감사·지배구조·소송)
- `audit` (388), `audit_corp_legal` (86), `audit_audit_comp` (59), `audit_common` (2)

### Thomson Reuters / Refinitiv (Datastream·SDC 등)
- `trdstrm` (82, Datastream), `tr_ds_equities` (43), `tr_ds_fut` (20), `tr_ds_comds` (11), `tr_ds_econ` (8)
- `tr_common` (30) / `trcommon` (30), `tr_sdc_samples` (12)

### 채권 (TRACE / MSRB)
- `trace` (32), `trace_standard` (23), `trace_enhanced` (14)
- `msrb` (3) / `msrb_all` (3)

### 옵션·거래소
- `cboe` (90), `cboe_all` (1), `phlx` (2) / `phlx_all` (2), `otc` (1) / `otc_endofday` (1)

### 지배구조·의결권 (ISS)
- `iss_va_vote_us` (3), `iss_va_vote_global` (3), `iss_va_shareholder` (3)
- `risk` (26) ⚠️조회 권한 일부 제한, `risk_proposals` (3)

### Bank (규제·재무)
- `bank` (43), `bank_all` (21)

### Fama-French 팩터
- `ff` (12) / `ff_all` (12)

### 거시·경제 지표
- `macrofin` (24), `macrofin_comm_trade` (24), `frb` (4) / `frb_all` (4)
- `doe` (2) / `doe_all` (2), `pwt` (7) / `pwt_all` (7, Penn World Table)

### 기타 상용 데이터
- `block` (3) / `block_all` (3), `djones` (2) / `djones_all` (2)
- `dmef` (4) / `dmef_all` (4), `iri` (15) / `iri_all` (15)
- `calcbnch` (26, Calcbench), `mscicoms` (3, MSCI)
- `fjc` (7), `fjc_litigation` (4), `fjc_linking` (3) — 연방법원 소송

### WRDS Contributed (학계 기여 데이터셋)
- `contrib` (47), `contrib_general` (20), `contrib_as_filed_financials` (5)
- `contrib_global_factor` (4), `contrib_kpss` (2), `contrib_intangible_value` (2)
- `contrib_corp_fed_litigation` (2), `contrib_bond_firm_link` (1), `contrib_char_returns` (1)
- `contrib_corporate_culture` (1), `contrib_liva` (1)

### WRDS Applications (가공·링크 테이블)
- `wrdsapps` (71)
- 링크: `wrdsapps_link_crsp_taq`, `wrdsapps_link_crsp_bond`, `wrdsapps_link_crsp_factset`,
  `wrdsapps_link_comp_eushort`, `wrdsapps_link_supplychain`
- 이벤트 스터디: `wrdsapps_evtstudy_us`, `wrdsapps_evtstudy_int`, `wrdsapps_evtstudy_int_ginsight`, `wrdsapps_evtstudy_lr`
- 재무비율: `wrdsapps_finratio`, `wrdsapps_finratio_ccm`
- 기타: `wrdsapps_patents` (3), `wrdsapps_subsidiary` (2), `wrdsapps_windices` (3),
  `wrdsapps_backtest_basic`, `wrdsapps_backtest_plus`, `wrdsapps_eushort`
- `wrdssec_midas` (1)

### 시스템·공용
- `public` (13) / `public_all` (11), `columnar` (5), `gutenberg` (1)
- `totalq` (1) / `totalq_all` (1), `rq_all` (1), `midas` (1)

---

## 샘플·트라이얼 라이브러리 (132개, 참고)

모든 WRDS 회원이 공통으로 접근하는 제한 표본이라 "우리 기관 구독"과는 무관합니다.
대표 예: `crspsamp`, `compsamp`, `taqsamp`, `ciqsamp`, `mrktsamp`(Markit), `optionmsamp_us`(OptionMetrics),
`boardex_trial`, `bvd_orbis_trial`, `ravenpack_trial`, `revelio_samp`, `zacksamp` 등.

전체 목록은 [list_wrds_access.py](list_wrds_access.py) 실행으로 확인할 수 있습니다.

---

## 직접 확인하는 법

```bash
python list_wrds_access.py
```

특정 라이브러리의 테이블 목록:

```python
from exchange_transfers import connect
db = connect()
db.list_tables(library="crsp")   # 예: crsp 안의 테이블들
db.describe_table("crsp", "stocknames")  # 컬럼 스키마
db.close()
```
