"""세 원본을 합쳐 날짜별 분석용 데이터를 만든다. 원본은 수정하지 않는다."""

from pathlib import Path

import pandas as pd

from check_data import COLUMNS, PERIODS, RAW_DIR


def main():
    frames = []
    for filename, (start, end) in PERIODS.items():
        df = pd.read_csv(RAW_DIR / filename, encoding="cp949")
        if not set(COLUMNS).issubset(df.columns):
            raise ValueError(f"Unexpected columns: {filename}")
        df = df.rename(columns=COLUMNS)
        df["date"] = pd.to_datetime(df["date"], errors="raise")
        df = df.sort_values("date").reset_index(drop=True)
        expected = pd.date_range(start, end, freq="D")
        if not pd.DatetimeIndex(df["date"]).equals(expected):
            raise ValueError(f"Missing, duplicate, or unexpected dates: {filename}")
        if not df["station"].eq(155).all():
            raise ValueError(f"Unexpected station: {filename}")
        for column in ["tavg", "tmin", "tmax"]:
            df[column] = pd.to_numeric(df[column], errors="raise")
        df["source_file"] = filename
        frames.append(df)

    # 세 표를 세로 방향으로 이어 붙이고 날짜순으로 정렬한다.
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values("date").reset_index(drop=True)
    if combined["date"].duplicated().any():
        raise ValueError("Duplicate dates across files")

    combined["year"] = combined["date"].dt.year
    combined["month"] = combined["date"].dt.month
    combined["period"] = combined["year"].map(
        lambda year: "2006-2015" if year <= 2015
        else "2016-2025" if year <= 2025 else "2026-partial"
    )
    combined["is_main_analysis"] = combined["year"].between(2006, 2025)
    # 결측값을 0으로 채우거나 해당 행을 삭제하지 않는다.
    output = Path(__file__).resolve().parent / "data" / "processed" / "changwon_daily.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")

    print(f"Saved: {output}")
    print(combined.groupby("period").size().rename("rows").to_string())
    print("Missing temperatures:")
    print(combined[["tavg", "tmin", "tmax"]].isna().sum().to_string())


if __name__ == "__main__":
    main()
