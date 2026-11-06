import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
import data, run


def test_switchback_arms_balanced():
    df = data.pricing_experiment()
    share = df.price_mult.value_counts(normalize=True)
    assert share.min() > .2 and share.max() < .3


def test_fulfilment_rises_with_price_for_trucks():
    cell, _, _ = run.pricing(data.pricing_experiment())
    t = cell[cell.category == "Truck 14ft"].sort_values("price_mult")
    assert t.fulfilment.is_monotonic_increasing


def test_funnel_is_monotonic():
    f = data.partner_funnel()
    cols = ["leads", "docs", "verified", "trained", "first_trip", "m1_retained"]
    assert (f[cols].diff(axis=1).iloc[:, 1:] <= 0).all().all()


def test_retention_model_beats_chance():
    _, s = run.retention(data.partners())
    assert s["auc"] > .65


def test_redesign_cuts_resolution_time():
    _, s = run.support(data.support_tickets())
    before, after = s["redesign_median_min_before_after"]
    assert after < before
