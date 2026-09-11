"""브라우저용 계산 함수를 Node.js에서 실행해 Python 분석 결과와 대조한다."""
from pathlib import Path
import json
import subprocess
import pandas as pd

BASE = Path(__file__).resolve().parent

def main():
    javascript = """
const fs=require('fs'),vm=require('vm');
const sandbox={window:{}};
vm.runInNewContext(fs.readFileSync('dashboard/dist/data.js','utf8'),sandbox);
const {calculate}=require('./dashboard/dist/app.js');
const results={};
for(const t of [28,30,33]) results[t]=calculate(sandbox.window.WEATHER_DATA,2006,2025,t,'full');
results.partial=calculate(sandbox.window.WEATHER_DATA,2006,2026,30,'janaug');
results.single=calculate(sandbox.window.WEATHER_DATA,2024,2024,30,'full');
console.log(JSON.stringify(results));
"""
    process = subprocess.run(["node", "-e", javascript], cwd=BASE, capture_output=True, text=True, check=True)
    results = json.loads(process.stdout)
    reference = pd.read_csv(BASE / "data/processed/threshold_annual.csv")
    mapping = {"low": "hot_days_lower", "high": "hot_days_upper",
               "longLow": "longest_run_lower", "longHigh": "longest_run_upper",
               "missing": "missing_days"}
    checked = 0
    for threshold in [28,30,33]:
        expected = reference[reference.threshold_c.eq(threshold)].set_index("year")
        assert len(results[str(threshold)]) == 20
        for row in results[str(threshold)]:
            for actual, column in mapping.items():
                assert row[actual] == expected.loc[row['year'], column], (threshold,row['year'],column)
            assert row['days'] == expected.loc[row['year'],'valid_days'] + expected.loc[row['year'],'missing_days']
            checked += 1
    partial = pd.read_csv(BASE / "data/processed/jan_aug_comparison.csv").set_index("year")
    assert len(results['partial']) == 21
    for row in results['partial']:
        for actual,column in mapping.items():
            column = 'missing_tmax_days' if actual == 'missing' else column
            assert row[actual] == partial.loc[row['year'],column]
        assert row['days'] == partial.loc[row['year'],'calendar_days']
        checked += 1
    assert len(results['single']) == 1
    assert results['single'][0]['low'] == 78 and results['single'][0]['longLow'] == 34
    print(f"PASS: {checked} annual results and single-year filter match Python references.")
    print("This checks calculation functions, not browser rendering or UI events.")

if __name__ == '__main__':
    main()
