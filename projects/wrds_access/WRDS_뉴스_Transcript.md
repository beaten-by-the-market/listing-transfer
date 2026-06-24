# WRDS 뉴스·Transcript 데이터 접근 검증

- **계정**: `data01@krx.co.kr`
- **확인일**: 2026-06-25
- **확인 방법**: `list_libraries()`(카탈로그 가시성) + `information_schema.tables`(테이블명 검색)
  + 대표 테이블 `SELECT ... LIMIT 1`(실제 권한). 재현 스크립트: [check_news_transcript.py](check_news_transcript.py)
- **상위 문서**: [WRDS_권한_DB목록.md](WRDS_권한_DB목록.md), [WRDS_주요제품_상세.md](WRDS_주요제품_상세.md)

## 결론 (한 줄)

**본 기관 구독으로 실제 조회 가능한 뉴스·transcript 데이터는 사실상 0개.**
카탈로그(`list_libraries`)에는 이름이 보여도 실제 `SELECT` 시 대부분
`permission denied for schema ...`로 거부됩니다. **샘플·트라이얼만 열립니다.**

> ⚠️ 핵심 함정: `list_libraries()` 결과는 "보인다"이지 "조회된다"가 아닙니다.
> 특히 transcript 본문은 `ciq` 카탈로그에 나열되지만 물리적으로는 `ciq_transcripts`
> 스키마에 있고 **그 스키마 조회 권한이 없습니다.** 기존 [WRDS_권한_DB목록.md](WRDS_권한_DB목록.md)가
> `ciq`를 "구독(전체 접근)"으로 분류한 것과 별개로, transcript 부분은 미구독입니다.

---

## 1. Transcript (실적 컨퍼런스콜)

| 데이터 | 스키마 | 카탈로그 | 실제 SELECT |
|--------|--------|:------:|:----------:|
| S&P Capital IQ Events Transcripts | `ciq` / `ciq_transcripts` / `ciq_transcripts_old` | 보임 | ❌ 거부 (`permission denied for schema ciq_transcripts`) |
| 〃 **샘플** | `ciqsamp_transcripts` | 보임 | ✅ 가능 (소표본) |

**샘플(`ciqsamp_transcripts`) 내용** — 맛보기 수준:
- `wrds_transcript_detail` — **20행** (컬럼: `companyid`, `keydevid`, `transcriptid`, `headline`, `mostimportantdateutc` …). 본문 헤드라인·메타.
- `wrds_transcript_person` — 2,089행 (발언자·컴포넌트 단위).

> 전체 transcript 본문(발언 텍스트)은 미구독. 분석용 전수 데이터 불가.

---

## 2. News (뉴스·텍스트·ESG 인시던트)

| 데이터 | 본 구독 스키마 | 실제 SELECT | 샘플/트라이얼 | 비고 |
|--------|---------------|:----------:|--------------|------|
| **RavenPack** (Dow Jones·PR·Web 뉴스 분석/감성) | `ravenpack_full` `ravenpack_dj` `ravenpack_pr` `ravenpack_web` `ravenpack_common` | ❌ 거부 | `ravenpack_trial` ✅ | 트라이얼에 `rpa_full_equities` 40.9만행, `rpa_full_global_macro` 177만행 — 탐색용으론 충분 |
| **LexisNexis Metabase** (뉴스 기사 원문) | `lexisnexis_metabase` (`article_vw`) | ❌ 거부 | 없음 | — |
| **RepRisk** (ESG 뉴스·리스크 인시던트) | `reprisk` `reprisk_pm` `reprisk_std` | ❌ 거부 | `reprisk_sample` ✅ | 샘플 `pm_news_data` 69행 등 소표본 |
| **Compustat ComputexT** (글로벌/US 텍스트 문서) | (full 미확인) | — | `compsamp_computext` ✅ | 샘플이 큼: US **218만행**, Global 60만행 |
| **PitchBook** 뉴스 릴레이션 | `pitchbk_*` (`companynewsrelation` 등) | ❌ 거부 | — | — |
| **Revelio Labs** 감성 | `revelio` / `revelio_sentiment` | ❌ 거부 | `revelio_samp` ✅ | *금융 뉴스 아님* — 직원 리뷰/노동시장 감성 |
| **WRDS NLP Sentiment** | `wrds_nlpsa` | ❌ 없음 | — | 라이브러리 자체 미존재 |
| Dow Jones (`djones`) | `djones` (`djdaily`/`djmonthly`) | ✅ 가능 | — | **뉴스 아님** — 다우 '지수' 시세일 뿐 (오인 주의) |

---

## 3. 접근 가능한 샘플·트라이얼 상세 (참고)

모든 WRDS 회원 공통 제공분이라 "우리 기관 구독"과 무관하지만, 구조 파악·프로토타이핑엔 유용.

| 스키마 | 대표 테이블 (행수) | 성격 |
|--------|-------------------|------|
| `ravenpack_trial` | `rpa_full_global_macro`(177만) · `rpa_full_equities`(40.9만) · `wrds_rpa_company_names`(31.6만) | 뉴스 이벤트·감성 스코어 + 엔티티 매핑 |
| `compsamp_computext` | `computext_us`(218만) · `computext_global`(60.3만) | 기업 텍스트 문서(ISIN/CUSIP/gvkey 키) |
| `reprisk_sample` | `v2_risk_incidents`(177) · `pm_news_data`(69) · `v2_metrics`(465) | ESG 리스크 인시던트·RRI 스코어 |
| `ciqsamp_transcripts` | `wrds_transcript_person`(2,089) · `wrds_transcript_detail`(20) | 컨퍼런스콜 헤드라인·발언자 |
| `revelio_samp` | `sentiment_individual_reviews`(9.7만) 등 | 직원 리뷰 감성(금융뉴스 아님) |

---

## 4. 실사용하려면

위 뉴스·transcript 모듈(RavenPack, S&P CIQ Transcripts, LexisNexis Metabase, RepRisk 등)은
**기관 차원의 구독 추가가 필요**합니다. 현재 권한으로는 본문/스코어 전수 데이터를 받을 수 없습니다.

## 재현 방법

```bash
python check_news_transcript.py
```

출력의 `DENY ... permission denied`가 미구독, `OK`가 조회 가능을 뜻합니다.
