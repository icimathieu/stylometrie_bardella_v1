import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import cosine_similarity


def summarize(values: np.ndarray) -> Dict[str, float]:
    if values.size == 0:
        return {
            "n_pairs": 0,
            "mean": None,
            "std": None,
            "min": None,
            "p05": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p95": None,
            "max": None,
        }
    return {
        "n_pairs": int(values.size),
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=0)),
        "min": float(np.min(values)),
        "p05": float(np.quantile(values, 0.05)),
        "p25": float(np.quantile(values, 0.25)),
        "median": float(np.quantile(values, 0.50)),
        "p75": float(np.quantile(values, 0.75)),
        "p95": float(np.quantile(values, 0.95)),
        "max": float(np.max(values)),
    }


def pair_values(
    dist: np.ndarray,
    labels: np.ndarray,
    left: str,
    right: str,
) -> np.ndarray:
    if left == right:
        idx = np.where(labels == left)[0]
        if idx.size < 2:
            return np.array([], dtype=float)
        block = dist[np.ix_(idx, idx)]
        triu = np.triu_indices_from(block, k=1)
        return block[triu]

    left_idx = np.where(labels == left)[0]
    right_idx = np.where(labels == right)[0]
    if left_idx.size == 0 or right_idx.size == 0:
        return np.array([], dtype=float)
    block = dist[np.ix_(left_idx, right_idx)]
    return block.ravel()


def pair_values_indices(
    dist: np.ndarray,
    left_idx: np.ndarray,
    right_idx: np.ndarray,
    same_group: bool,
) -> np.ndarray:
    if left_idx.size == 0 or right_idx.size == 0:
        return np.array([], dtype=float)
    if same_group:
        if left_idx.size < 2:
            return np.array([], dtype=float)
        block = dist[np.ix_(left_idx, left_idx)]
        triu = np.triu_indices_from(block, k=1)
        return block[triu]

    block = dist[np.ix_(left_idx, right_idx)]
    return block.ravel()


def bootstrap_balanced(
    dist: np.ndarray,
    labels: np.ndarray,
    runs: int,
    seed: int,
    target_labels: Tuple[str, str, str] = ("E", "O", "C"),
) -> Dict[str, object]:
    idx_by = {lab: np.where(labels == lab)[0] for lab in target_labels}
    if any(v.size == 0 for v in idx_by.values()):
        return {"enabled": True, "error": "At least one target corpus has zero segment."}

    n = int(min(v.size for v in idx_by.values()))
    if n < 2:
        return {"enabled": True, "error": "Need at least 2 segments per target corpus for bootstrap."}

    rng = np.random.default_rng(seed)
    pairs = [("E", "E"), ("O", "O"), ("C", "C"), ("E", "O"), ("E", "C"), ("O", "C")]
    medians = {f"{a}_{b}": [] for a, b in pairs}

    for _ in range(runs):
        sampled = {lab: rng.choice(idx_by[lab], size=n, replace=False) for lab in target_labels}
        for a, b in pairs:
            key = f"{a}_{b}"
            vals = pair_values_indices(dist, sampled[a], sampled[b], same_group=(a == b))
            medians[key].append(float(np.median(vals)))

    def summarize_series(values: List[float]) -> Dict[str, float]:
        arr = np.array(values, dtype=float)
        return {
            "n_runs": int(arr.size),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr, ddof=0)),
            "min": float(np.min(arr)),
            "p025": float(np.quantile(arr, 0.025)),
            "p05": float(np.quantile(arr, 0.05)),
            "p25": float(np.quantile(arr, 0.25)),
            "median": float(np.quantile(arr, 0.50)),
            "p75": float(np.quantile(arr, 0.75)),
            "p95": float(np.quantile(arr, 0.95)),
            "p975": float(np.quantile(arr, 0.975)),
            "max": float(np.max(arr)),
        }

    summary = {k: summarize_series(v) for k, v in medians.items()}

    eo = np.array(medians["E_O"], dtype=float)
    ee = np.array(medians["E_E"], dtype=float)
    oo = np.array(medians["O_O"], dtype=float)
    ec = np.array(medians["E_C"], dtype=float)

    flags_rate = {
        "eo_gt_ee_rate": float(np.mean(eo > ee)),
        "eo_gt_oo_rate": float(np.mean(eo > oo)),
        "ec_lt_eo_rate": float(np.mean(ec < eo)),
    }

    return {
        "enabled": True,
        "runs": int(runs),
        "seed": int(seed),
        "n_per_corpus_per_run": int(n),
        "summary_median_distances": summary,
        "expectation_flags_rate": flags_rate,
    }


def nearest_neighbor_same_rate(dist: np.ndarray, labels: np.ndarray, target: str) -> Dict[str, float]:
    idx = np.where(labels == target)[0]
    if idx.size == 0:
        return {"n_items": 0, "same_label_rate": None}

    d = dist.copy()
    np.fill_diagonal(d, np.inf)
    nn_idx = np.argmin(d, axis=1)
    nn_labels = labels[nn_idx]
    rate = float(np.mean(nn_labels[idx] == target))
    return {"n_items": int(idx.size), "same_label_rate": rate}


def burrows_delta_matrix(x: np.ndarray) -> np.ndarray:
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds[stds == 0] = 1.0
    z = (x - means) / stds
    manhattan = pairwise_distances(z, metric="manhattan")
    return manhattan / z.shape[1]


def build_report(
    df: pd.DataFrame,
    x: np.ndarray,
    feature_family: str,
    bootstrap_runs: int,
    bootstrap_seed: int,
) -> Dict[str, object]:
    labels = df["corpus"].to_numpy()

    cos_sim = cosine_similarity(x)
    cos_dist = 1.0 - cos_sim

    delta_dist = burrows_delta_matrix(x)

    pairs = [("E", "E"), ("O", "O"), ("C", "C"), ("E", "O"), ("E", "C"), ("O", "C")]

    cosine_summary = {}
    delta_summary = {}
    for a, b in pairs:
        key = f"{a}_{b}"
        cosine_summary[key] = summarize(pair_values(cos_dist, labels, a, b))
        delta_summary[key] = summarize(pair_values(delta_dist, labels, a, b))

    subsource_summary = {"cosine_distance": {}, "burrows_delta": {}}
    for corpus in sorted(df["corpus"].unique().tolist()):
        df_c = df[df["corpus"] == corpus]
        subs = sorted(df_c["subsource"].unique().tolist())
        entries_cos = {}
        entries_delta = {}
        for i, s1 in enumerate(subs):
            idx1 = df_c.index[df_c["subsource"] == s1].to_numpy()
            key_same = f"{s1}__{s1}"
            entries_cos[key_same] = summarize(pair_values_indices(cos_dist, idx1, idx1, same_group=True))
            entries_delta[key_same] = summarize(pair_values_indices(delta_dist, idx1, idx1, same_group=True))
            for s2 in subs[i + 1 :]:
                idx2 = df_c.index[df_c["subsource"] == s2].to_numpy()
                key_cross = f"{s1}__{s2}"
                entries_cos[key_cross] = summarize(pair_values_indices(cos_dist, idx1, idx2, same_group=False))
                entries_delta[key_cross] = summarize(pair_values_indices(delta_dist, idx1, idx2, same_group=False))
        subsource_summary["cosine_distance"][corpus] = entries_cos
        subsource_summary["burrows_delta"][corpus] = entries_delta

    # Heuristique simple pour lecture rapide
    def median(s: Dict[str, float]):
        return s["median"] if s and s["median"] is not None else np.nan

    e_e_cos = median(cosine_summary["E_E"])
    o_o_cos = median(cosine_summary["O_O"])
    e_o_cos = median(cosine_summary["E_O"])
    e_c_cos = median(cosine_summary["E_C"])

    e_e_del = median(delta_summary["E_E"])
    o_o_del = median(delta_summary["O_O"])
    e_o_del = median(delta_summary["E_O"])
    e_c_del = median(delta_summary["E_C"])

    quick_flags = {
        "cosine": {
            "eo_gt_ee": bool(e_o_cos > e_e_cos) if np.isfinite(e_o_cos) and np.isfinite(e_e_cos) else None,
            "eo_gt_oo": bool(e_o_cos > o_o_cos) if np.isfinite(e_o_cos) and np.isfinite(o_o_cos) else None,
            "ec_lt_eo": bool(e_c_cos < e_o_cos) if np.isfinite(e_c_cos) and np.isfinite(e_o_cos) else None,
        },
        "burrows_delta": {
            "eo_gt_ee": bool(e_o_del > e_e_del) if np.isfinite(e_o_del) and np.isfinite(e_e_del) else None,
            "eo_gt_oo": bool(e_o_del > o_o_del) if np.isfinite(e_o_del) and np.isfinite(o_o_del) else None,
            "ec_lt_eo": bool(e_c_del < e_o_del) if np.isfinite(e_c_del) and np.isfinite(e_o_del) else None,
        },
    }

    report = {
        "n_segments": int(df.shape[0]),
        "segments_by_corpus": df["corpus"].value_counts().to_dict(),
        "feature_family": feature_family,
        "n_features": int(x.shape[1]),
        "books_in_E": sorted(df.loc[df["corpus"] == "E", "subsource"].unique().tolist()),
        "subsources_in_O": sorted(df.loc[df["corpus"] == "O", "subsource"].unique().tolist()),
        "nearest_neighbor_same_label_rate": {
            "cosine": {
                "E": nearest_neighbor_same_rate(cos_dist, labels, "E"),
                "O": nearest_neighbor_same_rate(cos_dist, labels, "O"),
                "C": nearest_neighbor_same_rate(cos_dist, labels, "C"),
            },
            "burrows_delta": {
                "E": nearest_neighbor_same_rate(delta_dist, labels, "E"),
                "O": nearest_neighbor_same_rate(delta_dist, labels, "O"),
                "C": nearest_neighbor_same_rate(delta_dist, labels, "C"),
            },
        },
        "pairwise_distance_summary": {
            "cosine_distance": cosine_summary,
            "burrows_delta": delta_summary,
        },
        "subsource_distance_summary_within_corpus": subsource_summary,
        "balanced_bootstrap": {
            "cosine_distance": bootstrap_balanced(
                cos_dist,
                labels,
                runs=bootstrap_runs,
                seed=bootstrap_seed,
            ),
            "burrows_delta": bootstrap_balanced(
                delta_dist,
                labels,
                runs=bootstrap_runs,
                seed=bootstrap_seed,
            ),
        },
        "quick_flags_against_pipeline_expectations": quick_flags,
    }

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Etapes 6-7: contrôles internes et comparaisons stylométriques.")
    parser.add_argument(
        "--features-csv",
        default="/Users/mathieu/Documents/CODE/histosef_codes/bardella/data/features/features_char_ngrams.csv",
        help="CSV de features (par défaut: n-grammes caractères).",
    )
    parser.add_argument(
        "--feature-prefix",
        default="cng::",
        help="Préfixe des colonnes de features à utiliser (ex: cng::, fw::, dm::).",
    )
    parser.add_argument(
        "--output-json",
        default="/Users/mathieu/Documents/CODE/histosef_codes/bardella/data/features/stylometry_comparisons_char_ngrams.json",
        help="Fichier JSON de sortie.",
    )
    parser.add_argument(
        "--bootstrap-runs",
        type=int,
        default=1000,
        help="Nombre de runs bootstrap équilibrés E/O/C.",
    )
    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=42,
        help="Seed bootstrap.",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.features_csv)
    feature_cols = [c for c in df.columns if c.startswith(args.feature_prefix)]
    if not feature_cols:
        raise ValueError(f"Aucune colonne de features avec le préfixe: {args.feature_prefix}")

    x = df[feature_cols].to_numpy(dtype=float)
    report = build_report(
        df,
        x,
        feature_family=args.feature_prefix,
        bootstrap_runs=args.bootstrap_runs,
        bootstrap_seed=args.bootstrap_seed,
    )

    out_path = Path(args.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: rapport généré -> {out_path}")
    print(f"Segments: {report['n_segments']} | Features: {report['n_features']}")
    print("Pair keys:", ", ".join(report["pairwise_distance_summary"]["cosine_distance"].keys()))


if __name__ == "__main__":
    main()
