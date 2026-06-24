# id_identify — 글로벌 상장 "회사" 마스터 (원천별 3-버전)

2011년 이후 **NYSE · Nasdaq · JPX(도쿄) · KRX · TWSE**에 (보통주 기준) 상장 상태였던
**회사(법인)** 를 거래소별 레코드로 추출하고, 회사 기준 공통식별자(ISIN=메인 보통주 /
CUSIP / 티커 / LEI)와 상장·상폐 일자(상폐 포함)를 붙인다.

## 왜 3-버전인가

같은 목표를 **서로 다른 원천 DB에서 독립적으로** 구축해, 모집단·식별자·일자를
상호대조(reconciliation)하기 위함. 각 폴더는 **독립적인 시작점**이다(서로 보강 아님).

| 폴더 | 원천(시작점) | 회사 키 | 강점 | 약점 |
|---|---|---|---|---|
| [factset/](factset/) | **FactSet** | `factset_entity_id` | 식별자·entity 모델, LEI 일부, RIC(보강) | 아시아 LEI 희소 |
| [compustat/](compustat/) | **Compustat (NA+Global)** | `gvkey` | 명시적 IPO/상폐일, 아시아 ISIN 98% | LEI 없음, 티커 약함 |
| [tr/](tr/) | **Refinitiv/TR** | `orgpermid`(또는 seccode) | RIC·SEDOL·org 모델, 일부 LEI | 거래소/일자 매핑 난도 |

> **공통 산출물 규약**: 각 폴더는 `build_master.py` → `company_master.csv`를 만들고,
> 가능한 한 동일 스키마(컬럼)를 따른다 → 버전 간 비교가 쉽도록.

## 공통 스코프 (확정)

- **거래소 5종**: NYSE, Nasdaq, JPX(도쿄/TSE), KRX(KOSPI+KOSDAQ), TWSE.
- **보통주만**(우선주/ETF/펀드/REIT/예탁증서 제외), **본국 보통주 상장만**(ADR/교차상장 제외).
- **회사(법인) 기준** — 회사×거래소 1행(같은 회사가 2개 거래소면 2행).
- **2011-01-01 이후 한 번이라도 상장 상태**(이전 상장+이후 상폐 포함). 상폐 회사 포함.
- 식별자: 티커 · 메인 보통주 ISIN · LEI · CUSIP (+RIC/SEDOL 가능 시).

## 검증 스팟체크(공통)
삼성전자 `KR7005930003`(KRX) · SK하이닉스 `KR7000660001` · 토요타 `JP3633400001`(JPX)
· TSMC `TW0002330008`(TWSE) · Apple `US0378331005`(Nasdaq, NYSE 아님).
상장중 회사 수 대략: KRX ~2,600 · TWSE ~1,000 · JPX ~3,900 · NYSE ~1,700–2,400 · Nasdaq ~3,200.

## 환경
- 접속: 리포지토리 루트 `.env` (`WRDS_USERNAME`/`WRDS_PASSWORD`)
- 각 폴더에서 `python build_master.py` 실행.
