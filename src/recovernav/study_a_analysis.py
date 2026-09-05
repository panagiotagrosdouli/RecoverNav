"""Frozen-analysis helpers for RecoverNav Study A.

These routines are deliberately small and dependency-light. They compare the
structural score against a clearance-only negative control and quantify sampling
uncertainty with a deterministic stratified bootstrap.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass

from .study_a import StudyAObservation, empirical_auc


@dataclass(frozen=True)
class PredictorObservation:
    trial_id: str
    score: float
    recovery_success: bool


@dataclass(frozen=True)
class AucInterval:
    auc: float
    lower: float
    upper: float
    confidence: float
    bootstrap_samples: int


def clearance_only_score(clearances_m: Sequence[float], c_min: float, c_ref: float) -> float:
    """Return a normalized minimum-clearance predictor in [0, 1]."""

    if not clearances_m:
        raise ValueError("clearances_m must not be empty")
    if c_min < 0 or c_ref <= 0:
        raise ValueError("invalid clearance normalization")
    margin = max(0.0, min(clearances_m) - c_min)
    return min(1.0, margin / c_ref)


def predictor_auc(observations: Sequence[PredictorObservation]) -> float:
    adapted = [
        StudyAObservation(
            trial_id=o.trial_id,
            scenario_id="analysis",
            rho_pre_event=o.score,
            recovery_success=o.recovery_success,
        )
        for o in observations
    ]
    return empirical_auc(adapted)


def stratified_bootstrap_auc(
    observations: Sequence[PredictorObservation],
    *,
    confidence: float = 0.95,
    bootstrap_samples: int = 5000,
    seed: int = 20260905,
) -> AucInterval:
    """Estimate an empirical percentile interval for ROC-AUC.

    Success and failure classes are resampled separately so every bootstrap
    replicate remains estimable. The seed is explicit for reproducibility.
    """

    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be positive")

    successes = [o for o in observations if o.recovery_success]
    failures = [o for o in observations if not o.recovery_success]
    if not successes or not failures:
        raise ValueError("bootstrap AUC requires both outcome classes")

    rng = random.Random(seed)
    boot = []
    for _ in range(bootstrap_samples):
        sample = [rng.choice(successes) for _ in successes]
        sample.extend(rng.choice(failures) for _ in failures)
        boot.append(predictor_auc(sample))
    boot.sort()

    alpha = 1.0 - confidence
    lo_index = max(0, int((alpha / 2.0) * bootstrap_samples))
    hi_index = min(
        bootstrap_samples - 1,
        int((1.0 - alpha / 2.0) * bootstrap_samples) - 1,
    )
    return AucInterval(
        auc=predictor_auc(observations),
        lower=boot[lo_index],
        upper=boot[hi_index],
        confidence=confidence,
        bootstrap_samples=bootstrap_samples,
    )
