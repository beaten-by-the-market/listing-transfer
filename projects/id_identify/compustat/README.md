# Compustat (S&P) — 글로벌 상장 "회사" 마스터

3-버전(FactSet / **Compustat** / Refinitiv-TR) 중 **Compustat 단독 원천** 버전.
`build_master.py` → `company_master.csv` 를 생성한다.

## 목표 / 스코프

- 거래소 5종: **NYSE, Nasdaq, JPX(도쿄/TSE), KRX(KOSPI+KOSDAQ), TWSE**.
- **2011-01-01 이후 한 번이라도 상장 상태**였던 **회사(법인 = GVKEY)**.
  - 2011 이전 상장이라도 이후까지 활성/상폐면 포함, 2011 이전에 상폐된 회사는 제외.
  - 필터: `costat='A'` (활성) **OR** `dldte >= '2011-01-01'` (2011 이후 상폐).
- **보통주만**(`tpci='0'` = Common or ordinary). 우선주/ETF/펀드/REIT/예탁증서(ADR) 제외.
- **본국 보통주(primary) 상장만**. ADR·교차상장 제외.
- 회사 × 거래소 1행(같은 회사가 2개 거래소면 2행).

## 검증된 방법 / 스키마 사실

- GVKEY는 NA·Global 두 유니버스에 걸쳐 유일. 한 회사는 한 유니버스에만 존재.
  - 미국(NYSE/Nasdaq): `comp.company` + `comp.security`
  - 아시아(KRX/JPX/TWSE): `comp.g_company` + `comp.g_security`
- **Primary 보통주 1행** 추출: 회사의 primary issue IID를 security에 조인.
  - 미국: `company.priusa = security.iid`
  - 아시아: `g_company.prirow = g_security.iid`
  - 검증: primary 조인 결과 gvkey당 보통주 row가 정확히 1개(팬아웃 없음).
- 거래소 코드(`comp.r_ex_codes`): 11=NYSE, 14=Nasdaq, 248=KRX(KOSPI),
  298=KRX(KOSDAQ), 260=TWSE, 264=TSE, 293=TSE(JASDAQ).
- 발행유형(`comp.r_issuetyp`): **`tpci='0'` = Common or ordinary** (확인).
- `ipodate`=상장(IPO)일, `dldte`=상폐일, `costat`='A'(활성)/'I'(비활성) — 모두 DATE/문자.

## 식별자 처리

| 컬럼 | 출처 / 비고 |
|---|---|
| `main_isin` | 아시아: Compustat Global ISIN(커버리지 ~98–99%). 미국: `security.isin` 우선, 없으면 **CUSIP에서 파생**(`isin_source='cusip_derived'`). |
| `main_cusip` | 미국 ~100%. Compustat Global(아시아)에는 CUSIP 없음(0%). |
| `main_ticker`| `security.tic`. 미국 강함, 아시아 약함/비어있음. |
| `sedol` | security 테이블(아시아 커버리지 좋음). |
| `lei` | **Compustat에 LEI 없음 → 항상 공란**(알려진 갭, 날조하지 않음). |

US/CA ISIN 파생: `"US"/"CA" + CUSIP(9) + 체크디지트`. 유효한 9자리 [0-9A-Z] CUSIP에 한함.

## 결과 (실행 시점)

총 **18,394행 / 고유 GVKEY 18,393** (1개 회사가 Nasdaq·JPX 동시 상장 → 2행).

| 거래소 | rows | 고유 GVKEY | 활성 | 상폐 |
|---|---:|---:|---:|---:|
| NYSE | 3,084 | 3,084 | 1,751 | 1,333 |
| Nasdaq | 5,815 | 5,815 | 3,216 | 2,599 |
| KRX (KOSPI+KOSDAQ) | 3,312 | 3,312 | 2,645 | 667 |
| JPX(TSE) | 5,034 | 5,034 | 3,926 | 1,108 |
| TWSE | 1,149 | 1,149 | 1,089 | 60 |

**식별자 채움률**: main_isin 99.4% · sedol 98.1% · main_cusip 48.4%(미국만) ·
main_ticker 48.4%(미국 위주) · lei 0%(원천 부재).
ISIN 출처: compustat 18,043 · cusip_derived 246 · 없음 105.

**스팟체크 전부 통과**: 삼성전자 `KR7005930003`(KRX, prirow=02W) ·
SK하이닉스 `KR7000660001`(KRX) · 토요타 `JP3633400001`(JPX) ·
TSMC `TW0002330008`(TWSE) · Apple `US0378331005`(Nasdaq).

활성 회사 수는 모두 기대치 범위 내(KRX ~2,600, TWSE ~1,000, JPX ~3,900,
NYSE 1,700–2,400, Nasdaq ~3,200).

## 주의 / 캐비엣

- **LEI 없음**: Compustat은 LEI를 제공하지 않음 → `lei` 컬럼 전부 공란. 교차대조 시
  LEI는 FactSet/TR 버전 또는 GLEIF로 보강해야 함.
- **미국 ISIN은 일부 CUSIP 파생**: `comp.security.isin`이 비어있는 미국 종목은
  CUSIP→ISIN 체크디지트로 생성(`isin_source='cusip_derived'`, 246행). 미국 58행은
  CUSIP 부재/무효로 ISIN 미생성.
- **아시아 CUSIP 없음**: Compustat Global은 아시아 보통주 CUSIP을 제공하지 않음.
- **티커 약함**: 아시아 `tic`가 대부분 비어 있음(거래소 코드/SEDOL/ISIN으로 매칭 권장).
- **JASDAQ(293)**: 2013년 도쿄증권거래소 통합으로 해당 코드의 활성 종목 0,
  전부 JPX(TSE)/XTKS로 매핑됨.
- **KOSPI(248)+KOSDAQ(298)**를 단일 `KRX`/`XKRX` 레이블로 통합. 동일 회사가 두 시장
  primary 보통주를 동시 보유하는 경우는 사실상 없음(primary 조인이 1행 보장).
- **회사 기준 행**: primary issue 기준이므로 우선주·복수 보통주 종목은 1개 대표 보통주로
  축약됨(예: 삼성전자는 prirow가 보통주 02W를 가리켜 우선주 01W 제외).

## 실행

```bash
# 루트 .env 의 WRDS_USERNAME / WRDS_PASSWORD 사용
PYTHONIOENCODING=utf-8 python build_master.py </dev/null 2>&1
```
출력: `company_master.csv` (UTF-8-SIG) + 콘솔 요약(거래소별 수·채움률·스팟체크).
