"""Drives src/evaluate_models.py for one agent on a fixed scenario subset.

Plan.md section 6, step 4. Splits the requested scenarios into chunk CSVs
(evaluate_models.py reads every CSV in --scenarios-dir and saves after each
one finishes, so chunks are what makes a run resumable), strips ERROR rows
from any previous output before resuming (a saved row, even an ERROR one,
counts as done and would otherwise be skipped), and supports --dry-run and
--max-calls so a run can be sized before it spends anything.

One process per agent: calls within a process are sequential
(src/model_wrappers.py), so running agents concurrently means separate
processes, not separate threads.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import pandas as pd
import yaml
from dotenv import load_dotenv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
load_dotenv(os.path.join(REPO_ROOT, ".env"))
SCENARIOS_CSV = os.path.join(
    REPO_ROOT, "data", "personalprotective", "claude-3-5-sonnet-latest.csv"
)

DEFAULT_CHUNK_SIZE = 20
CALLS_PER_SCENARIO = 3  # one forced-choice MCQ call + two Likert calls


def load_agent_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_scenario_ids(path: str) -> list:
    with open(path) as f:
        data = json.load(f)
    return data["scenario_ids"] if isinstance(data, dict) else data


def select_scenarios(scenario_ids: list) -> pd.DataFrame:
    df = pd.read_csv(SCENARIOS_CSV)
    selected = df[df["scenario_id"].isin(scenario_ids)]
    missing = set(scenario_ids) - set(selected["scenario_id"])
    if missing:
        raise ValueError(
            f"{len(missing)} scenario id(s) not found in {SCENARIOS_CSV}: "
            f"{sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}"
        )
    return selected.sort_values("scenario_id").reset_index(drop=True)


def write_chunks(df: pd.DataFrame, chunk_dir: str, chunk_size: int) -> list:
    os.makedirs(chunk_dir, exist_ok=True)
    paths = []
    n_chunks = math.ceil(len(df) / chunk_size)
    for i in range(n_chunks):
        chunk = df.iloc[i * chunk_size : (i + 1) * chunk_size]
        path = os.path.join(chunk_dir, f"chunk_{i:03d}.csv")
        chunk.to_csv(path, index=False)
        paths.append(path)
    return paths


def drop_error_rows(output_file: str) -> None:
    """Strip ERROR rows so a resumed run redoes them instead of skipping them."""
    if not os.path.exists(output_file):
        return
    df = pd.read_csv(output_file)
    if "choice" not in df.columns:
        return
    before = len(df)
    df = df[df["choice"] != "ERROR"]
    dropped = before - len(df)
    if dropped:
        print(f"Dropping {dropped} ERROR row(s) from {output_file} before resuming.")
        df.to_csv(output_file, index=False)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent", required=True, help="Path to an agent YAML config (swarmalign/agents/*.yaml)"
    )
    parser.add_argument(
        "--scenario-ids",
        required=True,
        help="Path to a JSON file holding a list of scenario_id strings",
    )
    parser.add_argument("--output-dir", default="swarmalign/results/choices")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the call count and chunk plan; make no API calls",
    )
    parser.add_argument(
        "--max-calls",
        type=int,
        default=None,
        help="Cap this invocation at roughly this many API calls (truncates the scenario list)",
    )
    parser.add_argument("--force-recompute", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    agent = load_agent_config(args.agent)
    agent_id = agent["id"]
    base_model = agent["base_model"]
    steer_prompt_file = agent.get("system_prompt_file")

    scenario_ids = load_scenario_ids(args.scenario_ids)

    if args.max_calls is not None:
        max_scenarios = max(0, args.max_calls // CALLS_PER_SCENARIO)
        if max_scenarios < len(scenario_ids):
            print(
                f"--max-calls {args.max_calls} caps this run at {max_scenarios} scenario(s) "
                f"of {len(scenario_ids)} requested "
                f"({CALLS_PER_SCENARIO} calls/scenario)."
            )
            scenario_ids = scenario_ids[:max_scenarios]

    df = select_scenarios(scenario_ids)
    n_calls = len(df) * CALLS_PER_SCENARIO
    n_chunks = math.ceil(len(df) / args.chunk_size) if len(df) else 0

    if args.dry_run:
        print(f"[dry-run] agent: {agent_id}  model: {base_model}")
        print(f"[dry-run] scenarios: {len(df)}")
        print(
            f"[dry-run] calls: {n_calls} "
            f"({CALLS_PER_SCENARIO} per scenario: 1 forced choice + 2 Likert ratings, "
            f"<=5 tokens each)"
        )
        print(f"[dry-run] chunks: {n_chunks} of up to {args.chunk_size} scenarios each")
        print("[dry-run] no API calls made")
        return

    os.makedirs(args.output_dir, exist_ok=True)
    output_name = f"{agent_id}.csv"
    output_file = os.path.join(args.output_dir, output_name)

    if not args.force_recompute:
        drop_error_rows(output_file)

    chunk_dir = os.path.join(args.output_dir, f".{agent_id}_chunks")
    if os.path.exists(chunk_dir):
        shutil.rmtree(chunk_dir)
    write_chunks(df, chunk_dir, args.chunk_size)

    cmd = [
        sys.executable,
        "evaluate_models.py",
        "--model", base_model,
        "--scenarios-dir", os.path.abspath(chunk_dir),
        "--output-dir", os.path.abspath(args.output_dir),
        "--output-name", output_name,
        "--temperature", "0.0",
        "--max-tokens", "5",
    ]
    if steer_prompt_file:
        cmd += ["--steer-prompt", os.path.abspath(steer_prompt_file)]
    if args.force_recompute:
        cmd.append("--force-recompute")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=SRC_DIR, check=True)


if __name__ == "__main__":
    main()
