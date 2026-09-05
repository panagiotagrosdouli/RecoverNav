import math

import pytest

from recovernav.study_a_analysis import (
    PredictorObservation,
    clearance_only_score,
    predictor_auc,
    stratified_bootstrap_auc,
)


def test_clearance_only_score_uses_weakest_clearance():
    assert math.isclose(clearance_only_score([0.50, 0.35, 0.60], 0.20, 0.30), 0.5)


def test_clearance_only_score_clips_infeasible_and_wide_routes():
    assert clearance_only_score([0.19, 0.80], 0.20, 0.30) == 0.0
    assert clearance_only_score([0.80, 0.90], 0.20, 0.30) == 1.0


def test_predictor_auc_perfect_ordering():
    observations = [
        PredictorObservation("f1", 0.1, False),
        PredictorObservation("f2", 0.2, False),
        PredictorObservation("s1", 0.8, True),
        PredictorObservation("s2", 0.9, True),
    ]
    assert predictor_auc(observations) == 1.0


def test_bootstrap_is_reproducible_and_bounded():
    observations = [
        PredictorObservation("f1", 0.1, False),
        PredictorObservation("f2", 0.3, False),
        PredictorObservation("f3", 0.6, False),
        PredictorObservation("s1", 0.4, True),
        PredictorObservation("s2", 0.8, True),
        PredictorObservation("s3", 0.9, True),
    ]
    a = stratified_bootstrap_auc(observations, bootstrap_samples=200, seed=7)
    b = stratified_bootstrap_auc(observations, bootstrap_samples=200, seed=7)
    assert a == b
    assert 0.0 <= a.lower <= a.auc <= a.upper <= 1.0


def test_bootstrap_rejects_one_class():
    with pytest.raises(ValueError):
        stratified_bootstrap_auc([PredictorObservation("s", 0.9, True)], bootstrap_samples=10)
