# M1-1: 창원 더위 변화 분석

## 분석 목적
창원에 거주하면서 경험하는 더위가 실제 관측자료에서도
변화하고 있는지 확인한다.
평균기온뿐 아니라 더운 날의 빈도와 지속기간을 함께 분석한다.

## 분석 질문
1. 2006~2015년과 2016~2025년의 월별 평균기온은 어떻게 다른가?
2. 일최고기온 30℃ 이상인 날의 수와 최장 연속일수는 달라졌는가?
3. 고온일의 변화는 한여름뿐 아니라 초여름과 초가을에도 나타나는가?

## 데이터
- 출처: 기상청 기상자료개방포털 ASOS 일자료
- 관측지점: 창원(155)
- 본 분석 기간: 2006-01-01~2025-12-31 (7,305일)
- 추가 비교: 2026-01-01~2026-08-31 (243일)
- 주요 항목: 날짜, 일평균기온, 일최고기온
- 날짜 누락·중복 없음. 최고기온·최저기온 각각 1개 결측은 보존한다.
- 30℃는 이번 분석에서 정한 고온일 기준이다.

## 결과물
- REPORT.md: 분석 결과, 시각화, 인사이트, 한계, AI 사용 로그
- check_data.py / prepare_data.py: 원본 점검과 통합
- analysis.py / heat_metrics.py / compare_2026.py: 분석과 시각화
- images/: 시각화 이미지
- requirements.txt: 실행에 필요한 라이브러리 목록

## 실행 방법

검증 환경은 Windows, Python 3.13.15이며 `requirements.txt`에 설치 버전을 고정했다.
과제의 최소 조건은 Python 3.10 이상이지만 이 의존성 조합을 모든 Python 버전에서
검증한 것은 아니다. 재현 시 Python 3.13 환경을 권장한다.
아래 명령은 PowerShell에서 프로젝트 폴더를 연 상태로 실행한다.
가상환경이 이미 있으면 생성·설치 단계를 건너뛰어도 된다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe check_data.py
.\.venv\Scripts\python.exe prepare_data.py
.\.venv\Scripts\python.exe analysis.py
.\.venv\Scripts\python.exe verify_results.py
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

원본 CSV가 저장소에 포함되어 있어 분석 실행에는 기상청 로그인이나 네트워크가 필요 없다.
처음 라이브러리를 설치할 때는 네트워크가 필요하다.
원본은 CP949, 생성 CSV는 UTF-8 BOM으로 읽는다. 이미지가 자동으로 열리지는 않으며
`images/`에서 PNG를 열거나 `REPORT.md`를 VS Code의 Ctrl+Shift+V로 미리보기 한다.
한글 글꼴은 Windows의 맑은 고딕을 사용하며, 다른 운영체제에는 코드에 지정한 한글 글꼴 설치가 필요할 수 있다.

## 과제 요구사항 대응

| 요구사항 | 결과 |
|---|---|
| 100개 이상 시계열 자료 | 원본 7,548행 |
| 질문 3개 이상 | 리포트 1절의 3개 질문 |
| 정제와 분석 기법 2가지 이상 | 결측·중복 점검, 월별 집계·구간 비교·연속일수 분석 |
| 시각화 2개 이상 | PNG 5개, 리포트에 상대경로로 포함 |
| 근거 있는 인사이트 3개 이상 | 리포트 8절 |
| 결론·한계·AI 사용 로그 | 리포트 8~9절 |
| 코드·데이터·재현 방법 | Python 스크립트, 원본, 의존성 목록과 위 실행 순서 |

민감도 분석과 2026년 비교는 추가 분석이다. 대시보드 및 분해·예측 보너스는 포함하지 않는다.
