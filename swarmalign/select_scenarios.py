"""Builds the fixed, committed scenario subsets for the real run.

Plan.md section 6, step 3: 400 ids from the kept scenarios, stratified so
value pairs are represented as evenly as possible, plus a nested subset of
200 for the validation agents.

Only 16 of the 28 possible value pairs have any kept scenario in
data/personalprotective/claude-3-5-sonnet-latest.csv (checked directly,
2026-11-08) -- plan.md's "28 value pairs" is the combinatorial upper bound,
not what ConflictScope actually generated and kept. Stratification below is
therefore over those 16 observed pairs, equal allocation per pair, not the
full 28.
"""
import json
import random
from pathlib import Path

import pandas as pd

SCENARIOS_CSV = "data/personalprotective/claude-3-5-sonnet-latest.csv"
SEED = 0
N_MAIN = 400
N_VALIDATION = 200
OUT_DIR = Path("swarmalign")


def main() -> None:
    df = pd.read_csv(SCENARIOS_CSV)
    kept = df[df["keep_scenario"] == True].copy()
    kept["pair"] = kept.apply(lambda r: tuple(sorted((r["value1"], r["value2"]))), axis=1)

    pairs = sorted(kept["pair"].unique())
    n_pairs = len(pairs)
    per_pair_main = N_MAIN // n_pairs  # 400 // 16 = 25
    per_pair_val = N_VALIDATION // n_pairs  # 200 // 16 = 12
    extra_val_pairs = N_VALIDATION - per_pair_val * n_pairs  # pairs that get 13 instead of 12

    rng = random.Random(SEED)
    main_ids, validation_ids = [], []
    pair_report = []

    for i, pair in enumerate(pairs):
        pool = kept[kept["pair"] == pair]["scenario_id"].tolist()
        if len(pool) < per_pair_main:
            raise ValueError(f"pair {pair} has only {len(pool)} kept scenarios, need {per_pair_main}")
        rng.shuffle(pool)
        chosen_main = sorted(pool[:per_pair_main])
        main_ids.extend(chosen_main)

        n_val_this_pair = per_pair_val + (1 if i < extra_val_pairs else 0)
        validation_ids.extend(chosen_main[:n_val_this_pair])

        pair_report.append(
            {"pair": list(pair), "n_kept": len(pool), "n_main": len(chosen_main), "n_validation": n_val_this_pair}
        )

    assert len(main_ids) == N_MAIN, len(main_ids)
    assert len(validation_ids) == N_VALIDATION, len(validation_ids)
    assert set(validation_ids) <= set(main_ids), "validation subset must nest inside main"

    (OUT_DIR / "scenarios_main_400.json").write_text(json.dumps(sorted(main_ids), indent=2))
    (OUT_DIR / "scenarios_validation_200.json").write_text(json.dumps(sorted(validation_ids), indent=2))
    (OUT_DIR / "scenarios_subset_meta.json").write_text(
        json.dumps(
            {
                "source_csv": SCENARIOS_CSV,
                "seed": SEED,
                "n_main": N_MAIN,
                "n_validation": N_VALIDATION,
                "n_pairs_observed": n_pairs,
                "pairs": pair_report,
            },
            indent=2,
        )
    )
    print(f"{n_pairs} pairs, {per_pair_main}/pair main, wrote {N_MAIN} main + {N_VALIDATION} nested validation ids")


if __name__ == "__main__":
    main()
