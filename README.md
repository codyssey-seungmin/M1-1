# M1-1: 창원 더위 변화 분석

## 분석 목적
창원에 거주하면서 경험하는 더위가 실제 관측자료에서도
변화하고 있는지 확인한다.
평균기온뿐 아니라 더운 날의 빈도와 지속기간을 함께 분석한다.

## 분석 질문
1. 2006~2015년과 2016~2025년의 월별 평균기온은 어떻게 다른가?
2. 일최고기온 30℃ 이상인 날의 수와 최장 연속일수는 달라졌는가?
3. 고온일의 변화는 한여름뿐 아니라 초여름과 초가을에도 나타나는가?

## 데이터 계획
- 출처: 기상청 기상자료개방포털 ASOS 일자료
- 관측지점: 창원(155)
- 목표 기간: 2006-01-01~2025-12-31
- 주요 항목: 날짜, 일평균기온, 일최고기온
- 실제 제공 범위와 결측 여부를 확인한 뒤 분석 범위를 확정한다.
- 30℃는 이번 분석에서 정한 고온일 기준이다.

## 예정 결과물
- REPORT.md: 분석 결과, 시각화, 인사이트, 한계, AI 사용 로그
- analysis.py: 데이터 정제 및 분석 코드
- images/: 시각화 이미지
- requirements.txt: 실행에 필요한 라이브러리 목록

## 실행 방법 (현재 단계)

Python 3.10 이상에서 프로젝트 폴더를 열고 실행한다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe check_data.py
.\.venv\Scripts\python.exe prepare_data.py
.\.venv\Scripts\python.exe analysis.py
```

- 원본과 수집 방법: [data/README.md](data/README.md)
- 통합 결과: `data/processed/changwon_daily.csv`
- 2006~2025년 7,305일을 본 분석에 사용한다.
- 2026년 1~8월 243일은 과거의 동일한 1~8월과 비교하는 추가 분석용이다.
- 통합 단계에서는 기온 결측 2개를 그대로 유지하며, 행을 삭제하거나 보간하지 않는다.
- 첫 분석 결과: [REPORT.md](REPORT.md), `images/01_monthly_comparison.png`
- 고온일수·지속기간: `heat_metrics.py`, `images/02_annual_heat.png`
- 월별 고온일수: `images/03_monthly_heat.png`
- 기준값 민감도(28℃·30℃·33℃): `images/04_threshold_comparison.png`
- 2026년 동일 기간 비교: `compare_2026.py`, `images/05_2026_comparison.png`
- `analysis.py`를 실행하면 현재까지의 다섯 분석을 모두 재생성한다.
