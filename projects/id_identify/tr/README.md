# id_identify #3 — TR(Refinitiv/Thomson Reuters) 버전

원천 독립 3-버전 중 **Refinitiv/TR (`tr_common`)** 단독. 회사 grain = PermID org(`orgpermid`).

## 경로 (검증)
- 모집단: `permquoteref`(exchcode, isprimary, status) + `permquoteinfo`(category='ORD'=보통주)
  + `perminstrref`(instrument→org). **isprimary='1'** 인 보통주 대표상장만.
- 거래소 매핑(exchcode): NYSE=`NYS` · **Nasdaq=`NSM`/`NMS`/`NAS`/`NAQ`** · KRX=`KSC`(KOSPI)+`KOE`(KOSDAQ)
  · JPX=`TYO` · TWSE=`TAI`. (KONEX `KNX`·대만 TPEx `TWO` 제외)
  - ⚠️ TR exchcode와 거래소가 1:1이 아니라 노이즈 존재(예: Nasdaq 대표상장 최다 코드가 `NSM`이라 Apple이
    여기 속함 — 초기 누락 원인). opol(MIC)은 더 깔끔하나 현재 스냅샷이라 상폐 누락 → exchcode(이력) 사용.
- 식별자: ISIN/CUSIP = org 대표상품(`priinstrpermid`)→`permisindata`/`permcusipdata`(최신).
  RIC/SEDOL = 해당 호가→`permricdata`/`permsedoldata`(최신). LEI=`permorgref.lei`. IPO일=`permorginfo.ipodate`.
- 회사×거래소 1행(상장중 우선 dedup).

## 결과 (2026-06-24) — `company_master.csv`
- 23,078 레코드 / 고유 org 23,008.

| 거래소 | 레코드 | 상장중 | 상폐(전기간) |
|---|---|---|---|
| JPX(TSE) | 5,066 | 3,852 | 1,214 |
| KRX | 3,599 | 2,308 | 1,291 |
| NYSE | 4,255 | 1,820 | 2,435 |
| Nasdaq | 8,964 | 3,050 | 5,914 |
| TWSE | 1,194 | 951 | 243 |

식별자 채움률: ISIN **81.2%** · **RIC 100%** · SEDOL 91.3% · CUSIP 38.5% · **LEI 24.1%** · IPO일(listing_start).
스팟체크 통과: 삼성 `KR7005930003`(005930.KS) · SK하이닉스 · 토요타 `JP3633400001`(7203.T)
· TSMC `TW0002330008`(2330.TW) · Apple `US0378331005`(AAPL.OQ, Nasdaq).

## ⚠️ 핵심 한계
- **상폐 일자(delisting date)를 신뢰할 수 없음**: PermID쪽 RIC 종료일은 9999 sentinel,
  Datastream `secmapx.enddate`는 벤더 갱신일(2079 sentinel)이라 둘 다 상폐일이 아님.
  → `listing_end`/`delisting_year` **미제공(공란)**. `is_active`(status=AC/DC)만 신뢰.
- 그 결과 **2011 필터를 상폐에 적용 불가**: 상장중은 전부(현재 상장=2011+ 충족), **상폐는 전기간 포함**
  (FactSet/Compustat의 "2011 이후 상폐"와 달리 시점 한정이 안 됨 → 상폐 수가 과다, 특히 Nasdaq).
- exchcode 노이즈로 거래소 귀속에 소량 오분류 가능.
- LEI는 TR도 아시아 커버리지 낮음(한국 org ~1.5%).

## 실행
`python build_master.py` → `company_master.csv` (루트 `.env` 사용)
