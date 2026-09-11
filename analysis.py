"""월별 평균기온과 연간 고온일수·지속기간을 분석한다."""

from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".cache/matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
from heat_metrics import analyze_heat


BASE_DIR = Path(__file__).resolve().parent


def main():
    df = pd.read_csv(BASE_DIR / "data/processed/changwon_daily.csv", parse_dates=["date"])
    # 진행 중인 2026년은 이번 비교에서 제외한다.
    main_data = df.loc[df["date"].dt.year.between(2006, 2025)].copy()
    expected = pd.date_range("2006-01-01", "2025-12-31")
    if not pd.DatetimeIndex(main_data["date"]).equals(expected):
        raise ValueError("Main analysis requires complete, sorted daily dates.")
    if main_data["tavg"].isna().any():
        raise ValueError("Missing tavg: decide monthly coverage rules before continuing.")
    main_data["year"] = main_data["date"].dt.year
    main_data["month"] = main_data["date"].dt.month
    main_data["period"] = main_data["year"].map(
        lambda year: "2006-2015" if year <= 2015 else "2016-2025"
    )

    # 1단계: 각 연도 안에서 월평균을 계산한다 (20년 × 12개월).
    monthly = main_data.groupby(["period", "year", "month"], as_index=False).agg(
        tavg=("tavg", "mean"), observed_days=("tavg", "count")
    )
    # 2단계: 각 월의 연도별 평균 10개를 같은 비중으로 평균 낸다.
    comparison = monthly.groupby(["period", "month"])["tavg"].mean().unstack("period")
    comparison["difference_c"] = comparison["2016-2025"] - comparison["2006-2015"]

    output_dir = BASE_DIR / "data/processed"
    monthly.to_csv(output_dir / "monthly_by_year.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(output_dir / "monthly_comparison.csv", encoding="utf-8-sig")

    # Windows에서는 맑은 고딕을 사용하고, 다른 환경에서는 설치된 한글 글꼴을 찾는다.
    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in ["Malgun Gothic", "AppleGothic", "Noto Sans CJK KR", "NanumGothic"]:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), layout="constrained")
    months = comparison.index
    for period, color in [("2006-2015", "#2563A6"), ("2016-2025", "#D66036")]:
        axes[0].plot(months, comparison[period], marker="o", label=period, color=color)
    axes[0].set(title="창원 월별 평균기온: 두 10년 구간 비교", ylabel="평균기온 (℃)")
    axes[0].legend(frameon=False)
    differences = comparison["difference_c"]
    axes[1].bar(months, differences, color=["#D66036" if v >= 0 else "#2563A6" for v in differences])
    axes[1].axhline(0, color="#444444", linewidth=1)
    for month, value in differences.items():
        axes[1].annotate(f"{value:+.2f}", (month, value),
                         xytext=(0, 5 if value >= 0 else -5), textcoords="offset points",
                         ha="center", va="bottom" if value >= 0 else "top", fontsize=10)
    axes[1].set(title="월별 차이: 2016-2025년 평균에서 2006-2015년 평균을 뺀 값", ylabel="기온 차이 (℃)", xlabel="월")
    axes[1].margins(y=0.22)
    for ax in axes:
        ax.set_xticks(range(1, 13))
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.supxlabel("출처: 기상청 ASOS 창원(155) | 각 연도의 월평균을 구한 뒤 10년 평균 | 2026년 제외", fontsize=10)
    image_dir = BASE_DIR / "images"
    image_dir.mkdir(exist_ok=True)
    fig.savefig(image_dir / "01_monthly_comparison.png", dpi=160)
    plt.close(fig)
    print(comparison.round(3).to_string())
    print("Saved: images/01_monthly_comparison.png")
    analyze_heat(main_data, BASE_DIR)


if __name__ == "__main__":
    main()
