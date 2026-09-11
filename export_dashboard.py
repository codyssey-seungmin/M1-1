"""분석 데이터를 브라우저에서 읽을 수 있는 파일로 내보낸다."""
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parent

def main():
    df = pd.read_csv(BASE / "data/processed/changwon_daily.csv")
    rows = json.loads(df[["date", "tavg", "tmax"]].to_json(orient="records", force_ascii=False))
    target = BASE / "dashboard/dist"
    target.mkdir(parents=True, exist_ok=True)
    (target / "data.js").write_text("window.WEATHER_DATA = " + json.dumps(rows, ensure_ascii=False, allow_nan=False) + ";\n", encoding="utf-8")
    print(f"Exported {len(rows)} rows to dashboard/dist/data.js")

if __name__ == "__main__":
    main()
