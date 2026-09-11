"""창원 월평균기온 240개월을 STL로 분해한다."""

from pathlib import Path
import os

BASE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE / ".cache/matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL


def main():
    daily = pd.read_csv(BASE / "data/processed/changwon_daily.csv", parse_dates=["date"])
    daily = daily.set_index("date").loc["2006-01-01":"2025-12-31"]
    expected = pd.date_range("2006-01-01", "2025-12-31")
    if not daily.index.equals(expected) or daily.tavg.isna().any():
        raise ValueError("Expected complete daily mean temperatures for 2006-2025")
    # MS는 월초를 뜻한다. 20년을 하나의 연속된 월별 시계열로 만든다.
    observed = daily.tavg.resample("MS").mean()
    assert len(observed) == 240 and observed.notna().all()

    # period는 12개월 주기, seasonal은 같은 계절 위치의 평활화 폭이다.
    fit = STL(observed, period=12, seasonal=13, trend=25, robust=True).fit()
    result = pd.DataFrame({"observed": observed, "trend": fit.trend,
                           "seasonal": fit.seasonal, "residual": fit.resid,
                           "robust_weight": fit.weights})
    result.index.name = "date"
    reconstructed = result[["trend", "seasonal", "residual"]].sum(axis=1)
    error = (result.observed - reconstructed).abs().max()
    np.testing.assert_allclose(reconstructed, observed, atol=1e-10, rtol=0)
    result.to_csv(BASE / "data/processed/stl_decomposition.csv", encoding="utf-8-sig")

    fonts = {font.name for font in font_manager.fontManager.ttflist}
    for font in ["Malgun Gothic", "AppleGothic", "Noto Sans CJK KR", "NanumGothic"]:
        if font in fonts:
            plt.rcParams["font.family"] = font
            break
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True, layout="constrained")
    panels = [("observed", "관측값: 월평균기온", "#334155"),
              ("trend", "추세: 완만하게 변하는 기온 수준", "#D66036"),
              ("seasonal", "계절성: 반복되는 연간 패턴", "#2563A6"),
              ("residual", "잔차: 추세·계절성으로 설명되지 않은 변동", "#6D5494")]
    for ax, (column, title, color) in zip(axes, panels):
        ax.plot(result.index, result[column], color=color, linewidth=1.2)
        ax.set(title=title, ylabel="℃")
        ax.grid(alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)
        if column in ["seasonal", "residual"]:
            ax.axhline(0, color="#555555", linewidth=0.8)
        if column == "trend":
            ax.axvspan(result.index[0], result.index[12], color="#999999", alpha=0.15)
            ax.axvspan(result.index[-13], result.index[-1], color="#999999", alpha=0.15)
    fig.suptitle("창원 기온의 STL 분해 | 2006-2025 월자료 240개", fontsize=16)
    fig.supxlabel("기상청 ASOS 창원(155) | 주기 12개월, 계절 평활폭 13, 추세 평활폭 25개월, robust=True\n패널별 세로축 범위가 다름 | 추세 양끝 회색 영역은 해석 주의 표시이며 신뢰구간이 아님", fontsize=10)
    (BASE / "images").mkdir(exist_ok=True)
    fig.savefig(BASE / "images/06_stl_decomposition.png", dpi=150)
    plt.close(fig)
    print("Monthly observations:", len(observed))
    print("Maximum reconstruction error:", error)
    print("Trend yearly means:")
    print(result.trend.groupby(result.index.year).mean().round(3).to_string())
    print("Largest positive residual:", result.residual.idxmax().date(), result.residual.max())
    print("Largest negative residual:", result.residual.idxmin().date(), result.residual.min())


if __name__ == "__main__":
    main()
