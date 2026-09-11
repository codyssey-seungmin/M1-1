"""STL 추세 평활폭과 robust 설정의 민감도를 비교한다."""

from decompose import BASE
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL


def main():
    baseline = pd.read_csv(BASE / "data/processed/stl_decomposition.csv", parse_dates=["date"]).set_index("date")
    observed = baseline.observed.asfreq("MS")
    if len(observed) != 240 or observed.isna().any():
        raise ValueError("Expected 240 complete monthly observations")
    curves, records = {}, []
    for width in [19, 25, 37]:
        for robust in [True, False]:
            label = f"trend={width}, robust={robust}"
            fit = STL(observed, period=12, seasonal=13, trend=width, robust=robust).fit()
            np.testing.assert_allclose(fit.trend + fit.seasonal + fit.resid, observed, atol=1e-10, rtol=0)
            curves[label] = fit.trend
            early = fit.trend.loc["2006":"2015"].mean()
            recent = fit.trend.loc["2016":"2025"].mean()
            records.append({"trend_window": width, "robust": robust,
                            "early_mean": early, "recent_mean": recent,
                            "difference_c": recent - early,
                            "last_trend": fit.trend.iloc[-1],
                            "max_abs_difference_from_baseline": (fit.trend - baseline.trend).abs().max()})
    trends = pd.DataFrame(curves)
    summary = pd.DataFrame(records)
    np.testing.assert_allclose(trends["trend=25, robust=True"], baseline.trend, atol=1e-10, rtol=0)
    trends.to_csv(BASE / "data/processed/stl_sensitivity_trends.csv", encoding="utf-8-sig")
    summary.to_csv(BASE / "data/processed/stl_sensitivity_summary.csv", index=False, encoding="utf-8-sig")
    fonts = {font.name for font in font_manager.fontManager.ttflist}
    for font in ["Malgun Gothic", "AppleGothic", "Noto Sans CJK KR", "NanumGothic"]:
        if font in fonts:
            plt.rcParams["font.family"] = font
            break
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), layout="constrained")
    palette = {19: "#2563A6", 25: "#D66036", 37: "#52834E"}
    for row in records:
        width, robust = row["trend_window"], row["robust"]
        label = f"trend={width}, robust={robust}"
        axes[0].plot(trends.index, trends[label], label=label, color=palette[width],
                     linestyle="-" if robust else "--", linewidth=1.4)
    axes[0].set(title="6개 설정의 추세선", ylabel="추세 성분 (℃)")
    axes[0].legend(ncol=3, fontsize=9, frameon=False)
    # 표시 구간은 가장 넓은 37개월 창의 절반에 맞춘 주의 영역이다.
    axes[0].axvspan(trends.index[0], trends.index[18], color="gray", alpha=0.12)
    axes[0].axvspan(trends.index[-19], trends.index[-1], color="gray", alpha=0.12)
    axes[1].bar(range(6), summary.difference_c, color=[palette[w] for w in summary.trend_window])
    for i, value in enumerate(summary.difference_c):
        axes[1].text(i, value + 0.008, f"{value:+.3f}", ha="center")
    axes[1].set(title="추세 성분 평균 차이: 2016-2025 평균에서 2006-2015 평균을 뺀 값",
                ylabel="차이 (℃)", xticks=range(6),
                xticklabels=[f"{r['trend_window']}개월\nrobust={r['robust']}" for r in records],
                ylim=(0, summary.difference_c.max() * 1.25))
    for ax in axes:
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("STL 설정 민감도 | 같은 240개월 자료, 주기 12·계절 평활폭 13 고정", fontsize=15)
    fig.supxlabel("기상청 ASOS 창원(155) | 회색: 양끝 약 18개월 해석 주의 | 설정 간 범위는 신뢰구간이 아님\n추세 성분의 비교이며 원본 기온 차이와 구분 | 가장 유리한 설정을 골라 결론을 내리지 않음", fontsize=10)
    fig.savefig(BASE / "images/07_stl_sensitivity.png", dpi=150)
    plt.close(fig)
    print(summary.round(4).to_string(index=False))
    print("Maximum setting spread:", (trends.max(axis=1) - trends.min(axis=1)).max())
    print("Last-month setting spread:", trends.iloc[-1].max() - trends.iloc[-1].min())


if __name__ == "__main__":
    main()
