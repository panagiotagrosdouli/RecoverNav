from __future__ import annotations

import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
import yaml
from recovernav.execution import run_scenario
from recovernav.scenarios import make_scenario

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--seeds",type=int,default=20); p.add_argument("--config",default=str(ROOT/"configs"/"default.yaml")); p.add_argument("--output",default=str(ROOT/"results"/"runs.csv")); args=p.parse_args()
    with open(args.config,encoding="utf-8") as f: cfg=yaml.safe_load(f)
    rows=[]; lam=float(cfg["planner"]["lambda_recovery"]); radius=int(cfg["planner"]["recovery_radius"])
    for seed in range(args.seeds):
        for name in cfg["experiments"]["scenarios"]:
            scenario=make_scenario(name,seed)
            for planner in ("baseline","recovernav"):
                _,metrics=run_scenario(scenario,planner,lam,radius); rows.append(metrics.as_dict())
    df=pd.DataFrame(rows); out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); df.to_csv(out,index=False); print(f"wrote {len(df)} paired runs to {out}")
if __name__=="__main__": main()
