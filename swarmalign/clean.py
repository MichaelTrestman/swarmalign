"""Turns raw src/evaluate_models.py output into the tidy choice CSVs group_metrics.py reads.

Plan.md section 6, step 7. Keeps only rows with a parsed A/B choice (INVALID
and ERROR rows never enter a fit, per plan.md section 9's conventions), and
writes agent_id, scenario_id, value1, value2, chose_value.

`chose_value` is the value *name* the agent picked. evaluate_models.py's
evaluate_models_mcq already remaps the displayed letter back through
action_map before saving, so the raw CSV's `choice` column means
"agent picked action1" or "action2", not "the model said the letter
A/B that happened to be on screen" -- the A/B swap only affected what the
model saw, not what got written to disk.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["scenario_id", "value1", "value2", "choice"]


def clean_agent_choices(agent_id: str, raw_choices_csv: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(raw_choices_csv)
    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"{raw_choices_csv} is missing column(s): {missing}")

    n_total = len(raw)
    valid = raw[raw["choice"].isin(["A", "B"])].copy()
    valid["chose_value"] = valid["value1"].where(valid["choice"] == "A", valid["value2"])
    valid["agent_id"] = agent_id

    n_dropped = n_total - len(valid)
    stats = {
        "agent_id": agent_id,
        "n_total": n_total,
        "n_kept": len(valid),
        "n_dropped": n_dropped,
        "drop_rate": (n_dropped / n_total) if n_total else 0.0,
    }
    return valid[["agent_id", "scenario_id", "value1", "value2", "chose_value"]], stats


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--choices-dir",
        type=Path,
        required=True,
        help="directory holding raw <agent_id>.csv files from run_assay.py",
    )
    p.add_argument("--agents", nargs="+", required=True, help="agent ids to clean")
    p.add_argument("--out", type=Path, required=True, help="output directory for cleaned CSVs")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    all_stats = []
    for agent_id in args.agents:
        raw_path = args.choices_dir / f"{agent_id}.csv"
        cleaned, stats = clean_agent_choices(agent_id, raw_path)
        cleaned.to_csv(args.out / f"{agent_id}.csv", index=False)
        all_stats.append(stats)
        print(
            f"{agent_id}: kept {stats['n_kept']}/{stats['n_total']} "
            f"(dropped {stats['n_dropped']}, {stats['drop_rate']:.1%})",
            file=sys.stderr,
        )

    # A subdirectory, not a sibling *.csv: group_metrics.py globs every *.csv
    # directly under --out as a cleaned-choices file, and this is not one.
    stats_dir = args.out / "_stats"
    stats_dir.mkdir(exist_ok=True)
    stats_df = pd.DataFrame(all_stats)
    stats_df.to_csv(stats_dir / "drop_rates.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
