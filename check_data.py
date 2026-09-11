"""원본 CSV의 날짜, 관측지점, 결측과 기온 순서를 확인한다."""

from pathlib import Path

import pandas as pd


RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
PERIODS = {
    "changwon_daily_2006_2015.csv": ("2006-01-01", "2015-12-31"),
    "changwon_daily_2016_2025.csv": ("2016-01-01", "2025-12-31"),
    "changwon_daily_2026_jan_aug.csv": ("2026-01-01", "2026-08-31"),
}
COLUMNS = {
    "지점": "station",
    "지점명": "station_name",
    "일시": "date",
    "평균기온(°C)": "tavg",
    "최저기온(°C)": "tmin",
    "최고기온(°C)": "tmax",
}


def main():
    frames = []
    for filename, (start, end) in PERIODS.items():
        # 기상청 CSV의 한글을 읽기 위해 CP949 인코딩을 지정한다.
        df = pd.read_csv(RAW_DIR / filename, encoding="cp949")
        missing_columns = set(COLUMNS) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")
        df = df.rename(columns=COLUMNS)
        df["date"] = pd.to_datetime(df["date"], errors="raise")
        expected = pd.date_range(start, end, freq="D")
        dates = pd.DatetimeIndex(df["date"])

        print(f"\n[{filename}]")
        print(f"Rows: {len(df)} / expected: {len(expected)}")
        print(f"Dates: {dates.min().date()} to {dates.max().date()}")
        print(f"Stations: {df['station'].unique().tolist()}")
        print(f"Sorted: {dates.is_monotonic_increasing}")
        print(f"Duplicate dates: {dates.duplicated().sum()}")
        print(f"Missing dates: {len(expected.difference(dates))}")
        print(f"Out-of-period dates: {len(dates.difference(expected))}")
        print("Missing temperature values:")
        print(df[["tavg", "tmin", "tmax"]].isna().sum().to_string())
        incomplete = df[["tavg", "tmin", "tmax"]].isna().any(axis=1)
        if incomplete.any():
            print(df.loc[incomplete, ["date", "tavg", "tmin", "tmax"]].to_string(index=False))

        # 결측이 있는 비교는 제외하고, 확인 가능한 기온 순서 오류를 찾는다.
        invalid = ((df["tmin"] > df["tavg"])
                   | (df["tavg"] > df["tmax"])
                   | (df["tmin"] > df["tmax"]))
        print(f"Temperature order violations: {invalid.sum()}")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    print(f"\nTotal rows: {len(combined)}")
    print(f"Duplicate dates across files: {combined['date'].duplicated().sum()}")


if __name__ == "__main__":
    main()
