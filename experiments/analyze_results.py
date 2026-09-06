from __future__ import annotations

import argparse, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
import matplotlib.pyplot as plt
import pandas as pd
from recovernav.evaluation.metrics import summarize_runs

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--input",default=str(ROOT/"results"/"runs.csv")); p.add_argument("--output-dir",default=str(ROOT/"results")); args=p.parse_args()
    df=pd.read_csv(args.input); summary=summarize_runs(df); print(summary.to_string(index=False)); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True); summary.to_csv(out/"summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(6,4)); by=df.groupby("planner")["success"].mean().sort_index(); ax.bar(by.index,by.values); ax.set_ylim(0,1); ax.set_ylabel("Success rate"); ax.set_title("Navigation success"); fig.tight_layout(); fig.savefig(out/"success_rate.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,4)); groups=list(df.groupby("planner")); ax.boxplot([g["executed_distance"].to_numpy() for _,g in groups],tick_labels=[n for n,_ in groups]); ax.set_ylabel("Executed distance"); ax.set_title("Executed distance by planner"); fig.tight_layout(); fig.savefig(out/"executed_distance.png",dpi=160); plt.close(fig)
if __name__=="__main__": main()
