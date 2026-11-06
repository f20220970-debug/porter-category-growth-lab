# Porter Category & Growth Lab

[![tests](https://github.com/f20220970-debug/porter-category-growth-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/f20220970-debug/porter-category-growth-lab/actions/workflows/tests.yml)

Built for **Porter's PS-II Business Intern roles (Category and Growth)**. It works through the five project areas in the Category JD (pricing × fulfilment%, partner acquisition, partner M1 retention, driver-support flows) and the Growth JD (retention and dormant-base reactivation) on one simulated intra-city logistics marketplace.

> **All data is simulated** (8 cities, 5 vehicle categories, made-up demand and supply behaviour). Nothing here is Porter data. The numbers show the method and the kind of decision each analysis supports, not facts about Porter.

Run it: `pip install -r requirements.txt && python run.py && pytest -q` (≈15 s). Results land in `results/`.

## 1. Pricing × fulfilment% (switchback price test)

Every city × category × 2-hour block gets one price multiplier (0.9, 1.0, 1.1 or 1.2). A higher price lowers quote-to-booking conversion but raises fulfilment, because more driver-partners accept. The metric that balances both is **contribution per 100 quotes**, and each city × category's winner is bootstrapped 300 times so that noise doesn't decide.

| Category | Fulfilment at 0.9× → 1.2× | Call |
| --- | --- | --- |
| 2W | 65.5% → 69.9% (barely moves) | **Cut price 10%** in all 8 cities: demand is elastic, and supply is already there |
| Truck 14ft | 61.9% → 77.4% (68.0% at today's 1.0×) | **Raise price**: fulfilment gain outweighs lost bookings (7 of 8 cities at 1.2×) |
| Tata Ace / Pickup | rises steadily | Raise 10–20% depending on the city |

- 24 of 40 city × category cells have a winner with at least 80% bootstrap confidence: 16 raise price, 8 cut it.
- Moving only those 24 cells lifts contribution per 100 quotes by **13%**.
- 1.2× is the top tested arm for trucks, so the next test should try 1.25–1.3× before calling that the ceiling.

`results/pricing_recommendation_by_city_category.csv` is the per-cell playbook.

## 2. Partner acquisition: which two channels to invest in

| Channel | Lead → first trip | Cost per M1-retained partner | Biggest leak |
| --- | --- | --- | --- |
| Referral | 42.6% | **₹563** | leads → documents (30%) |
| Fleet-owner tie-ups | 64.7% | **₹895** | leads → documents (15%) |
| Field camps | 42.4% | ₹1,113 | leads → documents (26%) |
| Digital ads | 11.9% | ₹1,895 | leads → documents (**66%**) |

Digital ads have the cheapest leads (₹90) but the most expensive retained partner, because two-thirds never upload documents. Referral and fleet-owner tie-ups get the playbooks in `docs/category_playbook.md`.

## 3. Partner M1 retention

A logistic model on 12,000 new partners (AUC **0.72** on a held-out 30%) shows what in week 1 predicts being active in month 1:

- **First-week earnings:** M1 retention goes from **21%** (under ₹2K) to **68%** (₹5K+).
- **A payout problem in week 1** halves retention: **24% vs 47%**.
- **Idle waiting time** between trips is the strongest negative driver.

What to do: guarantee a first-week earnings floor, route new partners to dense demand zones, and fix week-1 payouts first.

## 4. Driver-support flow redesign (chat and callback)

Across 40,000 simulated tickets, the median resolution time is **38 min with no handoff, 73 min with one and 103 min with two**. Callbacks take **91 min** vs **57 min** for chat. Payout delays and pricing disputes carry the most handoffs.

The redesign gives those two issues a self-serve status screen and a single owner (no handoff) and moves their callbacks to chat. Re-scored on the same tickets, the median falls from **67 to 47 min**, and the projected reopen rate falls from 12.9% to 8.1%. The reopen figure comes from the simulation's assumptions, so treat it as a hypothesis to test.

## 5. User growth: retention and the dormant base

Customers are SME shippers and individual movers (30,000 in all):

- **Dormant base:** 30.7% have placed no order in 12+ weeks.
- **A bad first order is the clearest warning sign:** only **13%** of customers whose first pickup was late or cancelled are still active, vs **45%** otherwise.
- **2,795 dormant customers had 5+ orders,** mostly kirana/retail and D2C sellers. They're the reactivation target, since a past habit is easier to restart than a new one.

The deeper method for this (uplift modelling, holdouts, loyalty ROI) is in the companion repo [retention-uplift-engine](https://github.com/f20220970-debug/retention-uplift-engine). The pricing method is in [marketplace-pricing-experiments](https://github.com/f20220970-debug/marketplace-pricing-experiments).

## Files

```
run.py                  all five modules -> results/
src/data.py             the simulator (assumptions are in the code, in one place)
docs/category_playbook.md   acquisition playbooks, support redesign, new-category launch checklist
docs/field_research_guide.md  how to test each finding with drivers, customers, support, design and data teams
tests/test_lab.py       5 checks (balanced arms, monotonic funnel, model beats chance, ...)
```
