"""
Dataset inspection and exploratory data analysis tool for CareerMatch AI.
Produces terminal statistics and generates a visual HTML report at reports/dataset_analysis.html.

Command: python -m data_generation.inspect_dataset
"""

import os
import json
import pandas as pd
import numpy as np


def inspect_dataset(csv_path: str = "data/generated_resume_job_dataset.csv", report_dir: str = "reports") -> dict:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please run python -m data_generation.generate_dataset first.")

    os.makedirs(report_dir, exist_ok=True)
    html_report_path = os.path.join(report_dir, "dataset_analysis.html")

    print(f"[*] Inspecting CareerMatch AI Training Dataset: {csv_path}")
    df = pd.read_csv(csv_path)

    total_records = len(df)
    missing_values = df.isnull().sum().to_dict()
    total_missing = sum(missing_values.values())
    duplicates = int(df.duplicated(subset=["resume_text", "job_description_text"]).sum())

    scores = df["match_score"]
    mean_score = float(scores.mean())
    std_score = float(scores.std())
    min_score = float(scores.min())
    max_score = float(scores.max())
    p25 = float(scores.quantile(0.25))
    p50 = float(scores.median())
    p75 = float(scores.quantile(0.75))

    low_bracket = int((scores < 50.0).sum())
    mid_bracket = int(((scores >= 50.0) & (scores < 75.0)).sum())
    high_bracket = int((scores >= 75.0).sum())

    role_counts = df["target_job_role"].value_counts().to_dict()
    archetype_counts = df["scenario_archetype"].value_counts().to_dict() if "scenario_archetype" in df.columns else {}
    exp_summary = {
        "candidate_exp_mean": round(float(df["candidate_experience_years"].mean()), 2),
        "required_exp_mean": round(float(df["required_experience_years"].mean()), 2)
    }

    print("=" * 65)
    print("CAREERMATCH AI - DATASET INSPECTION & INTEGRITY AUDIT")
    print("=" * 65)
    print(f"Total Records:             {total_records:,}")
    print(f"Total Missing / Nulls:     {total_missing}")
    print(f"Duplicate Resume-Job Pairs: {duplicates} ({duplicates / total_records * 100:.2f}%)")
    print("-" * 65)
    print("TARGET VARIABLE ('match_score') METRICS:")
    print(f"  Mean:   {mean_score:.2f}   | Std Dev: {std_score:.2f}")
    print(f"  Min:    {min_score:.2f}   | Max:     {max_score:.2f}")
    print(f"  25th%:  {p25:.2f}   | Median:  {p50:.2f}   | 75th%: {p75:.2f}")
    print("-" * 65)
    print("DISTRIBUTION BRACKETS:")
    print(f"  Low Match (<50):         {low_bracket:,} ({low_bracket / total_records * 100:.1f}%)")
    print(f"  Medium Match (50-75):    {mid_bracket:,} ({mid_bracket / total_records * 100:.1f}%)")
    print(f"  High Match (>=75):       {high_bracket:,} ({high_bracket / total_records * 100:.1f}%)")
    print("-" * 65)
    print(f"Target Roles Represented:  {len(role_counts)}")
    print(f"Average Candidate Exp:     {exp_summary['candidate_exp_mean']} years")
    print(f"Average Required Exp:      {exp_summary['required_exp_mean']} years")
    print("=" * 65)

    # Generate visual HTML Report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CareerMatch AI - Dataset Inspection Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #FAF9FC; color: #111111; margin: 0; padding: 40px; }}
    .container {{ max-width: 960px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); padding: 36px; border: 1px solid #E4DDEA; }}
    h1 {{ color: #7657B8; margin-top: 0; font-size: 28px; }}
    .subtitle {{ color: #555555; margin-bottom: 24px; font-size: 15px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }}
    .card {{ background: #EDE5F8; border-radius: 12px; padding: 20px; border: 1px solid #E4DDEA; text-align: center; }}
    .card .val {{ font-size: 24px; font-weight: 700; color: #7657B8; margin-top: 4px; }}
    .card .lbl {{ font-size: 13px; color: #555555; text-transform: uppercase; letter-spacing: 0.5px; }}
    .section {{ margin-top: 32px; }}
    h2 {{ font-size: 18px; border-bottom: 2px solid #EDE5F8; padding-bottom: 8px; color: #111111; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #F0EDF5; }}
    th {{ background: #FAF9FC; color: #555555; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
    .badge-low {{ background: #F8ECE7; color: #C04828; }}
    .badge-mid {{ background: #E7F1FA; color: #1A73E8; }}
    .badge-high {{ background: #E3F6F1; color: #137333; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>CareerMatch AI — Training Dataset Inspection</h1>
    <div class="subtitle">Explainable AI-Based Resume Screening and Skill Gap Analysis System | B.Tech Capstone Audit</div>

    <div class="grid">
      <div class="card"><div class="lbl">Total Records</div><div class="val">{total_records:,}</div></div>
      <div class="card"><div class="lbl">Mean Match Score</div><div class="val">{mean_score:.1f}%</div></div>
      <div class="card"><div class="lbl">Target Roles</div><div class="val">{len(role_counts)}</div></div>
      <div class="card"><div class="lbl">Missing Values</div><div class="val">{total_missing}</div></div>
    </div>

    <div class="section">
      <h2>Score Distribution Brackets</h2>
      <table>
        <thead>
          <tr><th>Bracket</th><th>Range</th><th>Records</th><th>Percentage</th><th>Classification</th></tr>
        </thead>
        <tbody>
          <tr><td>Low Match</td><td>0.0 - 49.9</td><td>{low_bracket:,}</td><td>{low_bracket/total_records*100:.1f}%</td><td><span class="badge badge-low">Major Skill Gap</span></td></tr>
          <tr><td>Medium Match</td><td>50.0 - 74.9</td><td>{mid_bracket:,}</td><td>{mid_bracket/total_records*100:.1f}%</td><td><span class="badge badge-mid">Transferable / Partial</span></td></tr>
          <tr><td>High Match</td><td>75.0 - 100.0</td><td>{high_bracket:,}</td><td>{high_bracket/total_records*100:.1f}%</td><td><span class="badge badge-high">Strong Alignment</span></td></tr>
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2>Role Distribution</h2>
      <table>
        <thead><tr><th>Target Job Role</th><th>Sample Count</th><th>Proportion</th></tr></thead>
        <tbody>
          {''.join([f"<tr><td>{r}</td><td>{c:,}</td><td>{c/total_records*100:.1f}%</td></tr>" for r, c in sorted(role_counts.items(), key=lambda x: x[1], reverse=True)])}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
    with open(html_report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Dataset visual inspection report generated at {html_report_path}")
    return {
        "total_records": total_records,
        "mean_score": mean_score,
        "std_score": std_score,
        "low_pct": round(low_bracket / total_records * 100, 2),
        "mid_pct": round(mid_bracket / total_records * 100, 2),
        "high_pct": round(high_bracket / total_records * 100, 2)
    }


if __name__ == "__main__":
    inspect_dataset()
