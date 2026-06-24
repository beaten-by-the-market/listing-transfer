# WRDS 주요 제품군 — 스키마별 테이블 목록·설명

- **계정**: `data01@krx.co.kr`
- **확인일**: 2026-06-24 (실제 `db.list_tables()` 호출 결과)
- **대상**: CRSP · Compustat · Capital IQ · FactSet · Refinitiv 5개 제품군의 접근 가능 스키마 25개
- **상위 문서**: [WRDS_주요제품_상세.md](WRDS_주요제품_상세.md) (제품군 개요),
  [WRDS_권한_DB목록.md](WRDS_권한_DB목록.md) (전체 권한 목록)

> 본문은 스키마별 **핵심 테이블만 추려 설명**합니다. 각 스키마의 **전체 테이블 목록**은
> 맨 아래 [부록](#부록--스키마별-전체-테이블-목록)에 접이식으로 모두 실었습니다.
> 컬럼 스키마는 `db.describe_table("<스키마>", "<테이블>")`로 확인하세요.

**WRDS 테이블 이름 규칙(공통)**
- 접두 `d`=daily(일별), `m`=monthly(월별), `q`=quarterly, `a`=annual
- 접두 `g_`=Global(국제), `wrds_`=WRDS가 가공한 편의 테이블, `r_`=reference(코드표)
- 접미 `_v2`/`_v3`=신버전, `_legacy`=구버전, `_query`=WRDS 웹쿼리용 뷰

---

## 1. CRSP

### `crsp` (433) — CRSP 통합 ✅
아래 `crsp_a_stock`·`crsp_a_indexes`·`crsp_a_treasuries`·`crsp_a_ccm`·`crsp_q_mutualfunds`가
한 스키마에 모두 들어간 통합본. 주식만 쓸 거면 `crsp_a_stock`을 봐도 동일.

**주식 시세·수익률**
| 테이블 | 설명 |
|--------|------|
| `dsf` / `msf` | 일별 / 월별 주가 파일 — `prc`(가격), `ret`(수익률), `vol`, `shrout`(주식수), `cfacpr`/`cfacshr`(조정계수) |
| `dsf_v2` / `msf_v2` | 위의 CRSP 신(v2) 포맷 버전 |
| `dsfhdr` / `msfhdr` | 종목별 시세 헤더(상장기간·첫·마지막 거래일 등) |

**종목 식별·이벤트**
| 테이블 | 설명 |
|--------|------|
| `stocknames` / `stocknames_v2` | PERMNO↔CUSIP·TICKER·종목명·거래소·SIC 이력(가장 많이 쓰는 식별 테이블) |
| `dsenames` / `msenames` | 시세이벤트 종목명 이력(거래소·share code 등) |
| `dsedelist` / `msedelist` | 상장폐지 — `dlret`(상폐수익률), `dlstcd`(사유코드) |
| `dsedist` / `msedist` | 배당·분할 등 분배 이벤트 |
| `dseexchdates` / `mseexchdates` | 거래소 코드·이전 이력 (이전상장 분석의 핵심) |
| `dseshares` | 발행주식수 변동 이력 |
| `stocknames62`, `dse62*` | NASDAQ 포함 1962년~ 시작 시계열(구 포맷) |

**지수**
| 테이블 | 설명 |
|--------|------|
| `dsi` / `msi` | CRSP 시장 종합지수(가치·동일가중) 일·월별 |
| `dsp500` / `msp500` | S&P500 지수 수익률 |
| `msp500list` | S&P500 구성종목 편입·편출 이력 |
| `dsia`/`dsib`/`dsic`/`dsio`/`dsix` | 거래소·규모별 분할 지수 시리즈 |

**국채(CRSP Treasuries 통합분)**: `tfz_dly`/`tfz_mth`(액면 시세), `tfz_mth_rf`(무위험수익률), `riskfree` 등 — 상세는 `crsp_a_treasuries` 참고.

**CCM 링크(통합분)**: `ccmxpf_lnkhist`(gvkey↔permno) 등 — 상세는 `crsp_a_ccm` 참고.

**뮤추얼펀드(통합분)**: `fund_hdr`, `monthly_returns`, `fund_fees`, `holdings` 등 — 상세는 `crsp_q_mutualfunds` 참고.

> 메모: `meta*`(메타데이터), `*_query`(웹쿼리 뷰), `saz_*`/`s6z_*`/`sfz_*`(지수 빌드용 내부 시리즈),
> `eod_*`/`esg`/`vg`(부가 데이터)는 일반 분석에서 직접 쓸 일이 적습니다.

### `crsp_a_stock` (95) — 연간 갱신 주식
`crsp` 통합본의 주식 부분만. 동일 키 테이블: `dsf`/`msf`/`dsf_v2`/`msf_v2`,
`stocknames`(+`_v2`), `dsenames`/`msenames`, `dsedelist`/`msedelist`,
`dsedist`/`msedist`, `dseexchdates`, `dseshares`, `dsi`/`msi`(시장지수).

### `crsp_a_indexes` (113) — 지수 전용
시장·규모·거래소별 지수 시리즈. `dsi*`/`msi*`(종합), `dsp500`/`msp500`(+`list`),
`dport1~9`/`mport1~5`(포트폴리오 십분위), `sfz_*`(S&P 지수 빌드), `rebal*`(리밸런싱), `cs5yr`/`cs20yr`(누적수익).

### `crsp_a_treasuries` (64) — 미국 국채
| 테이블 | 설명 |
|--------|------|
| `tfz_dly` / `tfz_mth` | 액면(issue)별 일·월별 국채 시세·수익률 |
| `tfz_mth_rf` / `tfz_dly_rf2` | 무위험수익률(1·3개월 등) 시계열 |
| `tfz_mth_ts` / `tfz_dly_ts2` | 만기수익률 기간구조(term structure) |
| `tfz_mast` / `tfz_iss` | 국채 종목 마스터·발행정보 |
| `tfz_idx` | CRSP 국채지수 |
| `riskfree` | 무위험수익률(간편본) |
| `bxyield`/`bmyield`/`fbyld` | 만기·벤치마크별 수익률 시리즈 |

### `crsp_a_ccm` (12) — CRSP/Compustat Merged 링크
| 테이블 | 설명 |
|--------|------|
| `ccmxpf_lnkhist` | **핵심 링크** — `gvkey`(Compustat)↔`lpermno`/`lpermco`(CRSP), `linktype`·`linkprim`·링크기간(`linkdt`~`linkenddt`) |
| `ccmxpf_linktable` | 링크 테이블(뷰 형태) |
| `ccmxpf_lnkused` / `ccmxpf_lnkrng` | 링크 사용·범위 보조 |
| `ccm_lookup` | gvkey↔permno 빠른 조회 |
| `comphead`/`comphist`/`compmaster`, `sechead`/`sechist` | Compustat 기업·증권 헤더·이력 |

### `crsp_q_mutualfunds` (29) — 미국 뮤추얼펀드
| 테이블 | 설명 |
|--------|------|
| `fund_hdr` / `fund_hdr_hist` | 펀드 헤더(현재·이력) — `crsp_fundno` 키 |
| `fund_names` | 펀드명 이력 |
| `monthly_returns` / `daily_returns` | 월·일별 수익률 |
| `monthly_nav` / `daily_nav` | 순자산가치(NAV) |
| `monthly_tna` / `monthly_tna_ret_nav` | 총순자산(TNA)·수익·NAV 통합 |
| `fund_fees` | 보수·비용비율 |
| `fund_style` | 스타일·투자목적 분류 |
| `holdings` / `holdings_co_info` | 보유종목 내역 |
| `front_load*` / `rear_load*` | 선취·후취 수수료 |
| `fund_flows` | 자금 유입·유출 |
| `crsp_cik_map` / `crsp_portno_map` | CIK·포트폴리오번호 매핑 |

---

## 2. Compustat

### `comp` (293) — Compustat 통합 ✅
북미·글로벌·은행·세그먼트가 한 스키마에. 북미만 쓰면 `comp_na_daily_all`로도 동일.

**재무제표(가장 중요)**
| 테이블 | 설명 |
|--------|------|
| `funda` | **연간 재무제표** — `at`·`sale`·`ni`·`ceq`·`dltt`·`ib` 등 수백 항목. 키: `gvkey`+`datadate`+`indfmt`/`datafmt`/`consol`/`popsrc` |
| `fundq` | **분기 재무제표** |
| `funda_fncd` / `fundq_fncd` | 위 항목별 각주 코드 |
| `company` | 기업 마스터 — `conm`(상호)·`sic`·`naics`·`gind`(GICS)·`loc`(국가)·`ipodate`·`cik` |
| `names` | gvkey↔티커·CUSIP·상호 |
| `co_industry` / `co_hgic` | 산업분류(SIC/NAICS, GICS 이력) |

**시세**
| 테이블 | 설명 |
|--------|------|
| `secd` | 일별 증권 시세 — `prccd`(종가)·`cshoc`(상장주식수)·`cshtrd`(거래량)·`ajexdi`(조정계수) |
| `secm` | 월별 증권 시세 |
| `security` | 증권 마스터(`iid`·`isin`·`exchg`·`tpci`) |
| `sec_dprc` / `sec_mthprc` | 일·월별 가격(대체 경로) |
| `sec_split` / `sec_divid` | 분할·배당 |
| `sec_shortint` | 공매도 잔량 |

**글로벌(`g_` 접두, 북미 외)**: `g_funda`/`g_fundq`(재무), `g_secd`/`g_secm`(시세),
`g_company`/`g_names`(기업), `g_security`, `g_sec_dprc`. 상세는 `comp_global_daily` 참고.

**은행**: `bank_funda`/`bank_fundq` 등 — 상세는 `comp_bank_daily` 참고.

**세그먼트**: `wrds_segmerged`, `seg_ann`, `seg_geo`/`seg_product`/`seg_customer` — 상세는 `comp_segments_hist_daily` 참고.

**지수·기타**: `idx_daily`/`idx_mth`(S&P 지수), `idxcst_his`(지수 구성이력), `spind`(S&P 지수),
`exrt_dly`/`exrt_mth`(환율), `wrds_ratios`(재무비율), `adsprate`(S&P 신용등급).
`r_*` 다수는 코드 해설 테이블(예: `r_giccd`=GICS 코드표, `r_siccd`=SIC 코드표).

### `comp_na_daily_all` (206) — 북미 일별
`comp`의 북미 부분. 핵심은 동일: `funda`/`fundq`, `company`/`names`, `secd`/`secm`/`security`,
`idx_*`, `seg_*`, `r_*` 코드표. 글로벌(`g_*`) 테이블은 빠져 있음.

### `comp_global_daily` (125) — 글로벌 일별
전부 `g_` 접두. `g_funda`/`g_fundq`(국제 재무제표), `g_secd`/`g_secm`(국제 시세),
`g_company`/`g_names`/`g_namesq`, `g_security`, `g_sec_dprc`, `g_idx_*`(국제 지수),
`g_exrt_dly`/`g_exrt_mth`(환율), `g_sedolgvkey`(SEDOL↔gvkey). + 공용 `r_*` 코드표.

### `comp_snapshot` / `compsnap` (125) — Point-in-Time
"발표 당시 그대로"의 스냅샷이라 백테스트 look-ahead 방지에 사용.
| 테이블 | 설명 |
|--------|------|
| `wrds_csa_pit` / `wrds_csq_pit` | **연·분기 PIT(시점고정)** 재무 — 가장 자주 쓰는 진입점 |
| `wrds_csa_unrestated` / `wrds_csq_unrestated` | 사후수정 미반영(원본) |
| `wrds_csa_restated` / `wrds_csq_restated` | 사후수정 반영 |
| `*_dc`, `*_sorted` | 동일 데이터의 datacode/정렬 변형 |
| `cscompany` / `cssecurity` | 스냅샷용 기업·증권 마스터 |
| `wrds_cs_names` | 기업명 |

> `xfc_*`/`xfl_*` 100여 개는 데이터 적재(ETL) 메타라 분석엔 불필요.

### `comp_bank_daily` (20) — 은행
`bank_funda`/`bank_fundq`(은행 특화 연·분기 재무), `bank_funda_fncd`/`bank_fundq_fncd`(각주),
`bank_names`/`bank_namesq`(기업명), `bank_afnd1`/`bank_afnd2`(원자료 항목), `bank_adesind`(항목 설명).

### `comp_segments_hist_daily` / `compseg` (14) — 사업·지역 부문
| 테이블 | 설명 |
|--------|------|
| `wrds_segmerged` | **세그먼트 통합본**(가장 편함) |
| `seg_ann` / `seg_annfund` | 연간 부문 재무 |
| `seg_geo` | 지역별 매출·자산 |
| `seg_product` | 제품·서비스별 |
| `seg_customer` | 주요 고객(매출 비중) |
| `seg_naics` | 부문 NAICS 분류 |
| `wrds_seg_geo`/`wrds_seg_product`/`wrds_seg_customer` | 위의 WRDS 정리본 |

---

## 3. Capital IQ

### `ciq` (258) — Capital IQ 통합
접두 `ciq*`=원본 테이블, `wrds_*`=WRDS 정리본(분석 진입점으로 권장), `sp*`=S&P 신용평가.

**식별·기업·증권**
| 테이블 | 설명 |
|--------|------|
| `ciqcompany` | 기업 마스터 — `companyid`(CIQ 기업 ID)·상호·상태 |
| `ciqsecurity` / `ciqtradingitem` | 증권·거래종목(`securityid`/`tradingitemid`) |
| `ciqgvkeyiid` / `wrds_gvkey` | **CIQ↔Compustat `gvkey`/`iid` 링크** |
| `ciqsymbol` / `wrds_ciqsymbol`(+`_primary`) | 티커 등 심볼 |
| `wrds_cusip` / `wrds_isin` / `wrds_cik` / `wrds_ticker` | 식별자 매핑(정리본) |
| `ciqbusinessdescription`(+`long`) | 사업 설명 |
| `ciqcompanyindustrytree` / `ciqsimpleindustry` | 산업분류 |

**M&A·자본조달(Transactions)**
| 테이블 | 설명 |
|--------|------|
| `ciqtransaction` | 딜 마스터(M&A·자금조달 공통) |
| `ciqtransma` / `wrds_transactions` | M&A 딜(원본/정리본) |
| `ciqtransoffering` / `wrds_offerings` | 증권 발행(IPO·증자·채권) |
| `wrds_trans_advisors` / `wrds_trans_considerations` / `wrds_trans_features` | 자문사·대가·조건 정리본 |

**Key Developments(기업 이벤트)**
| 테이블 | 설명 |
|--------|------|
| `ciqkeydev` / `wrds_keydev` | 실적발표·경영진 변동·M&A 등 이벤트(코드: `ciqkeydevcategorytype`) |
| `wrds_keydev_div` | 배당 관련 이벤트 |

**실적 컨퍼런스콜(Transcripts)**: `ciqtranscript`(+`component`/`person`), `wrds_transcript_detail`/`wrds_transcript_person`.

**S&P 신용평가**: `spratingdata`(등급 데이터), `spratingleveldata`, `wrds_erating`/`wrds_irating`/`wrds_srating`(엔티티·발행·증권 등급 정리본), `spassessmentdata`.

**임원 보상**: `ciqcompensation`(+`detail`), `wrds_compensation`/`wrds_compensationdetails`, `ciqperson`/`ciqprofessional`.

**재무**: `ciqfininstance`/`ciqfincollection`/`vw_fincollectiondata`(재무 컬렉션), `wrds_summary`.

### `ciq_common` (59) — 공통 식별·참조
`ciq`의 식별·참조 부분만 추린 경량 스키마. 식별 매핑에 가장 자주 쓰임:
`ciqcompany`, `ciqsecurity`, `ciqtradingitem`, `ciqgvkeyiid`, `ciqsymbol`,
`wrds_gvkey`/`wrds_cusip`/`wrds_isin`/`wrds_cik`/`wrds_ticker`/`wrds_ciqsymbol`,
`ciqexchange`, `ciqcurrency`, `ciqcountrygeo`, `ciqindex`(+`constituent`/`value`), `ciqsimpleindustry`.

### `ciq_capstrct` (43) — 자본구조
| 테이블 | 설명 |
|--------|------|
| `wrds_debt` / `wrds_equity` / `wrds_summary` | **부채·자본·요약 정리본**(권장 진입점) |
| `ciqcapstdtcomponent` / `ciqcapstdtcompntasrptddata` | 개별 부채 항목·발표값 |
| `ciqcapstdtinterestrate` / `ciqcapstdtintratetype` | 부채 금리·금리유형 |
| `ciqcapstdttype` / `ciqcapstdtsubtype` / `ciqcapstdtseniority`류 | 부채 유형·서열 코드 |
| `ciqcapsteqcomponent` / `ciqcapsteqcomponentdata` | 자본(주식) 구성 항목 |
| `ciqfininstance` / `vw_fincollectiondata` | 재무 인스턴스·컬렉션 |

---

## 4. FactSet

### `factset` (378) — FactSet 통합 ✅
크게 ① 심볼로지(`sym_*`/`h_*`/`edm_*`), ② 펀더멘털(`ff_*`), ③ 소유구조(`own_*`),
④ 시세(`*_prices_*`/`fx_*`), ⑤ 코드표(`*_map`)로 나뉨.

**심볼로지(식별 허브 — FactSet의 강점)**
| 테이블 | 설명 |
|--------|------|
| `sym_coverage` | 심볼 커버리지 마스터(`fsym_id` 중심) |
| `sym_ticker_region`(+`_hist`) / `sym_ticker_exchange` | 티커↔지역/거래소 |
| `sym_isin`(+`_hist`) / `sym_cusip`(+`_hist`) / `sym_sedol` | ISIN·CUSIP·SEDOL 매핑 |
| `sym_entity` / `sym_sec_entity` | 심볼↔엔티티(발행사) |
| `h_security_*` / `h_entity` | 식별자 이력(history) 계열 |
| `edm_standard_entity`(+`_identifiers`/`_structure`) | 표준 엔티티·지배구조 |

**펀더멘털(`ff_` — Basic/Advanced × 기간 × 권역)**
| 패턴 | 설명 |
|--------|------|
| `ff_basic_af_*` / `ff_basic_qf_*` | 기본 항목 연간(af)·분기(qf) 재무 |
| `ff_basic_ltm_*` / `ff_basic_saf_*` / `ff_basic_ytd_*` | LTM·반기·YTD |
| `ff_advanced_*` | 고급(확장) 항목 |
| `ff_*_der_*` | 파생(계산) 항목 |
| `ff_*_r_*` | restated(사후수정) |
| 접미 `_am`/`_ap`/`_eu` | 권역: 미주(Americas)·아·태(APAC)·유럽 |
| `ff_segbus_af_*` / `ff_segreg_af_*` | 사업·지역 부문 |
| `wrds_fund_af_*`/`wrds_fund_qf_*`(+`int`/`usc`) | **WRDS 정리본 펀더멘털**(권장 진입점) |

**소유구조(`own_*`)**
| 테이블 | 설명 |
|--------|------|
| `own_inst_13f_detail_eq` | 13F 기관 보유 상세 |
| `own_fund_detail_eq` | 펀드 보유 상세 |
| `own_insider_trans_eq` | 내부자 거래 |
| `own_stakes_detail_eq` | 지분(stake) 상세 |
| `own_ent_institutions` / `own_ent_funds` | 기관·펀드 마스터 |
| `wrds_own_13f` / `wrds_own_fund` | WRDS 정리본 |

**시세·환율**: `monthly_prices_final_usc_v3`/`monthly_prices_final_int_v3`(월별 가격),
`own_sec_prices_eq`(소유 모듈 가격), `fx_rates_usd`/`fx_rates_hist`(환율).

**거버넌스·주주활동(`shrk_*`)**: 주주제안·의결권·행동주의 캠페인 관련 코드·이벤트 다수(대부분 `_map` 코드표).

**코드표(`*_map`)**: `country_map`, `factset_sector_map`/`factset_industry_map`,
`iso_currency_map`, `ma_deal_type_map` 등 — 코드 해석용.

### `factset_common` (196) — 공통 심볼로지·참조
`factset`에서 시세·소유구조를 뺀 **심볼로지 + 코드표 + 펀더멘털 메타** 묶음.
식별 매핑만 필요하면 여기로 충분: `sym_*` 전체, `h_*`, `edm_*`, 각종 `*_map`,
`ff_metadata`/`ff_sec_map`/`ff_sec_coverage`, `wrds_securities`(+`_v3`).

### `factset_own` (34) — 소유구조 전용
`factset`의 `own_*` 부분만. 13F(`own_inst_13f_detail_eq`, `own_ent_13f_*`),
펀드(`own_fund_detail_eq`, `own_ent_funds`), 내부자(`own_insider_trans_eq`),
지분(`own_stakes_detail_eq`), 기관마스터(`own_ent_institutions`),
WRDS 정리본(`wrds_own_13f`/`wrds_own_fund`), MSCI 보유(`wrds_holdings_by_firm_msci` 등).

---

## 5. Refinitiv / Thomson Reuters

### `trdstrm` (82) — Datastream 통합
주식(`ds2*`)·선물(`dsfut*`)·상품(`dscm*`)·경제(`eco*`)가 한 스키마에. 개별 스키마와 동일 테이블.

**주식(`ds2*`)**
| 테이블 | 설명 |
|--------|------|
| `wrds_ds2dsf` | **WRDS 정리 일별 주식 시세**(가격·수익률·시총) — 권장 진입점 |
| `ds2primqtprc` / `ds2primqtri` | 주가격(P)·총수익지수(RI) 주가격 |
| `ds2mktval` | 시가총액 |
| `ds2numshares` | 발행주식수 |
| `ds2security` / `ds2company` | 증권·기업 마스터(`infocode`/`dscode`) |
| `ds2xref` | 식별자 교차참조 |
| `ds2div`/`ds2dps` | 배당·DPS |
| `wrds_ds_names`(+`_full`) | 종목명 정리본 |
| `ds2equityindex`/`ds2indexdata`/`wrds_ds_indexmerged` | 지수·구성종목 |

**선물(`dsfut*`)·상품(`dscm*`)·경제(`eco*`)**: 아래 개별 스키마와 동일.

### `tr_ds_equities` (43) — Datastream 주식
`trdstrm`의 주식 부분. `wrds_ds2dsf`(정리 시세), `ds2primqtprc`/`ds2primqtri`,
`ds2mktval`, `ds2numshares`, `ds2security`/`ds2company`, `ds2xref`, `ds2div`/`ds2dps`,
지수(`ds2equityindex`/`wrds_ds_indexmerged`), 종목명(`wrds_ds_names`).

### `tr_ds_fut` (20) — Datastream 선물
| 테이블 | 설명 |
|--------|------|
| `wrds_fut_contract` / `wrds_fut_series` | **WRDS 정리 선물 계약·시리즈**(권장) |
| `wrds_contract_info` / `wrds_cseries_info` | 계약·연속시리즈 정보 |
| `dsfutcontr` / `dsfutcontrval` | 개별 계약·가격값 |
| `dsfutcalcser*` | 연속(continuous) 계산 시리즈 |
| `dsfutclass`/`dsfutcode`/`dsfutdesc` | 선물 분류·코드·설명 |

### `tr_ds_comds` (11) — Datastream 상품
`wrds_cmdy_data`/`wrds_cmdy_info`(**WRDS 정리 상품 시세·정보**, 권장),
`dscmval`(가격값), `dscminfo`/`dscmitem`/`dscmcode`/`dscmdesc`(메타), `dscmloc`/`dscmreg`(지역).

### `tr_ds_econ` (8) — Datastream 경제지표
`ecodata`(지표 시계열 값), `ecoinfo`/`wrds_ecoinfo`(지표 정보), `ecocode`(코드),
`ecoclscode`/`ecoclslvlmap`(분류), `ecoattrdata`(속성), `ecolanguagedesc`(설명).

### `tr_common` (30) — 식별·마스터 공통
Datastream/SDC 공용 종목·기관·증권 매핑. `secmstrx`/`secmapx`(증권 마스터·매핑),
`vw_securitymasterx`/`vw_securitymappingx`(뷰), `perminstrinfo`/`perminstrref`(상품정보),
`permorginfo`/`permorgref`(기관), `permquoteinfo`(호가), `permisindata`/`permcusipdata`/`permsedoldata`/`permricdata`(ISIN·CUSIP·SEDOL·RIC 매핑), `tmccode`/`tmcregncntrymap`(분류·국가).

### `tr_sdc_samples` (12) — SDC Platinum + VC/PE 표본 ⚠️
이름과 달리 **표본(sample)**이며 전체 SDC 구독이 아닐 수 있음.
`deals_data`(딜), `ratings`(등급), `maturity`/`calldata`(채권 조건), `sdc_joint_ventures`(합작),
`wrds_vc_*`(벤처캐피탈 펀드·투자), `wrds_bo_*`(바이아웃/PE), `wrds_managers`(운용사).

---

## 부록 — 스키마별 전체 테이블 목록

각 스키마의 2026-06-24 기준 전체 테이블입니다(접어둠).

### CRSP

<details>
<summary><code>crsp</code> — 433개</summary>

```
acti                            asia                            asib                            asic
asio                            asix                            bmdebt                          bmheader
bmpaymts                        bmquotes                        bmyield                         bndprt06
bndprt12                        bxcalind                        bxdlyind                        bxmthind
bxquotes                        bxyield                         cap                             ccm_lookup
ccm_qvards                      ccmxpf_linktable                ccmxpf_lnkhist                  ccmxpf_lnkrng
ccmxpf_lnkused                  comphead                        comphist                        compmaster
contact_info                    core                            crsp_cik_map                    crsp_daily_data
crsp_header                     crsp_monthly_data               crsp_names                      crsp_portno_map
crsp_ziman_daily_index          crsp_ziman_monthly_index        cs20yr                          cs5yr
cs90d                           cst_hist                        daily_nav                       daily_nav_ret
daily_returns                   dividends                       dport1                          dport2
dport3                          dport4                          dport5                          dport6
dport7                          dport8                          dport9                          dsbc
dsbo                            dse                             dse62                           dse62delist
dse62dist                       dse62exchdates                  dse62names                      dse62nasdin
dse62shares                     dseall                          dseall62                        dsedelist
dsedist                         dseexchdates                    dsenames                        dsenasdin
dseshares                       dsf                             dsf62                           dsf62_v2
dsf_v2                          dsfhdr                          dsfhdr62                        dsi
dsi62                           dsia                            dsib                            dsic
dsio                            dsir                            dsix                            dsiy
dsp500                          dsp500_v2                       dsp500list                      dsp500list_v2
dsp500p                         dssc                            dsso                            eod_cap
eod_core                        eod_esg                         eod_sector                      eod_vg
erdport1                        erdport2                        erdport3                        erdport4
erdport5                        erdport6                        erdport7                        erdport8
erdport9                        ermport1                        ermport2                        ermport3
ermport4                        ermport5                        esg                             fbpri
fbyld                           front_load                      front_load_det                  front_load_grp
fund_fees                       fund_flows                      fund_hdr                        fund_hdr_hist
fund_names                      fund_style                      fund_summary                    fund_summary2
fwdask06                        fwdask12                        fwdave06                        fwdave12
fwdbid06                        fwdbid12                        hldask06                        hldask12
hldave06                        hldave12                        hldbid06                        hldbid12
holdings                        holdings_co_info                idx_const_close_pf_v2           idx_const_close_v2
idx_const_open_pf_v2            idx_const_open_proj_v2          idx_const_open_v2               idx_levels
inddlyseriesdata                inddlyseriesdata62              inddlyseriesdata_ind            index_descriptions
index_type_map                  indfamilyinfohdr                indfamilyinfohdr62              indfamilyinfohdr_ind
indissrebalancesummary_ind      indmthseriesdata                indmthseriesdata62              indmthseriesdata_ind
indsecrebalancesummary_ind      indseriesinfohdr                indseriesinfohdr62              indseriesinfohdr_ind
mbi                             mbmdat                          mbmhdr                          mbx
mbxid                           mcti                            metacalendarperiod              metacalendarperiod62
metacalendarperiod_ind          metacolumncoverage              metacolumncoverage62            metacolumncoverage_ind
metacolumninfo                  metacolumninfo62                metacolumninfo_ind              metaexchangecalendar
metaexchangecalendar62          metaexchangecalendar_ind        metafileinfo                    metafileinfo62
metafileinfo_ind                metaflagcoverage                metaflagcoverage62              metaflagcoverage_ind
metaflaginfo                    metaflaginfo62                  metaflaginfo_ind                metaflagtype
metaflagtype62                  metaflagtype_ind                metaiteminfo                    metaiteminfo62
metaiteminfo_ind                metasiztociz                    metasiztociz62                  metasiztociz_ind
mfdbname                        mhista                          mhistn                          mhistq
monthly_nav                     monthly_returns                 monthly_tna                     monthly_tna_ret_nav
mport1                          mport2                          mport3                          mport4
mport5                          mse                             mse62                           mse62delist
mse62dist                       mse62exchdates                  mse62names                      mse62nasdin
mse62shares                     mseall                          mseall62                        msedelist
msedist                         mseexchdates                    msenames                        msenasdin
mseshares                       msf                             msf62                           msf62_v2
msf_v2                          msfhdr                          msfhdr62                        msi
msi62                           msia                            msib                            msic
msio                            msir                            msix                            msiy
msp500                          msp500_v2                       msp500list                      msp500list_v2
msp500p                         portnomap                       priask06                        priask12
priave06                        priave12                        pribid06                        pribid12
price_type                      property_type                   qcti                            qsia
qsib                            qsic                            qsio                            qsix
rear_load                       rear_load_det                   rear_load_grp                   rebala
rebaln                          rebalq                          reit_type                       riskfree
s6z_agg_ann                     s6z_agg_ann_legacy              s6z_agg_mth                     s6z_agg_mth_legacy
s6z_agg_qtr                     s6z_agg_qtr_legacy              s6z_del                         s6z_del_legacy
s6z_dind                        s6z_dind_legacy                 s6z_dis                         s6z_dis_legacy
s6z_dp_dly                      s6z_dp_dly_legacy               s6z_ds_dly                      s6z_ds_dly_legacy
s6z_hdr                         s6z_hdr_legacy                  s6z_indhdr                      s6z_indhdr_legacy
s6z_mdel                        s6z_mdel_legacy                 s6z_mind                        s6z_mind_legacy
s6z_mth                         s6z_mth_legacy                  s6z_nam                         s6z_nam_legacy
s6z_ndi                         s6z_ndi_legacy                  s6z_shr                         s6z_shr_legacy
saz_agg_ann                     saz_agg_ann_legacy              saz_agg_mth                     saz_agg_mth_legacy
saz_agg_qtr                     saz_agg_qtr_legacy              saz_del                         saz_del_legacy
saz_dind                        saz_dind_legacy                 saz_dis                         saz_dis_legacy
saz_dp_dly                      saz_dp_dly_legacy               saz_ds_dly                      saz_ds_dly_legacy
saz_hdr                         saz_hdr_legacy                  saz_indhdr                      saz_indhdr_legacy
saz_mdel                        saz_mdel_legacy                 saz_mind                        saz_mind_legacy
saz_mth                         saz_mth_legacy                  saz_nam                         saz_nam_legacy
saz_ndi                         saz_ndi_legacy                  saz_shr                         saz_shr_legacy
sechead                         sechist                         sector                          sfz_dind
sfz_dind_legacy                 sfz_indhdr                      sfz_indhdr_legacy               sfz_mbr
sfz_mbr_legacy                  sfz_mind                        sfz_mind_legacy                 sfz_portd
sfz_portd_legacy                sfz_portm                       sfz_portm_legacy                sfz_rb
sfz_rb_legacy                   stkannsecuritydata              stkannsecuritydata62            stkdelists
stkdelists62                    stkdistributions                stkdistributions62              stkdlycumulativeadjfactor
stkdlycumulativeadjfactor62     stkdlysecuritydata              stkdlysecuritydata62            stkdlysecurityprimarydata
stkdlysecurityprimarydata62     stkindissuerstatistics_ind      stkindmembership_ind            stkindsecuritystatistics_ind
stkissuerinfohdr                stkissuerinfohdr62              stkissuerinfohist               stkissuerinfohist62
stkmthcumulativeadjfactor       stkmthcumulativeadjfactor62     stkmthfloatshares               stkmthfloatshares62
stkmthsecuritydata              stkmthsecuritydata62            stkqtrsecuritydata              stkqtrsecuritydata62
stksecurityinfohdr              stksecurityinfohdr62            stksecurityinfohist             stksecurityinfohist62
stkshares                       stkshares62                     stock_qvards                    stocknames
stocknames62                    stocknames62_v2                 stocknames_v2                   sub_property_type
tfz_dly                         tfz_dly_cd                      tfz_dly_cpi                     tfz_dly_ft
tfz_dly_rf2                     tfz_dly_ts2                     tfz_idx                         tfz_iss
tfz_mast                        tfz_mth                         tfz_mth_bp                      tfz_mth_cd
tfz_mth_cpi                     tfz_mth_fb                      tfz_mth_ft                      tfz_mth_rf
tfz_mth_rf2                     tfz_mth_ts                      tfz_mth_ts2                     tfz_pay
vg                              wrds_dailyindexret62_query      wrds_dailyindexret_query        wrds_dsf62v2_query
wrds_dsfv2_query                wrds_inddlytranspose_query      wrds_indmthtranspose_query      wrds_monthlyindexret62_query
wrds_monthlyindexret_query      wrds_msf62v2_query              wrds_msfv2_query                wrds_names62_query
wrds_names_query                yldask06                        yldask12                        yldave06
yldave12                        yldbid06                        yldbid12                        ziman_reit_info
zr_hdrnames
```
</details>

<details>
<summary><code>crsp_a_stock</code> — 95개</summary>

```
dse                             dseall                          dsedelist                       dsedist
dseexchdates                    dsenames                        dsenasdin                       dseshares
dsf                             dsf_v2                          dsfhdr                          dsi
dsiy                            inddlyseriesdata                indfamilyinfohdr                indmthseriesdata
indseriesinfohdr                metacalendarperiod              metacolumncoverage              metacolumninfo
metaexchangecalendar            metafileinfo                    metaflagcoverage                metaflaginfo
metaflagtype                    metaiteminfo                    metasiztociz                    mse
mseall                          msedelist                       msedist                         mseexchdates
msenames                        msenasdin                       mseshares                       msf
msf_v2                          msfhdr                          msi                             msiy
saz_agg_ann                     saz_agg_ann_legacy              saz_agg_mth                     saz_agg_mth_legacy
saz_agg_qtr                     saz_agg_qtr_legacy              saz_del                         saz_del_legacy
saz_dind                        saz_dind_legacy                 saz_dis                         saz_dis_legacy
saz_dp_dly                      saz_dp_dly_legacy               saz_ds_dly                      saz_ds_dly_legacy
saz_hdr                         saz_hdr_legacy                  saz_indhdr                      saz_indhdr_legacy
saz_mdel                        saz_mdel_legacy                 saz_mind                        saz_mind_legacy
saz_mth                         saz_mth_legacy                  saz_nam                         saz_nam_legacy
saz_ndi                         saz_ndi_legacy                  saz_shr                         saz_shr_legacy
stkannsecuritydata              stkdelists                      stkdistributions                stkdlycumulativeadjfactor
stkdlysecuritydata              stkdlysecurityprimarydata       stkissuerinfohdr                stkissuerinfohist
stkmthcumulativeadjfactor       stkmthfloatshares               stkmthsecuritydata              stkqtrsecuritydata
stksecurityinfohdr              stksecurityinfohist             stkshares                       stock_qvards
stocknames                      stocknames_v2                   wrds_dailyindexret_query        wrds_dsfv2_query
wrds_monthlyindexret_query      wrds_msfv2_query                wrds_names_query
```
</details>

<details>
<summary><code>crsp_a_indexes</code> — 113개</summary>

```
acti                            asia                            asib                            asic
asio                            asix                            cs20yr                          cs5yr
cs90d                           dport1                          dport2                          dport3
dport4                          dport5                          dport6                          dport7
dport8                          dport9                          dsbc                            dsbo
dsia                            dsib                            dsic                            dsio
dsir                            dsix                            dsiy                            dsp500
dsp500_v2                       dsp500list                      dsp500list_v2                   dsp500p
dssc                            dsso                            erdport1                        erdport2
erdport3                        erdport4                        erdport5                        erdport6
erdport7                        erdport8                        erdport9                        ermport1
ermport2                        ermport3                        ermport4                        ermport5
inddlyseriesdata_ind            indfamilyinfohdr_ind            indissrebalancesummary_ind      indmthseriesdata_ind
indsecrebalancesummary_ind      indseriesinfohdr_ind            mcti                            metacalendarperiod_ind
metacolumncoverage_ind          metacolumninfo_ind              metaexchangecalendar_ind        metafileinfo_ind
metaflagcoverage_ind            metaflaginfo_ind                metaflagtype_ind                metaiteminfo_ind
metasiztociz_ind                mhista                          mhistn                          mhistq
mport1                          mport2                          mport3                          mport4
mport5                          msia                            msib                            msic
msio                            msir                            msix                            msiy
msp500                          msp500_v2                       msp500list                      msp500list_v2
msp500p                         qcti                            qsia                            qsib
qsic                            qsio                            qsix                            rebala
rebaln                          rebalq                          sfz_dind                        sfz_dind_legacy
sfz_indhdr                      sfz_indhdr_legacy               sfz_mbr                         sfz_mbr_legacy
sfz_mind                        sfz_mind_legacy                 sfz_portd                       sfz_portd_legacy
sfz_portm                       sfz_portm_legacy                sfz_rb                          sfz_rb_legacy
stkindissuerstatistics_ind      stkindmembership_ind            stkindsecuritystatistics_ind    wrds_inddlytranspose_query
wrds_indmthtranspose_query
```
</details>

<details>
<summary><code>crsp_a_treasuries</code> — 64개</summary>

```
bmdebt                          bmheader                        bmpaymts                        bmquotes
bmyield                         bndprt06                        bndprt12                        bxcalind
bxdlyind                        bxmthind                        bxquotes                        bxyield
fbpri                           fbyld                           fwdask06                        fwdask12
fwdave06                        fwdave12                        fwdbid06                        fwdbid12
hldask06                        hldask12                        hldave06                        hldave12
hldbid06                        hldbid12                        mbi                             mbmdat
mbmhdr                          mbx                             mbxid                           priask06
priask12                        priave06                        priave12                        pribid06
pribid12                        riskfree                        tfz_dly                         tfz_dly_cd
tfz_dly_cpi                     tfz_dly_ft                      tfz_dly_rf2                     tfz_dly_ts2
tfz_idx                         tfz_iss                         tfz_mast                        tfz_mth
tfz_mth_bp                      tfz_mth_cd                      tfz_mth_cpi                     tfz_mth_fb
tfz_mth_ft                      tfz_mth_rf                      tfz_mth_rf2                     tfz_mth_ts
tfz_mth_ts2                     tfz_pay                         yldask06                        yldask12
yldave06                        yldave12                        yldbid06                        yldbid12
```
</details>

<details>
<summary><code>crsp_a_ccm</code> — 12개</summary>

```
ccm_lookup                      ccm_qvards                      ccmxpf_linktable                ccmxpf_lnkhist
ccmxpf_lnkrng                   ccmxpf_lnkused                  comphead                        comphist
compmaster                      cst_hist                        sechead                         sechist
```
</details>

<details>
<summary><code>crsp_q_mutualfunds</code> — 29개</summary>

```
contact_info                    crsp_cik_map                    crsp_portno_map                 daily_nav
daily_nav_ret                   daily_returns                   dividends                       front_load
front_load_det                  front_load_grp                  fund_fees                       fund_flows
fund_hdr                        fund_hdr_hist                   fund_names                      fund_style
fund_summary                    fund_summary2                   holdings                        holdings_co_info
mfdbname                        monthly_nav                     monthly_returns                 monthly_tna
monthly_tna_ret_nav             portnomap                       rear_load                       rear_load_det
rear_load_grp
```
</details>


### Compustat

<details>
<summary><code>comp</code> — 293개</summary>

```
aco_amda                        aco_imda                        aco_indfnta                     aco_indfntq
aco_indfntytd                   aco_indsta                      aco_indstq                      aco_indstytd
aco_notesa                      aco_notesq                      aco_notessa                     aco_notesytd
aco_pnfnda                      aco_pnfndq                      aco_pnfndytd                    aco_pnfnta
aco_pnfntq                      aco_pnfntytd                    aco_transa                      aco_transq
aco_transsa                     aco_transytd                    adsprate                        asec_amda
asec_imda                       asec_notesa                     asec_notesq                     asec_transa
asec_transq                     bank_aacctchg                   bank_adesind                    bank_afnd1
bank_afnd2                      bank_afnddc1                    bank_afnddc2                    bank_afntind
bank_funda                      bank_funda_fncd                 bank_fundq                      bank_fundq_fncd
bank_iacctchg                   bank_idesind                    bank_ifndq                      bank_ifndytd
bank_ifntq                      bank_ifntytd                    bank_names                      bank_namesq
chars                           co_aacctchg                     co_aaudit                       co_acthist
co_adesind                      co_adjfact                      co_afnd1                        co_afnd2
co_afnddc1                      co_afnddc2                      co_afntind1                     co_afntind2
co_ainvval                      co_amkt                         co_busdescl                     co_cotype
co_filedate                     co_fortune                      co_hgic                         co_iacctchg
co_iaudit                       co_idesind                      co_ifndq                        co_ifndsa
co_ifndytd                      co_ifntq                        co_ifntsa                       co_ifntytd
co_imkt                         co_industry                     co_ipcd                         co_mthly
co_offtitl                      company                         currency                        dd_group
dd_group_xref                   dd_item                         dd_package                      ecind_desc
ecind_mth                       exrt_dly                        exrt_mth                        filings
funda                           funda_fncd                      fundq                           fundq_fncd
g_chars                         g_co_aaudit                     g_co_adesind                    g_co_afnd1
g_co_afnd2                      g_co_afnddc1                    g_co_afnddc2                    g_co_afntind1
g_co_afntind2                   g_co_ainvval                    g_co_gsuppl                     g_co_hgic
g_co_iaudit                     g_co_idesind                    g_co_ifndq                      g_co_ifndsa
g_co_ifndytd                    g_co_ifntq                      g_co_ifntsa                     g_co_ifntytd
g_co_industry                   g_co_ipcd                       g_co_offtitl                    g_company
g_currency                      g_ecind_desc                    g_ecind_mth                     g_exrt_dly
g_exrt_mth                      g_funda                         g_funda_fncd                    g_fundq
g_fundq_fncd                    g_idx_daily                     g_idx_index                     g_idx_mth
g_idxcst_his                    g_indexcst_his                  g_names                         g_names_ix
g_names_ix_cst                  g_namesq                        g_sec_adesind                   g_sec_adjfact
g_sec_afnd                      g_sec_afnddc                    g_sec_afnt                      g_sec_divid
g_sec_dprc                      g_sec_dtrt                      g_sec_gmdivfn                   g_sec_gmth
g_sec_gmthdiv                   g_sec_gmthprc                   g_sec_history                   g_sec_idesind
g_sec_ifnd                      g_sec_ifnt                      g_sec_split                     g_secd
g_secm                          g_secnamesd                     g_security                      g_sedolgvkey
g_tmptable_pkg6775_tbl5551      gsecnamesm                      idx_ann                         idx_anndes
idx_daily                       idx_index                       idx_mth                         idx_qrt
idx_qrtdes                      idxcst_his                      indexcst_his                    io_qaggregate
io_qbuysell                     io_qchanges                     io_qfloatadj                    io_qholders
it_mbuysell                     it_msummary                     it_r_rltn                       names
names_aco_indsta                names_aco_indstq                names_aco_pnfnda                names_aco_pnfndq
names_adsprate                  names_ix                        names_ix_cst                    names_seg
namesd                          namesm                          namesq                          r_accstd
r_acqmeth                       r_auditors                      r_auopic                        r_balpres
r_cf_formt                      r_co_status                     r_coindpre                      r_compstat
r_consol                        r_country                       r_cstclscd                      r_datacode
r_datafmt                       r_divtaxmarker                  r_docsrce                       r_ex_codes
r_exchgtier                     r_exrt_typ                      r_fndfntcd                      r_footnts
r_foricd                        r_giccd                         r_hcalendr                      r_idxclscd
r_inactvcd                      r_incstats                      r_indfmt                        r_indsec
r_invval                        r_issuetyp                      r_majidxcl                      r_mic_codes
r_naiccd                        r_notetype                      r_ntsubtype                     r_offcrso
r_ogmethod                      r_opinions                      r_prc_stat                      r_qsrcdoc
r_sec_stat                      r_secannfn                      r_sectors                       r_siccd
r_spiicd                        r_spmicd                        r_statalrt                      r_states
r_stko                          r_titles                        r_updates                       sec_adesind
sec_adjfact                     sec_afnd                        sec_afnddc                      sec_afnt
sec_divid                       sec_dprc                        sec_dtrt                        sec_history
sec_idcurrent                   sec_idesind                     sec_idhist                      sec_ifnd
sec_ifnt                        sec_mdivfn                      sec_mshare                      sec_msptfn
sec_mth                         sec_mthdiv                      sec_mthprc                      sec_mthspt
sec_mthtrt                      sec_shortint                    sec_shortint_legacy             sec_spind
sec_split                       secd                            secm                            security
sedolgvkey                      seg_ann                         seg_annfund                     seg_customer
seg_geo                         seg_naics                       seg_product                     seg_type
spidx_cst                       spind                           spind_dly                       spind_mth
wrds_g_exrate                   wrds_idx_cst_current            wrds_ratios                     wrds_seg_customer
wrds_seg_geo                    wrds_seg_product                wrds_segmerged                  xfl_column
xfl_table
```
</details>

<details>
<summary><code>comp_na_daily_all</code> — 206개</summary>

```
aco_amda                        aco_imda                        aco_indfnta                     aco_indfntq
aco_indfntytd                   aco_indsta                      aco_indstq                      aco_indstytd
aco_notesa                      aco_notesq                      aco_notessa                     aco_notesytd
aco_pnfnda                      aco_pnfndq                      aco_pnfndytd                    aco_pnfnta
aco_pnfntq                      aco_pnfntytd                    aco_transa                      aco_transq
aco_transsa                     aco_transytd                    adsprate                        asec_amda
asec_imda                       asec_notesa                     asec_notesq                     asec_transa
asec_transq                     chars                           co_aacctchg                     co_aaudit
co_acthist                      co_adesind                      co_adjfact                      co_afnd1
co_afnd2                        co_afnddc1                      co_afnddc2                      co_afntind1
co_afntind2                     co_ainvval                      co_amkt                         co_busdescl
co_cotype                       co_filedate                     co_fortune                      co_hgic
co_iacctchg                     co_iaudit                       co_idesind                      co_ifndq
co_ifndsa                       co_ifndytd                      co_ifntq                        co_ifntsa
co_ifntytd                      co_imkt                         co_industry                     co_ipcd
co_mthly                        co_offtitl                      company                         currency
dd_group                        dd_group_xref                   dd_item                         dd_package
ecind_desc                      ecind_mth                       exrt_dly                        exrt_mth
funda                           funda_fncd                      fundq                           fundq_fncd
idx_ann                         idx_anndes                      idx_daily                       idx_index
idx_mth                         idx_qrt                         idx_qrtdes                      idxcst_his
indexcst_his                    io_qaggregate                   io_qbuysell                     io_qchanges
io_qfloatadj                    io_qholders                     it_mbuysell                     it_msummary
it_r_rltn                       names                           names_aco_indsta                names_aco_indstq
names_aco_pnfnda                names_aco_pnfndq                names_adsprate                  names_ix
names_ix_cst                    names_seg                       namesd                          namesm
namesq                          r_accstd                        r_acqmeth                       r_auditors
r_auopic                        r_balpres                       r_cf_formt                      r_co_status
r_coindpre                      r_compstat                      r_consol                        r_country
r_cstclscd                      r_datacode                      r_datafmt                       r_divtaxmarker
r_docsrce                       r_ex_codes                      r_exchgtier                     r_exrt_typ
r_fndfntcd                      r_footnts                       r_foricd                        r_giccd
r_hcalendr                      r_idxclscd                      r_inactvcd                      r_incstats
r_indfmt                        r_indsec                        r_invval                        r_issuetyp
r_majidxcl                      r_mic_codes                     r_naiccd                        r_notetype
r_ntsubtype                     r_offcrso                       r_ogmethod                      r_opinions
r_prc_stat                      r_qsrcdoc                       r_sec_stat                      r_secannfn
r_sectors                       r_siccd                         r_spiicd                        r_spmicd
r_statalrt                      r_states                        r_stko                          r_titles
r_updates                       sec_adesind                     sec_adjfact                     sec_afnd
sec_afnddc                      sec_afnt                        sec_divid                       sec_dprc
sec_dtrt                        sec_history                     sec_idcurrent                   sec_idesind
sec_idhist                      sec_ifnd                        sec_ifnt                        sec_mdivfn
sec_mshare                      sec_msptfn                      sec_mth                         sec_mthdiv
sec_mthprc                      sec_mthspt                      sec_mthtrt                      sec_shortint
sec_shortint_legacy             sec_spind                       sec_split                       secd
secm                            security                        sedolgvkey                      seg_ann
seg_annfund                     seg_customer                    seg_geo                         seg_naics
seg_product                     seg_type                        spidx_cst                       spind
spind_dly                       spind_mth                       wrds_idx_cst_current            wrds_ratios
wrds_seg_customer               wrds_seg_geo                    wrds_seg_product                wrds_segmerged
xfl_column                      xfl_table
```
</details>

<details>
<summary><code>comp_global_daily</code> — 125개</summary>

```
dd_group                        dd_group_xref                   dd_item                         dd_package
g_chars                         g_co_aaudit                     g_co_adesind                    g_co_afnd1
g_co_afnd2                      g_co_afnddc1                    g_co_afnddc2                    g_co_afntind1
g_co_afntind2                   g_co_ainvval                    g_co_gsuppl                     g_co_hgic
g_co_iaudit                     g_co_idesind                    g_co_ifndq                      g_co_ifndsa
g_co_ifndytd                    g_co_ifntq                      g_co_ifntsa                     g_co_ifntytd
g_co_industry                   g_co_ipcd                       g_co_offtitl                    g_company
g_currency                      g_ecind_desc                    g_ecind_mth                     g_exrt_dly
g_exrt_mth                      g_funda                         g_funda_fncd                    g_fundq
g_fundq_fncd                    g_idx_daily                     g_idx_index                     g_idx_mth
g_idxcst_his                    g_indexcst_his                  g_names                         g_names_ix
g_names_ix_cst                  g_namesq                        g_sec_adesind                   g_sec_adjfact
g_sec_afnd                      g_sec_afnddc                    g_sec_afnt                      g_sec_divid
g_sec_dprc                      g_sec_dtrt                      g_sec_gmdivfn                   g_sec_gmth
g_sec_gmthdiv                   g_sec_gmthprc                   g_sec_history                   g_sec_idesind
g_sec_ifnd                      g_sec_ifnt                      g_sec_split                     g_secd
g_secm                          g_secnamesd                     g_security                      g_sedolgvkey
g_tmptable_pkg6775_tbl5551      gsecnamesm                      r_accstd                        r_acqmeth
r_auditors                      r_auopic                        r_balpres                       r_cf_formt
r_co_status                     r_coindpre                      r_compstat                      r_consol
r_country                       r_cstclscd                      r_datacode                      r_datafmt
r_divtaxmarker                  r_docsrce                       r_ex_codes                      r_exchgtier
r_exrt_typ                      r_fndfntcd                      r_footnts                       r_foricd
r_giccd                         r_hcalendr                      r_idxclscd                      r_inactvcd
r_incstats                      r_indfmt                        r_indsec                        r_invval
r_issuetyp                      r_majidxcl                      r_mic_codes                     r_naiccd
r_notetype                      r_ntsubtype                     r_offcrso                       r_ogmethod
r_opinions                      r_prc_stat                      r_qsrcdoc                       r_sec_stat
r_secannfn                      r_sectors                       r_siccd                         r_spiicd
r_spmicd                        r_statalrt                      r_states                        r_stko
r_titles                        r_updates                       wrds_g_exrate                   xfl_column
xfl_table
```
</details>

<details>
<summary><code>comp_snapshot</code> — 125개</summary>

```
chars                           cs_items                        csco_aaudit                     csco_afnd
csco_afntind                    csco_ainvval                    csco_akey                       csco_atxt
csco_iaudit                     csco_ifndq                      csco_ifndytd                    csco_ifntq
csco_ifntytd                    csco_ikey                       csco_ipcd                       csco_itxt
cscompany                       cssecurity                      dd_group                        dd_group_xref
dd_item                         dd_package                      r_actioncd                      sec_idhist
wrds_cs_names                   wrds_csa_pit                    wrds_csa_pit_dc                 wrds_csa_pit_dc_sorted
wrds_csa_pit_sorted             wrds_csa_restated               wrds_csa_restated_dc            wrds_csa_unrestated
wrds_csa_unrestated_dc          wrds_csq_pit                    wrds_csq_pit_dc                 wrds_csq_pit_dc_sorted
wrds_csq_pit_sorted             wrds_csq_restated               wrds_csq_restated_dc            wrds_csq_unrestated
wrds_csq_unrestated_dc          xfc_actionstartconditiontype    xfc_actionstatetype             xfc_actiontype
xfc_activitytype                xfc_changeflagtype              xfc_cleanuptype                 xfc_column
xfc_columntodatabasetype        xfc_columnusetype               xfc_databasetype                xfc_datetimeformattype
xfc_datetimetodatabasetype      xfc_daynotinfeedfrequency       xfc_delimitertype               xfc_emailaccounttype
xfc_errormessage                xfc_failuretype                 xfc_feedfrequencytype           xfc_feedpop
xfc_hosttype                    xfc_indextype                   xfc_lengthsemantictype          xfc_loaderobjecttype
xfc_loadersetting               xfc_loaderver                   xfc_loadjobtype                 xfc_loadsubstatetype
xfc_loadsubtype                 xfc_notificationtype            xfc_pac                         xfc_pacgroup
xfc_pacsource                   xfc_pacsourcetohost             xfc_pacsourcetype               xfc_pacver
xfc_pacverfeedpoptopacsrchost   xfc_pacverfeedpoptotableinst    xfc_pacverfeedpoptozipfile      xfc_pacverfeedpopupgrade
xfc_pacverrelationship          xfc_pacvertofeedpop             xfc_phasetype                   xfc_prepostloadsql
xfc_prepostloadtype             xfc_progresstype                xfc_proxyprotocoltype           xfc_relationshiptype
xfc_resulttype                  xfc_table                       xfc_tableinst                   xfc_tableinstindex
xfc_tableinstindexcolumn        xfc_tableinsttocolumn           xfc_tabletype                   xfc_textfile
xfc_textfilecolumnmapping       xfc_textfiletype                xfc_upgradeabstraction          xfc_upgradetable
xfc_upgradetablesql             xfc_upgradetype                 xfc_validationtype              xfc_zipfile
xfc_zipfiletotextfile           xfc_zipfiletype                 xfc_zipruntype                  xfl_column
xfl_datagroup                   xfl_datagroup_table             xfl_db_version                  xfl_file_datagroup
xfl_filelayout                  xfl_lrm_cstat_fsup0             xfl_lrm_cstat_fsup0_2           xfl_lrm_cstat_rsup0
xfl_lrm_cstat_tsup0             xfl_lrm_user_load_plan          xfl_mapping                     xfl_package
xfl_package_file                xfl_package_rel                 xfl_refer                       xfl_sequence
xfl_table
```
</details>

<details>
<summary><code>comp_bank_daily</code> — 20개</summary>

```
bank_aacctchg                   bank_adesind                    bank_afnd1                      bank_afnd2
bank_afnddc1                    bank_afnddc2                    bank_afntind                    bank_funda
bank_funda_fncd                 bank_fundq                      bank_fundq_fncd                 bank_iacctchg
bank_idesind                    bank_ifndq                      bank_ifndytd                    bank_ifntq
bank_ifntytd                    bank_names                      bank_namesq                     chars
```
</details>

<details>
<summary><code>comp_segments_hist_daily</code> — 14개</summary>

```
names_seg                       seg_ann                         seg_annfund                     seg_customer
seg_geo                         seg_naics                       seg_product                     seg_type
wrds_seg_customer               wrds_seg_geo                    wrds_seg_product                wrds_segmerged
xfl_column                      xfl_table
```
</details>


### Capital IQ

<details>
<summary><code>ciq</code> — 258개</summary>

```
chars                           ciqaddress                      ciqaddresstype                  ciqbusinessdescription
ciqbusinessdescriptionlong      ciqcapstdtasrptdclasstype       ciqcapstdtclasstype             ciqcapstdtcompntasrptddata
ciqcapstdtcomponent             ciqcapstdtconvertibletype       ciqcapstdtcumulativetype        ciqcapstdtdescription
ciqcapstdtintbenchmarktype      ciqcapstdtinterestrate          ciqcapstdtintratetype           ciqcapstdtleveltype
ciqcapstdtnonrecoursetype       ciqcapstdtparticipatingtype     ciqcapstdtredeemabletype        ciqcapstdtsecuredtype
ciqcapstdtsubtype               ciqcapstdttype                  ciqcapsteqauthrzdsharestype     ciqcapsteqcomponent
ciqcapsteqcomponentdata         ciqcapsteqconvertibletype       ciqcapsteqsubtype               ciqcapsteqtype
ciqcapsteqvotingrightstype      ciqchartype                     ciqchartypetosubtype            ciqcommittee
ciqcompany                      ciqcompanyindustrytree          ciqcompanyrel                   ciqcompanyreltype
ciqcompanystatustype            ciqcompanytype                  ciqcompensation                 ciqcompensationadjustment
ciqcompensationadjustmenttype   ciqcompensationdetail           ciqcompensationsubtype          ciqcompensationtype
ciqconstituent                  ciqcountrygeo                   ciqcurrency                     ciqdataitem
ciqdataitemgroup                ciqdataitemgrouptodataitem      ciqdataitemtransaction          ciqexchange
ciqexchangerate                 ciqfinancialdataset             ciqfincollection                ciqfindatacollectiontype
ciqfininstance                  ciqfininstancedate              ciqfininstancetocollection      ciqfininstancetocollecttype
ciqfininstancetype              ciqfinperiod                    ciqfinstatementrestatetype      ciqfinunittype
ciqgvkeyiid                     ciqindex                        ciqindexconstituent             ciqindexprovider
ciqindexrel                     ciqindextradingitem             ciqindextradingitemtype         ciqindexvalue
ciqindustrytosic                ciqkeydev                       ciqkeydevcategorytype           ciqkeydevobjectroletype
ciqkeydevsplitinfo              ciqkeydevtimezone               ciqkeydevtoobjecttoeventtype    ciqkeydevtosourcetype
ciqobjecttype                   ciqperiodtype                   ciqperson                       ciqpersonbiography
ciqprofessional                 ciqprofessionalcoverage         ciqprofunction                  ciqprotoprofunction
ciqreportingtemplatetype        ciqrestatementtype              ciqsecurity                     ciqsecuritygroup
ciqsecuritysubtype              ciqsecuritytype                 ciqsimpleindustry               ciqsourcetype
ciqstate                        ciqsubtype                      ciqsymbol                       ciqsymboltype
ciqtradingitem                  ciqtradingitemstatus            ciqtransaccountingmethod        ciqtransaction
ciqtransactionadvisortype       ciqtransactionconditiontype     ciqtransactioncontrolstake      ciqtransactiondealapproach
ciqtransactiondealattitude      ciqtransactionfeetype           ciqtransactionmergerevent       ciqtransactionmergereventtype
ciqtransactionreltype           ciqtransactionstaketype         ciqtransactionstatustype        ciqtransactiontoadvisor
ciqtransactiontocompanyrel      ciqtransactiontocompreltype     ciqtransactiontype              ciqtransactionuseofproceeds
ciqtranscompanyreltype          ciqtransconsiddetailscenario    ciqtransconsidstatustype        ciqtransconsidsubtype
ciqtransconsidtype              ciqtranscript                   ciqtranscriptcollectiontype     ciqtranscriptcomponent
ciqtranscriptcomponenttype      ciqtranscriptdelayreason        ciqtranscriptdelayreasontype    ciqtranscriptperson
ciqtranscriptpresentationtype   ciqtranscriptspeakertype        ciqtransdataitemmapping         ciqtransfeatures
ciqtransma                      ciqtransmaadvisor               ciqtransmacompanyrel            ciqtransmaconsiddetail
ciqtransmaconsideration         ciqtransmadatabit               ciqtransmadatadate              ciqtransmadatafinancial
ciqtransmadatainteger           ciqtransmadatanumeric           ciqtransmadatavarchar           ciqtransmadoctomergerevent
ciqtransmadocuments             ciqtransmastatustodate          ciqtransmatocondition           ciqtransmatoprimaryfeature
ciqtransmatotransfeature        ciqtransofferdatafinancial      ciqtransoffering                ciqtransofferingdatabit
ciqtransofferingdatadate        ciqtransofferingdatainteger     ciqtransofferingdatanumeric     ciqtransofferingdatavarchar
ciqtransofferingdocuments       ciqtransofferingfee             ciqtransofferinglockup          ciqtransofferingregistration
ciqtransofferingrel             ciqtransofferingstatustodate    ciqtransofferingtoadvisor       ciqtransofferingtoseller
ciqtransoffersecuritydetail     ciqtransoffertoprimaryfeat      ciqtransoffertotransfeature     ciqtransoffertouseofproceeds
ciqtransprimaryfeaturetype      ciqtranssecuritysubtype         ciqtranssecuritytype            ciqtransvaluationtype
ciqvaluetype                    companyrels                     companyreltype                  compensation_length
datesource                      ratings_ids                     reasonforchange                 sourcetype
spassessmentdata                spassessmentleveldata           spassessmenttype                spentityleveldata
spentitysector                  spentitysectorcode              spindustrychar                  spindustrytype
spinstrumentleveldata           spinstrumentsector              spinstrumentsectorcode          spinstrumenttoentity
spratinganalystcode             spratingcollateraltype          spratingcountry                 spratingcoupontype
spratingcurrencytype            spratingdata                    spratingdataitemtype            spratingdebttype
spratingidentifier              spratingidentifiertype          spratinginstrumenttype          spratingleveldata
spratingnaicscode               spratingorgdebttype             spratingprogramtype             spratingpvtplacementtype
spratingregion                  spratingroletype                spratingsiccode                 spratingstate
spratingtype                    spsecurityleveldata             staketype                       vw_fincollectiondata
vw_summary_fincollectiondata    wrds_cik                        wrds_ciqsymbol                  wrds_ciqsymbol_primary
wrds_compensation               wrds_compensationdetails        wrds_consideration_financials   wrds_cusip
wrds_debt                       wrds_eassessment                wrds_entity_info                wrds_equity
wrds_erating                    wrds_gvkey                      wrds_inst_info                  wrds_irating
wrds_isin                       wrds_keydev                     wrds_keydev_div                 wrds_offerings
wrds_offerings_advisors         wrds_offerings_feat             wrds_offerings_proceeds         wrds_offerings_registration
wrds_offerings_rel              wrds_professional               wrds_sassessment                wrds_sec_info
wrds_srating                    wrds_summary                    wrds_ticker                     wrds_trans_advisors
wrds_trans_conditions           wrds_trans_considerations       wrds_trans_features             wrds_transactions
wrds_transcript_detail          wrds_transcript_person
```
</details>

<details>
<summary><code>ciq_common</code> — 59개</summary>

```
chars                           ciqaddress                      ciqaddresstype                  ciqbusinessdescription
ciqbusinessdescriptionlong      ciqchartype                     ciqchartypetosubtype            ciqcommittee
ciqcompany                      ciqcompanyindustrytree          ciqcompanyrel                   ciqcompanyreltype
ciqcompanystatustype            ciqcompanytype                  ciqconstituent                  ciqcountrygeo
ciqcurrency                     ciqdataitem                     ciqdataitemtransaction          ciqexchange
ciqexchangerate                 ciqgvkeyiid                     ciqindex                        ciqindexconstituent
ciqindexprovider                ciqindexrel                     ciqindextradingitem             ciqindextradingitemtype
ciqindexvalue                   ciqindustrytosic                ciqobjecttype                   ciqperiodtype
ciqreportingtemplatetype        ciqrestatementtype              ciqsecurity                     ciqsecuritygroup
ciqsecuritysubtype              ciqsecuritytype                 ciqsimpleindustry               ciqstate
ciqsubtype                      ciqsymbol                       ciqsymboltype                   ciqtradingitem
ciqtradingitemstatus            ciqvaluetype                    companyrels                     companyreltype
datesource                      reasonforchange                 sourcetype                      staketype
wrds_cik                        wrds_ciqsymbol                  wrds_ciqsymbol_primary          wrds_cusip
wrds_gvkey                      wrds_isin                       wrds_ticker
```
</details>

<details>
<summary><code>ciq_capstrct</code> — 43개</summary>

```
ciqcapstdtasrptdclasstype       ciqcapstdtclasstype             ciqcapstdtcompntasrptddata      ciqcapstdtcomponent
ciqcapstdtconvertibletype       ciqcapstdtcumulativetype        ciqcapstdtdescription           ciqcapstdtintbenchmarktype
ciqcapstdtinterestrate          ciqcapstdtintratetype           ciqcapstdtleveltype             ciqcapstdtnonrecoursetype
ciqcapstdtparticipatingtype     ciqcapstdtredeemabletype        ciqcapstdtsecuredtype           ciqcapstdtsubtype
ciqcapstdttype                  ciqcapsteqauthrzdsharestype     ciqcapsteqcomponent             ciqcapsteqcomponentdata
ciqcapsteqconvertibletype       ciqcapsteqsubtype               ciqcapsteqtype                  ciqcapsteqvotingrightstype
ciqdataitem                     ciqdataitemgroup                ciqdataitemgrouptodataitem      ciqfinancialdataset
ciqfincollection                ciqfindatacollectiontype        ciqfininstance                  ciqfininstancedate
ciqfininstancetocollection      ciqfininstancetocollecttype     ciqfininstancetype              ciqfinperiod
ciqfinstatementrestatetype      ciqfinunittype                  vw_fincollectiondata            vw_summary_fincollectiondata
wrds_debt                       wrds_equity                     wrds_summary
```
</details>


### FactSet

<details>
<summary><code>factset</code> — 378개</summary>

```
affiliate_type_map              asset_class_map                 audit_type_map                  ca_div_freq_qual_map
ca_div_type_map                 ca_event_type_map               ce_audio_source_map             ce_event_type_map
ce_fiscal_period_map            ce_market_time_map              cic_classification_map          country_coord_map
country_map                     cs3_monthly_prices_final_int    cs3_monthly_prices_final_usc    dcs_category_map
dcs_coupon_map                  dcs_debt_map                    dcs_fiscal_year_map             dcs_reporting_period_map
dcs_seniority_map               dcs_summary_map                 econ_category_map               econ_concept_map
econ_country_inclusion          econ_event_type_map             econ_frequency_map              econ_importance_ind_map
econ_indicator_map              econ_region_map                 econ_source_map                 econ_subcategory_map
econ_unit_amounts_map           edm_standard_address            edm_standard_entity             edm_standard_entity_identifiers
edm_standard_entity_naics_rank  edm_standard_entity_structure   ekey_category_map               ekey_source_map
ekey_subcategory_map            entity_profile_type_map         entity_relation_type_map        entity_status_map
entity_sub_type_map             entity_type_map                 etf_fund_category_map           etf_fund_focus_map
etf_fund_niche_map              etf_geo_exposure_map            etf_legal_struct_map            etf_select_crit_map
etf_strategy_map                etf_weight_scheme_map           factset_industry_map            factset_sector_map
fe_actualflag_map               fe_cmtsubid_map                 fe_item                         fe_item_map
fe_revisionflag_map             ff_accounting_standard_map      ff_advanced_af_am               ff_advanced_af_ap
ff_advanced_af_eu               ff_advanced_der_af_am           ff_advanced_der_af_ap           ff_advanced_der_af_eu
ff_advanced_der_ltm_am          ff_advanced_der_ltm_ap          ff_advanced_der_ltm_eu          ff_advanced_der_qf_am
ff_advanced_der_qf_ap           ff_advanced_der_qf_eu           ff_advanced_der_r_af_am         ff_advanced_der_r_af_ap
ff_advanced_der_r_af_eu         ff_advanced_der_r_ltm_am        ff_advanced_der_r_ltm_ap        ff_advanced_der_r_ltm_eu
ff_advanced_der_r_qf_am         ff_advanced_der_r_qf_ap         ff_advanced_der_r_qf_eu         ff_advanced_der_r_saf_am
ff_advanced_der_r_saf_ap        ff_advanced_der_r_saf_eu        ff_advanced_der_r_ytd_am        ff_advanced_der_r_ytd_ap
ff_advanced_der_r_ytd_eu        ff_advanced_der_saf_am          ff_advanced_der_saf_ap          ff_advanced_der_saf_eu
ff_advanced_der_ytd_am          ff_advanced_der_ytd_ap          ff_advanced_der_ytd_eu          ff_advanced_ltm_am
ff_advanced_ltm_ap              ff_advanced_ltm_eu              ff_advanced_qf_am               ff_advanced_qf_ap
ff_advanced_qf_eu               ff_advanced_r_af_am             ff_advanced_r_af_ap             ff_advanced_r_af_eu
ff_advanced_r_ltm_am            ff_advanced_r_ltm_ap            ff_advanced_r_ltm_eu            ff_advanced_r_qf_am
ff_advanced_r_qf_ap             ff_advanced_r_qf_eu             ff_advanced_r_saf_am            ff_advanced_r_saf_ap
ff_advanced_r_saf_eu            ff_advanced_r_ytd_am            ff_advanced_r_ytd_ap            ff_advanced_r_ytd_eu
ff_advanced_saf_am              ff_advanced_saf_ap              ff_advanced_saf_eu              ff_advanced_ytd_am
ff_advanced_ytd_ap              ff_advanced_ytd_eu              ff_auditor_opinion_map          ff_auditors_int
ff_balance_model                ff_balance_model_ind            ff_balance_model_rpt_map        ff_basic_af_am
ff_basic_af_ap                  ff_basic_af_eu                  ff_basic_cf_am                  ff_basic_cf_ap
ff_basic_cf_eu                  ff_basic_der_af_am              ff_basic_der_af_ap              ff_basic_der_af_eu
ff_basic_der_ltm_am             ff_basic_der_ltm_ap             ff_basic_der_ltm_eu             ff_basic_der_qf_am
ff_basic_der_qf_ap              ff_basic_der_qf_eu              ff_basic_der_r_af_am            ff_basic_der_r_af_ap
ff_basic_der_r_af_eu            ff_basic_der_r_ltm_am           ff_basic_der_r_ltm_ap           ff_basic_der_r_ltm_eu
ff_basic_der_r_qf_am            ff_basic_der_r_qf_ap            ff_basic_der_r_qf_eu            ff_basic_der_r_saf_am
ff_basic_der_r_saf_ap           ff_basic_der_r_saf_eu           ff_basic_der_r_ytd_am           ff_basic_der_r_ytd_ap
ff_basic_der_r_ytd_eu           ff_basic_der_saf_am             ff_basic_der_saf_ap             ff_basic_der_saf_eu
ff_basic_der_ytd_am             ff_basic_der_ytd_ap             ff_basic_der_ytd_eu             ff_basic_ltm_am
ff_basic_ltm_ap                 ff_basic_ltm_eu                 ff_basic_qf_am                  ff_basic_qf_ap
ff_basic_qf_eu                  ff_basic_r_af_am                ff_basic_r_af_ap                ff_basic_r_af_eu
ff_basic_r_ltm_am               ff_basic_r_ltm_ap               ff_basic_r_ltm_eu               ff_basic_r_qf_am
ff_basic_r_qf_ap                ff_basic_r_qf_eu                ff_basic_r_saf_am               ff_basic_r_saf_ap
ff_basic_r_saf_eu               ff_basic_r_ytd_am               ff_basic_r_ytd_ap               ff_basic_r_ytd_eu
ff_basic_saf_am                 ff_basic_saf_ap                 ff_basic_saf_eu                 ff_basic_ytd_am
ff_basic_ytd_ap                 ff_basic_ytd_eu                 ff_entity_profiles              ff_financial_stmt_map
ff_fp_ind_map                   ff_gen_ind_map                  ff_metadata                     ff_report_freq_map
ff_sec_coverage                 ff_sec_entity                   ff_sec_entity_hist              ff_sec_map
ff_sec_map_int                  ff_sec_map_usc                  ff_segbus_af_am                 ff_segbus_af_ap
ff_segbus_af_eu                 ff_segreg_af_am                 ff_segreg_af_ap                 ff_segreg_af_eu
ff_stitch_af                    ff_stitch_ltm                   ff_stitch_qf                    ff_stitch_saf
fp_div_ngflag_map               fp_div_tax_marker_map           fp_div_type_map                 fp_sec_type_map
fref_sec_exchange_map           fref_security_type_map          frequency_map                   fund_type_map
fut_unit_map                    fx_rates_hist                   fx_rates_usd                    generic_holding_id_map
generic_id_map                  h_entity                        h_entity_sector                 h_security_cusip
h_security_cusip_hist           h_security_isin                 h_security_sedol                h_security_sedol_hist
h_security_ticker_exchange      h_security_ticker_region        hier_product_type_map           hts_code_map
insider_tran_map                invt_obj_asset_type_map         invt_obj_map                    invt_obj_specialization_map
iso_currency_map                issue_type_map                  list_map                        ma_acq_purpose_map
ma_closing_status_map           ma_company_role_map             ma_deal_attitude_map            ma_deal_type_map
ma_profession_role_map          ma_profession_type_map          ma_term_change_types_map        metro_map
mic_exchange_map                monthly_prices_final_int_v3     monthly_prices_final_usc_v3     nace_classification_map
naics6_map                      own_ent_13f_combined_inst       own_ent_13f_filing_hist         own_ent_13f_subfiler_inst
own_ent_address                 own_ent_coverage                own_ent_fund_filing_hist        own_ent_fund_identifiers
own_ent_fund_managers           own_ent_fund_objectives         own_ent_funds                   own_ent_funds_feeder_master
own_ent_inst_identifiers        own_ent_inst_profiles           own_ent_institutions            own_fund_detail_eq
own_fund_generic_eq             own_fund_generic_summary_fi     own_insider_trans_eq            own_inst_13f_detail_eq
own_inst_stakes_detail_eq       own_sec_13f_reportable_eq       own_sec_adr_ord_ratio_eq        own_sec_coverage_eq
own_sec_entity_eq               own_sec_entity_hist_eq          own_sec_map_eq                  own_sec_prices_eq
own_stakes_detail_eq            own_uksr_cust_detail_eq         own_uksr_detail_eq              pe_event_id_map
pe_fund_status_map              pe_fund_type_map                pe_instrument_map               pe_security_categories_map
pe_transaction_map              period_type_map                 ppl_asset_type_map              ppl_board_committee_map
ppl_bus_map                     ppl_job_function_map            ppl_region_map                  ppl_special_area_map
rbics_structure_l2_curr         ref_metadata_codes              ref_metadata_fields             ref_metadata_packages
ref_metadata_tables             region_map                      relationship_type_map           resolution_map
sc_ship_unit_map                shrk_advisor_type_map           shrk_amendment_type_map         shrk_anr_event_map
shrk_ca_activism_map            shrk_ca_activist_map            shrk_ca_defense_map             shrk_campaign_status_map
shrk_campaign_type_map          shrk_cg_amendment_type_map      shrk_cg_source_map              shrk_election_source_map
shrk_frq_rec_map                shrk_gov_obj_map                shrk_meeting_type_map           shrk_pill_status_map
shrk_pill_type_map              shrk_pill_version_type_map      shrk_proposal_cat_map           shrk_proposal_sub_map
shrk_proposal_type_map          shrk_recommend_type_map         shrk_source_type_map            shrk_special_exhibit_map
shrk_value_obj_map              shrk_vote_pass_map              shrk_vote_req_map               shrk_winner_map
sic_map                         source_map                      state_prov_coord_map            state_province_map
sym_address                     sym_coverage                    sym_cusip                       sym_cusip_hist
sym_entity                      sym_entity_sector               sym_entity_sector_rbics         sym_isin
sym_isin_hist                   sym_legacy_perm_id              sym_people                      sym_region
sym_sec_entity                  sym_sedol                       sym_ticker_exchange             sym_ticker_exchange_hist
sym_ticker_region               sym_ticker_region_hist          sym_xc_isin                     unit_amount_map
wrds_ffheader_int_v3            wrds_ffheader_usc_v3            wrds_fund_af_int_v3             wrds_fund_af_usc_v3
wrds_fund_ltm_int_v3            wrds_fund_ltm_usc_v3            wrds_fund_qf_int_v3             wrds_fund_qf_usc_v3
wrds_fund_r_af_int_v3           wrds_fund_r_af_usc_v3           wrds_fund_saf_int_v3            wrds_fund_saf_usc_v3
wrds_holdings_by_firm_msci      wrds_holdings_by_security_msci  wrds_own_13f                    wrds_own_fund
wrds_securities                 wrds_securities_v3
```
</details>

<details>
<summary><code>factset_common</code> — 196개</summary>

```
affiliate_type_map              asset_class_map                 audit_type_map                  ca_div_freq_qual_map
ca_div_type_map                 ca_event_type_map               ce_audio_source_map             ce_event_type_map
ce_fiscal_period_map            ce_market_time_map              cic_classification_map          country_coord_map
country_map                     dcs_category_map                dcs_coupon_map                  dcs_debt_map
dcs_fiscal_year_map             dcs_reporting_period_map        dcs_seniority_map               dcs_summary_map
econ_category_map               econ_concept_map                econ_country_inclusion          econ_event_type_map
econ_frequency_map              econ_importance_ind_map         econ_indicator_map              econ_region_map
econ_source_map                 econ_subcategory_map            econ_unit_amounts_map           edm_standard_address
edm_standard_entity             edm_standard_entity_identifiers  edm_standard_entity_naics_rank  edm_standard_entity_structure
ekey_category_map               ekey_source_map                 ekey_subcategory_map            entity_profile_type_map
entity_relation_type_map        entity_status_map               entity_sub_type_map             entity_type_map
etf_fund_category_map           etf_fund_focus_map              etf_fund_niche_map              etf_geo_exposure_map
etf_legal_struct_map            etf_select_crit_map             etf_strategy_map                etf_weight_scheme_map
factset_industry_map            factset_sector_map              fe_actualflag_map               fe_cmtsubid_map
fe_item                         fe_item_map                     fe_revisionflag_map             ff_accounting_standard_map
ff_auditor_opinion_map          ff_balance_model                ff_balance_model_ind            ff_balance_model_rpt_map
ff_entity_profiles              ff_financial_stmt_map           ff_fp_ind_map                   ff_gen_ind_map
ff_metadata                     ff_report_freq_map              ff_sec_coverage                 ff_sec_entity
ff_sec_entity_hist              ff_sec_map                      ff_stitch_af                    ff_stitch_ltm
ff_stitch_qf                    ff_stitch_saf                   fp_div_ngflag_map               fp_div_tax_marker_map
fp_div_type_map                 fp_sec_type_map                 fref_sec_exchange_map           fref_security_type_map
frequency_map                   fund_type_map                   fut_unit_map                    fx_rates_hist
fx_rates_usd                    generic_holding_id_map          generic_id_map                  h_entity
h_entity_sector                 h_security_cusip                h_security_cusip_hist           h_security_isin
h_security_sedol                h_security_sedol_hist           h_security_ticker_exchange      h_security_ticker_region
hier_product_type_map           hts_code_map                    insider_tran_map                invt_obj_asset_type_map
invt_obj_map                    invt_obj_specialization_map     iso_currency_map                issue_type_map
list_map                        ma_acq_purpose_map              ma_closing_status_map           ma_company_role_map
ma_deal_attitude_map            ma_deal_type_map                ma_profession_role_map          ma_profession_type_map
ma_term_change_types_map        metro_map                       mic_exchange_map                nace_classification_map
naics6_map                      pe_event_id_map                 pe_fund_status_map              pe_fund_type_map
pe_instrument_map               pe_security_categories_map      pe_transaction_map              period_type_map
ppl_asset_type_map              ppl_board_committee_map         ppl_bus_map                     ppl_job_function_map
ppl_region_map                  ppl_special_area_map            rbics_structure_l2_curr         ref_metadata_codes
ref_metadata_fields             ref_metadata_packages           ref_metadata_tables             region_map
relationship_type_map           resolution_map                  sc_ship_unit_map                shrk_advisor_type_map
shrk_amendment_type_map         shrk_anr_event_map              shrk_ca_activism_map            shrk_ca_activist_map
shrk_ca_defense_map             shrk_campaign_status_map        shrk_campaign_type_map          shrk_cg_amendment_type_map
shrk_cg_source_map              shrk_election_source_map        shrk_frq_rec_map                shrk_gov_obj_map
shrk_meeting_type_map           shrk_pill_status_map            shrk_pill_type_map              shrk_pill_version_type_map
shrk_proposal_cat_map           shrk_proposal_sub_map           shrk_proposal_type_map          shrk_recommend_type_map
shrk_source_type_map            shrk_special_exhibit_map        shrk_value_obj_map              shrk_vote_pass_map
shrk_vote_req_map               shrk_winner_map                 sic_map                         source_map
state_prov_coord_map            state_province_map              sym_address                     sym_coverage
sym_cusip                       sym_cusip_hist                  sym_entity                      sym_entity_sector
sym_entity_sector_rbics         sym_isin                        sym_isin_hist                   sym_legacy_perm_id
sym_people                      sym_region                      sym_sec_entity                  sym_sedol
sym_ticker_exchange             sym_ticker_exchange_hist        sym_ticker_region               sym_ticker_region_hist
sym_xc_isin                     unit_amount_map                 wrds_securities                 wrds_securities_v3
```
</details>

<details>
<summary><code>factset_own</code> — 34개</summary>

```
own_ent_13f_combined_inst       own_ent_13f_filing_hist         own_ent_13f_subfiler_inst       own_ent_address
own_ent_coverage                own_ent_fund_filing_hist        own_ent_fund_identifiers        own_ent_fund_managers
own_ent_fund_objectives         own_ent_funds                   own_ent_funds_feeder_master     own_ent_inst_identifiers
own_ent_inst_profiles           own_ent_institutions            own_fund_detail_eq              own_fund_generic_eq
own_fund_generic_summary_fi     own_insider_trans_eq            own_inst_13f_detail_eq          own_inst_stakes_detail_eq
own_sec_13f_reportable_eq       own_sec_adr_ord_ratio_eq        own_sec_coverage_eq             own_sec_entity_eq
own_sec_entity_hist_eq          own_sec_map_eq                  own_sec_prices_eq               own_stakes_detail_eq
own_uksr_cust_detail_eq         own_uksr_detail_eq              wrds_holdings_by_firm_msci      wrds_holdings_by_security_msci
wrds_own_13f                    wrds_own_fund
```
</details>


### Refinitiv / Thomson Reuters

<details>
<summary><code>trdstrm</code> — 82개</summary>

```
ds2adj                          ds2capevent                     ds2company                      ds2constdatadly
ds2constdatamth                 ds2constdly                     ds2constmth                     ds2ctryqtinfo
ds2cusipchg                     ds2datatype                     ds2div                          ds2dps
ds2equityindex                  ds2exchange                     ds2exchqtinfo                   ds2fxcode
ds2fxrate                       ds2indexaddldata                ds2indexdata                    ds2indexdatatype
ds2indexlist                    ds2isinchg                      ds2localcodechg                 ds2mktval
ds2mnemchg                      ds2numshares                    ds2primexchqtchg                ds2primqtprc
ds2primqtri                     ds2qtnamechg                    ds2region                       ds2scdqtprc
ds2scdqtri                      ds2security                     ds2sedolchg                     ds2sharehldgs
ds2xref                         dscmcode                        dscmdesc                        dscmextval
dscminfo                        dscmitem                        dscmlicflagcode                 dscmloc
dscmreg                         dscmval                         dsfutcalcserextval              dsfutcalcserinfo
dsfutcalcsermth                 dsfutcalcserval                 dsfutclass                      dsfutcode
dsfutcontr                      dsfutcontrchg                   dsfutcontrextval                dsfutcontrinfo
dsfutcontrval                   dsfutcotrepval                  dsfutdesc                       dsfutitem
dsfuttrdcycle                   dsfutundrmap                    ecoattrdata                     ecoclscode
ecoclslvlmap                    ecocode                         ecodata                         ecoinfo
ecolanguagedesc                 wrds_cmdy_data                  wrds_cmdy_info                  wrds_contract_info
wrds_cseries_info               wrds_ds2dsf                     wrds_ds_indexconstmerged_dly    wrds_ds_indexconstmerged_mth
wrds_ds_indexmerged             wrds_ds_names                   wrds_ds_names_full              wrds_ecoinfo
wrds_fut_contract               wrds_fut_series
```
</details>

<details>
<summary><code>tr_ds_equities</code> — 43개</summary>

```
ds2adj                          ds2capevent                     ds2company                      ds2constdatadly
ds2constdatamth                 ds2constdly                     ds2constmth                     ds2ctryqtinfo
ds2cusipchg                     ds2datatype                     ds2div                          ds2dps
ds2equityindex                  ds2exchange                     ds2exchqtinfo                   ds2fxcode
ds2fxrate                       ds2indexaddldata                ds2indexdata                    ds2indexdatatype
ds2indexlist                    ds2isinchg                      ds2localcodechg                 ds2mktval
ds2mnemchg                      ds2numshares                    ds2primexchqtchg                ds2primqtprc
ds2primqtri                     ds2qtnamechg                    ds2region                       ds2scdqtprc
ds2scdqtri                      ds2security                     ds2sedolchg                     ds2sharehldgs
ds2xref                         wrds_ds2dsf                     wrds_ds_indexconstmerged_dly    wrds_ds_indexconstmerged_mth
wrds_ds_indexmerged             wrds_ds_names                   wrds_ds_names_full
```
</details>

<details>
<summary><code>tr_ds_fut</code> — 20개</summary>

```
dsfutcalcserextval              dsfutcalcserinfo                dsfutcalcsermth                 dsfutcalcserval
dsfutclass                      dsfutcode                       dsfutcontr                      dsfutcontrchg
dsfutcontrextval                dsfutcontrinfo                  dsfutcontrval                   dsfutcotrepval
dsfutdesc                       dsfutitem                       dsfuttrdcycle                   dsfutundrmap
wrds_contract_info              wrds_cseries_info               wrds_fut_contract               wrds_fut_series
```
</details>

<details>
<summary><code>tr_ds_comds</code> — 11개</summary>

```
dscmcode                        dscmdesc                        dscmextval                      dscminfo
dscmitem                        dscmlicflagcode                 dscmloc                         dscmreg
dscmval                         wrds_cmdy_data                  wrds_cmdy_info
```
</details>

<details>
<summary><code>tr_ds_econ</code> — 8개</summary>

```
ecoattrdata                     ecoclscode                      ecoclslvlmap                    ecocode
ecodata                         ecoinfo                         ecolanguagedesc                 wrds_ecoinfo
```
</details>

<details>
<summary><code>tr_common</code> — 30개</summary>

```
gsecmapx                        gsecmstrx                       gsecsdlchg                      permcincusipdata
permcode                        permcusipdata                   perminstrinfo                   perminstrref
permisindata                    permorginfo                     permorgref                      permquoteinfo
permquoteref                    permricdata                     permsecmapx                     permsedoldata
prcisr                          sddates_v                       sdexchinfo_v                    sdinfo_v
seccspchgx                      secmapx                         secmstrx                        secsdl2chgx
secsdlchgx                      secventype                      tmccode                         tmcregncntrymap
vw_securitymappingx             vw_securitymasterx
```
</details>

<details>
<summary><code>tr_sdc_samples</code> — 12개</summary>

```
calldata                        deals_data                      maturity                        ratings
sdc_joint_ventures              wrds_bo_fund_firm               wrds_bo_fundra_fund             wrds_bo_invdtl_compn_fund
wrds_managers                   wrds_vc_fund_firm               wrds_vc_fundra_fund             wrds_vc_invdtl_compn_fund
```
</details>

