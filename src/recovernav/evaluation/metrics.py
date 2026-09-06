from __future__ import annotations

import pandas as pd


def summarize_runs(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("planner", as_index=False)
        .agg(
            runs=("success", "size"),
            success_rate=("success", "mean"),
            mean_path_length=("path_length", "mean"),
            mean_executed_distance=("executed_distance", "mean"),
            mean_replans=("replans", "mean"),
            mean_planning_time=("initial_planning_time", "mean"),
        )
        .sort_values("planner")
    )
