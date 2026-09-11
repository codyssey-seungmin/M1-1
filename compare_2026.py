"""2026년 1~8월을 과거 동일 월 범위와 비교한다."""

import pandas as pd
import matplotlib.pyplot as plt

from heat_metrics import longest_run


def compare_current_year(data, base_dir):
    subset = data.loc[data["date"].dt.month.le(8)].copy()
    records = []
    for year, group in subset.groupby(subset["date"].dt.year):
        group = group.sort_values("date")
        expected = pd.date_range(f"{year}-01-01", f"{year}-08-31")
        if not pd.DatetimeIndex(group["date"]).equals(expected):
            raise ValueError(f"Incomplete January-August dates: {year}")
        if group["tavg"].isna().any():
            raise ValueError(f"Missing mean temperature: {year}")
        missing = group["tmax"].isna()
        low = group["tmax"].ge(30) & ~missing
        high = low | missing
        # 각 월에 같은 비중을 주는 참고 지표이며, 일별 기온의 단순평균과 구분한다.
        monthly_mean = group.groupby(group["date"].dt.month)["tavg"].mean()
        records.append({
            "year": year, "calendar_days": len(group),
            "valid_tmax_days": int((~missing).sum()),
            "missing_tmax_days": int(missing.sum()),
            "equal_month_tavg": monthly_mean.mean(),
            "hot_days_lower": int(low.sum()), "hot_days_upper": int(high.sum()),
            "hot_pct_lower": low.sum() / len(group) * 100,
            "hot_pct_upper": high.sum() / len(group) * 100,
            "observed_hot_pct": low.sum() / (~missing).sum() * 100,
            "longest_run_lower": longest_run(low), "longest_run_upper": longest_run(high),
        })
    result = pd.DataFrame(records).set_index("year")
    historical = result.loc[2006:2025]
    result.to_csv(base_dir / "data/processed/jan_aug_comparison.csv", encoding="utf-8-sig")

    daily = subset.assign(year=subset["date"].dt.year, month=subset["date"].dt.month)
    monthly = daily.groupby(["year", "month"])["tavg"].mean().unstack("year")
    plot_data = pd.DataFrame({
        "historical_mean": monthly.loc[:, 2006:2025].mean(axis=1),
        "historical_min": monthly.loc[:, 2006:2025].min(axis=1),
        "historical_max": monthly.loc[:, 2006:2025].max(axis=1),
        "2026": monthly[2026],
    })
    plot_data.to_csv(base_dir / "data/processed/monthly_2026_comparison.csv", encoding="utf-8-sig")
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout="constrained")
    axes[0].fill_between(plot_data.index, plot_data.historical_min, plot_data.historical_max,
                         alpha=0.15, color="#2563A6", label="2006-2025 각 월평균의 최솟값~최댓값")
    axes[0].plot(plot_data.index, plot_data.historical_mean, marker="o", color="#2563A6", label="2006-2025 평균")
    axes[0].plot(plot_data.index, plot_data["2026"], marker="o", color="#D66036", label="2026")
    axes[0].set(title="1~8월 월평균기온", xlabel="월", ylabel="기온 (℃)", xticks=range(1, 9))
    axes[0].legend(frameon=False, fontsize=9)
    colors = ["#D66036" if y == 2026 else "#2563A6" for y in result.index]
    axes[1].bar(result.index, result.hot_days_lower, color=colors)
    for year, row in result.iterrows():
        lo, hi = int(row.hot_days_lower), int(row.hot_days_upper)
        axes[1].text(year, hi + 0.8, str(lo) if lo == hi else f"{lo}~{hi}", ha="center", fontsize=9)
    axes[1].axhline(historical.hot_days_lower.mean(), color="#555555", linestyle="--",
                    label=f"과거 평균 하한 {historical.hot_days_lower.mean():.1f}일")
    axes[1].set(title="각 연도 1~8월의 고온일수 (일최고기온 30℃ 이상)",
                xlabel="연도", ylabel="일수 (일)", xticks=result.index,
                ylim=(0, result.hot_days_upper.max() * 1.22))
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].legend(frameon=False)
    for ax in axes:
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("2026년 창원 더위: 과거와 같은 1~8월만 비교", fontsize=16)
    fig.supxlabel("기상청 ASOS 창원(155) | 음영은 과거 월평균의 관측 범위이며 예측구간이 아님\n2025년 결측 범위 표시 | 2026년 연간 결과로 해석하지 않음", fontsize=10)
    fig.savefig(base_dir / "images/05_2026_comparison.png", dpi=160)
    plt.close(fig)
    print("\nJanuary-August comparison:")
    print(result.round(3).to_string())
    print("Historical mean hot days bounds:", historical.hot_days_lower.mean(), historical.hot_days_upper.mean())
    print("2026 monthly temperatures:\n", plot_data.round(3).to_string())
