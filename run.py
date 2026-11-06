"""Porter Category & Growth Lab: runs all five modules on simulated data and writes results/*.csv + results/summary.json.

Modules
1. Pricing x fulfilment%  - switchback price test per city x category, pick the price that maximises fulfilled contribution
2. Partner acquisition    - onboarding funnel and cost per month-1-retained partner by channel
3. Partner M1 retention   - what in a partner's first week predicts month-1 retention
4. Driver-support flows   - where chat / callback resolution loses time, and the impact of a redesign
5. User growth            - customer retention by segment, dormant base sizing for reactivation
"""
import json, os, sys
import numpy as np, pandas as pd, duckdb
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import data  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(0)


# ---------- 1. Pricing x fulfilment ----------
def pricing(df):
    df = df.assign(contrib=df.fulfilled * df.fare * df.margin)
    cell = duckdb.sql("""
        select category, price_mult, sum(quotes) quotes, sum(bookings) bookings, sum(fulfilled) fulfilled,
               sum(contrib) contrib
        from df group by all order by category, price_mult""").df()
    cell["conversion"] = cell.bookings / cell.quotes
    cell["fulfilment"] = cell.fulfilled / cell.bookings
    cell["fulfilled_per_100_quotes"] = 100 * cell.fulfilled / cell.quotes
    cell["contrib_per_100_quotes"] = 100 * cell.contrib / cell.quotes

    # best price per city x category, with a block bootstrap so the call is not noise
    picks = []
    for (city, cat), g in df.groupby(["city", "category"]):
        blocks = {a: gg for a, gg in g.groupby("price_mult")}
        def score(gs):
            return {a: 100 * s.contrib.sum() / s.quotes.sum() for a, s in gs.items()}
        base = score(blocks)
        best = max(base, key=base.get)
        wins = 0
        for _ in range(300):
            bs = {a: s.sample(len(s), replace=True, random_state=int(rng.integers(1e9))) for a, s in blocks.items()}
            sc = score(bs)
            wins += max(sc, key=sc.get) == best
        picks.append(dict(city=city, category=cat, best_mult=best, confidence=wins / 300,
                          contrib_best=base[best], contrib_current=base[1.0],
                          uplift_pct=100 * (base[best] / base[1.0] - 1)))
    picks = pd.DataFrame(picks)
    confident = picks[picks.confidence >= .8]
    # portfolio uplift if we move only the confident cells, weighted by current contribution
    w = picks.contrib_current
    moved = np.where(picks.confidence >= .8, picks.contrib_best, picks.contrib_current)
    portfolio_uplift = 100 * (moved.sum() / w.sum() - 1)
    return cell, picks, dict(
        cells=len(picks), confident_cells=len(confident),
        cells_raise_price=int((confident.best_mult > 1).sum()), cells_cut_price=int((confident.best_mult < 1).sum()),
        portfolio_contrib_uplift_pct=round(portfolio_uplift, 1),
        fulfilment_2W_at_0_9_vs_1_2=[round(cell.query("category=='2W' and price_mult==0.9").fulfilment.iat[0] * 100, 1),
                                      round(cell.query("category=='2W' and price_mult==1.2").fulfilment.iat[0] * 100, 1)],
        fulfilment_truck_at_0_9_vs_1_2=[round(cell.query("category=='Truck 14ft' and price_mult==0.9").fulfilment.iat[0] * 100, 1),
                                         round(cell.query("category=='Truck 14ft' and price_mult==1.2").fulfilment.iat[0] * 100, 1)],
    )


# ---------- 2. Partner acquisition ----------
def acquisition(f):
    f = f.copy()
    f["lead_to_first_trip_pct"] = 100 * f.first_trip / f.leads
    f["cost_per_first_trip"] = f.spend / f.first_trip
    f["cost_per_m1_partner"] = f.spend / f.m1_retained
    stages = ["leads", "docs", "verified", "trained", "first_trip"]
    drops = []
    for _, r in f.iterrows():
        losses = {f"{a}->{b}": 1 - r[b] / r[a] for a, b in zip(stages, stages[1:])}
        k = max(losses, key=losses.get)
        drops.append(f"{k} ({losses[k]*100:.0f}% lost)")
    f["biggest_drop"] = drops
    f = f.sort_values("cost_per_m1_partner")
    return f, dict(cheapest_channels=f.channel.head(2).tolist(),
                   cost_per_m1_partner={r.channel: round(r.cost_per_m1_partner) for r in f.itertuples()},
                   digital_ads_biggest_drop=f.set_index("channel").biggest_drop["Digital ads"])


# ---------- 3. Partner M1 retention ----------
def retention(p):
    X = p[["first_week_trips", "avg_wait_min", "first_week_earnings", "payout_issue", "got_incentive"]].astype(float)
    y = p.m1_active
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.3, random_state=0, stratify=y)
    mu, sd = Xtr.mean(), Xtr.std()
    m = LogisticRegression(max_iter=500).fit((Xtr - mu) / sd, ytr)
    auc = roc_auc_score(yte, m.predict_proba((Xte - mu) / sd)[:, 1])
    coefs = pd.Series(m.coef_[0], index=X.columns).sort_values()
    p = p.assign(earn_band=pd.cut(p.first_week_earnings, [-1, 2000, 3500, 5000, 1e9], labels=["<2K", "2-3.5K", "3.5-5K", "5K+"]))
    band = p.groupby("earn_band", observed=True).m1_active.mean()
    pay = p.groupby("payout_issue").m1_active.mean()
    return coefs, dict(m1_rate=round(y.mean() * 100, 1), auc=round(auc, 3),
                       m1_by_first_week_earnings={k: round(v * 100, 1) for k, v in band.items()},
                       m1_with_vs_without_payout_issue=[round(pay[True] * 100, 1), round(pay[False] * 100, 1)],
                       strongest_negative_driver=coefs.index[0])


# ---------- 4. Driver-support flows ----------
def support(t):
    by = duckdb.sql("""
        select issue, channel, count(*) n, median(minutes) median_min, avg(handoffs) avg_handoffs,
               avg(reopened::int) reopen_rate
        from t group by all order by issue, channel""").df()
    h = t.groupby("handoffs").minutes.median()
    # redesign: payout + pricing disputes get a self-serve status screen and a one-step owner (no handoff),
    # callbacks for those issues move to chat. Re-score the same tickets.
    t2 = t.copy()
    target = t2.issue.isin(["Payout delay", "Pricing dispute"])
    t2.loc[target, "minutes"] -= 26 * t2.loc[target, "handoffs"]
    t2.loc[target & (t2.channel == "Callback"), "minutes"] *= .7
    t2.loc[target, "handoffs"] = 0
    before, after = t.minutes.median(), t2.minutes.median()
    reopen_before = t.reopened.mean()
    reopen_after = (0.06 + 0.09 * t2.handoffs).mean()
    return by, dict(tickets=len(t), median_min_by_handoffs={int(k): round(v, 1) for k, v in h.items()},
                    callback_vs_chat_median=[round(t[t.channel == "Callback"].minutes.median(), 1),
                                             round(t[t.channel == "Chat"].minutes.median(), 1)],
                    redesign_median_min_before_after=[round(before, 1), round(after, 1)],
                    redesign_reopen_rate_before_after=[round(reopen_before * 100, 1), round(reopen_after * 100, 1)])


# ---------- 5. User growth ----------
def growth(c):
    c = c.assign(status=np.select([c.weeks_since_last <= 4, c.weeks_since_last <= 12], ["Active", "At risk"], "Dormant"))
    seg = pd.crosstab(c.segment, c.status, normalize="index").round(3) * 100
    bad = c.groupby("first_order_bad").apply(lambda g: (g.status == "Active").mean(), include_groups=False)
    dormant = c[c.status == "Dormant"]
    worth = dormant[dormant.orders >= 5]
    return seg, dict(customers=len(c), dormant_pct=round((c.status == "Dormant").mean() * 100, 1),
                     active_after_bad_vs_good_first_order=[round(bad[True] * 100, 1), round(bad[False] * 100, 1)],
                     dormant_high_value=int(len(worth)),
                     dormant_high_value_segments=worth.segment.value_counts().head(2).to_dict())


def main():
    cell, picks, s1 = pricing(data.pricing_experiment())
    fun, s2 = acquisition(data.partner_funnel())
    coefs, s3 = retention(data.partners())
    sup, s4 = support(data.support_tickets())
    seg, s5 = growth(data.customers())
    cell.round(3).to_csv(f"{OUT}/pricing_by_category_arm.csv", index=False)
    picks.round(3).to_csv(f"{OUT}/pricing_recommendation_by_city_category.csv", index=False)
    fun.round(1).to_csv(f"{OUT}/partner_acquisition_funnel.csv", index=False)
    coefs.round(3).to_csv(f"{OUT}/partner_m1_drivers.csv")
    sup.round(3).to_csv(f"{OUT}/support_flows.csv", index=False)
    seg.to_csv(f"{OUT}/customer_status_by_segment.csv")
    summary = dict(pricing=s1, acquisition=s2, partner_retention=s3, support=s4, growth=s5)
    with open(f"{OUT}/summary.json", "w") as fh:
        json.dump(summary, fh, indent=1, default=str)
    print(json.dumps(summary, indent=1, default=str))
    return summary


if __name__ == "__main__":
    main()
