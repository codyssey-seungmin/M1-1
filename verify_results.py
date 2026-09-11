"""분석 실행 후 원본 보존·집계 일관성·리포트 이미지 링크를 검증한다."""

from pathlib import Path
import re

import pandas as pd
from PIL import Image

from check_data import COLUMNS, PERIODS, RAW_DIR

BASE = Path(__file__).resolve().parent
PROCESSED = BASE / "data/processed"


def main():
    raw = pd.concat([pd.read_csv(RAW_DIR / name, encoding="cp949").rename(columns=COLUMNS)
                     for name in PERIODS], ignore_index=True)
    combined = pd.read_csv(PROCESSED / "changwon_daily.csv")
    pd.testing.assert_frame_equal(raw, combined[raw.columns])
    assert len(combined) == 7548
    assert combined.is_main_analysis.sum() == 7305

    annual = pd.read_csv(PROCESSED / "annual_heat.csv").set_index("year")
    monthly = pd.read_csv(PROCESSED / "monthly_heat_by_year.csv")
    columns = ["hot_days_lower", "hot_days_upper"]
    assert len(monthly) == 240
    assert monthly.groupby("year").size().eq(12).all()
    pd.testing.assert_frame_equal(monthly.groupby("year")[columns].sum(), annual[columns])

    threshold = pd.read_csv(PROCESSED / "threshold_annual.csv")
    pd.testing.assert_frame_equal(threshold[threshold.threshold_c.eq(30)].set_index("year"), annual)
    assert threshold.groupby(["threshold_c", "period"]).size().eq(10).all()
    for column in columns + ["longest_run_lower", "longest_run_upper"]:
        pivot = threshold.pivot(index="year", columns="threshold_c", values=column)
        assert (pivot[28] >= pivot[30]).all() and (pivot[30] >= pivot[33]).all()

    partial = pd.read_csv(PROCESSED / "jan_aug_comparison.csv").set_index("year")
    pd.testing.assert_frame_equal(monthly[monthly.month.le(8)].groupby("year")[columns].sum(),
                                  partial.loc[2006:2025, columns])
    assert partial.loc[2026, "hot_days_lower"] == 56
    assert partial.loc[2026, "calendar_days"] == 243

    report = (BASE / "REPORT.md").read_text(encoding="utf-8")
    image_links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", report)
    assert len(image_links) == 5
    for link in image_links:
        with Image.open(BASE / link) as picture:
            picture.verify()
    for name in ["README.md", "REPORT.md", "data/README.md"]:
        document = BASE / name
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if not link.startswith(("http://", "https://", "#")):
                assert (document.parent / link).exists(), f"Broken link: {name}: {link}"
    print("PASS: original values, annual/monthly totals, thresholds, January-August comparison, 5 PNGs, local links")


if __name__ == "__main__":
    main()
