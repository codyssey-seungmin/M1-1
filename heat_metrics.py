"""고온일수와 연속일수를 계산하고 시각화한다."""

import pandas as pd
import matplotlib.pyplot as plt


def longest_run(flags):
    """True가 연속으로 나타난 가장 긴 길이. 연도별로 따로 호출한다."""
    longest = current = 0
    for hot in flags:
        current = current + 1 if hot else 0
        longest = max(longest, current)
    return longest


def annual_heat(data, threshold=30):
    records = []
    for year, group in data.groupby("year"):
        group = group.sort_values("date")
        missing = group["tmax"].isna()
        # 두 가정은 원본을 채우는 것이 아니라 가능한 결과 범위를 계산한다.
        lower = group["tmax"].ge(threshold) & ~missing
        upper = lower | missing
        records.append({
            "year": year,
            "period": "2006-2015" if year <= 2015 else "2016-2025",
            "threshold_c": threshold,
            "valid_days": int((~missing).sum()),
            "missing_days": int(missing.sum()),
            "hot_days_lower": int(lower.sum()),
            "hot_days_upper": int(upper.sum()),
            "longest_run_lower": longest_run(lower),
            "longest_run_upper": longest_run(upper),
        })
    return pd.DataFrame(records)


def analyze_heat(data, base_dir):
    annual = annual_heat(data)
    metrics = ["hot_days_lower", "hot_days_upper", "longest_run_lower", "longest_run_upper"]
    summary = annual.groupby("period")[metrics].mean()
    annual.to_csv(base_dir / "data/processed/annual_heat.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(base_dir / "data/processed/heat_period_comparison.csv", encoding="utf-8-sig")

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout="constrained")
    colors = ["#2563A6" if year <= 2015 else "#D66036" for year in annual.year]
    for ax, metric, title in zip(axes, ["hot_days", "longest_run"],
                                ["연간 고온일수", "연도 내 최장 연속 고온일수"]):
        lo = annual[f"{metric}_lower"]
        hi = annual[f"{metric}_upper"]
        ax.bar(annual.year, lo, color=colors, width=0.7)
        ax.errorbar(annual.year, lo, yerr=[lo * 0, hi - lo], fmt="none", color="#222222", capsize=3)
        for year, low, high in zip(annual.year, lo, hi):
            label = str(low) if low == high else f"{low}~{high}"
            ax.text(year, high + 0.8, label, ha="center", fontsize=9)
        ax.axvline(2015.5, color="#777777", linestyle=":")
        ax.set(title=title, ylabel="일수 (일)", xticks=annual.year)
        ax.tick_params(axis="x", rotation=45)
        ax.set_ylim(0, hi.max() * 1.18)
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("창원 더위의 빈도와 지속기간 | 일최고기온 30℃ 이상", fontsize=16)
    fig.supxlabel("기상청 ASOS 창원(155) | 파랑: 2006-2015 / 주황: 2016-2025\n2025년 최고기온 1일 결측: 고온일수 범위 표시, 최장 연속일수는 두 가정에서 동일", fontsize=10)
    fig.savefig(base_dir / "images/02_annual_heat.png", dpi=160)
    plt.close(fig)
    print("\nAnnual heat metrics:")
    print(annual.to_string(index=False))
    print("\nPeriod means:")
    print(summary.to_string())
