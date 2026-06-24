# listing-transfer

미국 거래소 간 **이전상장(listing transfer)** 내역을 CRSP 데이터로 추출하고
인터랙티브 대시보드로 시각화하는 프로젝트.

PERMNO를 고정한 채 CRSP 거래소 코드(`exchcd`)가 바뀌는 지점을 이전상장으로
식별한다. NYSE(1) · NYSE American/AMEX(2) · NASDAQ(3) 간 이동을 다룬다.

## 구성

| 파일 | 설명 |
|---|---|
| `exchange_transfers.py` | `crsp.stocknames`에서 이전상장 내역 추출 → CSV 출력 |
| `visualize.py` | 추출 결과를 자체 완결형 HTML 대시보드로 시각화 |
| `requirements.txt` | 의존 패키지 |

## 사용법

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# WRDS 자격증명 (.env.example 참고해 .env 작성)
#   WRDS_USERNAME=...
#   WRDS_PASSWORD=...

python exchange_transfers.py            # NYSE <-> NASDAQ
python exchange_transfers.py --amex     # AMEX 경유 포함
python visualize.py                     # transfers_dashboard.html 생성
```

## 대시보드

- **Sankey 흐름도** — 기간(10년) 슬라이더로 거래소 간 이동량 탐색
- **연도별 추이** / **NYSE↔NASDAQ 순이동** / **누적 순이동**
- **이전상장 목록** — 검색·정렬, 슬라이더와 연동 필터 (외부 CDN 의존 없음)

## 데이터 출처

[WRDS](https://wrds-www.wharton.upenn.edu/) CRSP. 데이터 접근에는 WRDS 구독 계정이 필요하다.
공식 파이썬 라이브러리: [`wrds`](https://github.com/wharton/wrds) (`pip install wrds`).
