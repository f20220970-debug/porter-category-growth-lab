"""Simulated Porter-style intra-city logistics data. Nothing here is real Porter data."""
import numpy as np, pandas as pd

CITIES = ["Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai", "Ahmedabad", "Kolkata"]
CATS = {  # base fare INR, demand elasticity, driver price sensitivity, contribution margin
    "2W":        dict(fare=120, elast=-2.4, supply=0.5, margin=.10),
    "3W":        dict(fare=320, elast=-1.7, supply=0.8, margin=.11),
    "Tata Ace":  dict(fare=650, elast=-1.1, supply=1.1, margin=.12),
    "Pickup 8ft":dict(fare=900, elast=-1.0, supply=1.2, margin=.12),
    "Truck 14ft":dict(fare=2400,elast=-0.8, supply=1.4, margin=.13),
}
ARMS = [0.90, 1.00, 1.10, 1.20]


def pricing_experiment(seed=1, blocks=2400):
    """Switchback test: each city x category x 2-hour block gets one price multiplier."""
    r = np.random.default_rng(seed)
    city_supply = dict(zip(CITIES, r.uniform(0.55, 0.85, len(CITIES))))
    rows = []
    for city in CITIES:
        for cat, p in CATS.items():
            for b in range(blocks // 40):
                arm = r.choice(ARMS)
                peak = b % 6 in (1, 4)
                quotes = r.poisson(160 if cat in ("2W", "3W") else 70) * (1.35 if peak else 1)
                conv = np.clip(0.42 * arm ** p["elast"] * r.normal(1, .05), .02, .95)
                bookings = r.binomial(int(quotes), conv)
                base_f = city_supply[city] - (0.12 if peak else 0)
                fulfil = np.clip(base_f + p["supply"] * 0.25 * (arm - 1) * 4 / 4 * (1.6 if cat in ("Tata Ace", "Pickup 8ft", "Truck 14ft") else 1) + r.normal(0, .03), .2, .99)
                fulfilled = r.binomial(bookings, fulfil)
                rows.append((city, cat, b, peak, arm, int(quotes), bookings, fulfilled, p["fare"] * arm, p["margin"]))
    return pd.DataFrame(rows, columns=["city", "category", "block", "peak", "price_mult", "quotes", "bookings", "fulfilled", "fare", "margin"])


CHANNELS = {  # cost per lead INR, stage pass rates (docs, verified, trained, first_trip), M1 retention
    "Referral":           (150, [.70, .85, .90, .80], .62),
    "Field camps":        (260, [.75, .80, .92, .78], .55),
    "Digital ads":        (90,  [.35, .70, .80, .60], .38),
    "Fleet-owner tie-ups":(400, [.85, .90, .95, .90], .70),
}


def partner_funnel(seed=2, leads_per_channel=6000):
    r = np.random.default_rng(seed)
    out = []
    for ch, (cpl, rates, m1) in CHANNELS.items():
        n = leads_per_channel
        stages = [n]
        for p in rates:
            n = r.binomial(n, p); stages.append(n)
        retained = r.binomial(n, m1)
        out.append(dict(channel=ch, leads=stages[0], docs=stages[1], verified=stages[2], trained=stages[3],
                        first_trip=stages[4], m1_retained=retained, spend=cpl * stages[0]))
    return pd.DataFrame(out)


def partners(seed=3, n=12000):
    """New driver-partners with their first-week experience and month-1 retention."""
    r = np.random.default_rng(seed)
    wk_trips = r.poisson(9, n)
    wait_min = r.gamma(3, 6, n)                 # avg idle wait between trips, minutes
    earn = wk_trips * r.normal(420, 60, n)       # first-week earnings INR
    pay_issue = r.random(n) < .14                # payout delay / dispute in week 1
    incentive = r.random(n) < .5                 # got onboarding incentive
    z = -1.6 + .00055 * earn - .045 * wait_min - 1.1 * pay_issue + .35 * incentive
    m1 = r.random(n) < 1 / (1 + np.exp(-z))
    return pd.DataFrame(dict(first_week_trips=wk_trips, avg_wait_min=wait_min.round(1), first_week_earnings=earn.round(0),
                             payout_issue=pay_issue, got_incentive=incentive, m1_active=m1))


ISSUES = {  # share, base minutes, chance it needs a handoff
    "Payout delay":       (.30, 38, .55),
    "Pricing dispute":    (.22, 30, .45),
    "Order cancellation": (.20, 14, .15),
    "App / login":        (.15, 18, .25),
    "Document update":    (.13, 45, .40),
}


def support_tickets(seed=4, n=40000):
    r = np.random.default_rng(seed)
    kinds = list(ISSUES)
    issue = r.choice(kinds, n, p=[ISSUES[k][0] for k in kinds])
    channel = r.choice(["Chat", "Callback"], n, p=[.65, .35])
    base = np.array([ISSUES[k][1] for k in issue]); hp = np.array([ISSUES[k][2] for k in issue])
    handoffs = r.binomial(2, hp)
    queue = np.where(channel == "Callback", r.gamma(2, 22, n), r.gamma(2, 4, n))
    minutes = base * r.lognormal(0, .35, n) + 26 * handoffs + queue
    reopened = r.random(n) < (.06 + .09 * handoffs)
    return pd.DataFrame(dict(issue=issue, channel=channel, handoffs=handoffs, minutes=minutes.round(1), reopened=reopened))


def customers(seed=5, n=30000):
    """SME shippers for the Growth module: order history over 26 weeks."""
    r = np.random.default_rng(seed)
    seg = r.choice(["Kirana / retail", "D2C seller", "Furniture / home", "Individual mover"], n, p=[.35, .25, .15, .25])
    freq = np.select([seg == "Kirana / retail", seg == "D2C seller", seg == "Furniture / home"], [1.6, 1.2, .5], .15)
    first_bad = r.random(n) < .12          # first order had a late or cancelled pickup
    start = r.uniform(0, 22, n)            # week of first order within a 26-week window
    life = r.exponential(np.where(first_bad, 4, 16) * np.where(seg == "Individual mover", .3, 1))
    last = np.minimum(26, start + life)
    orders = r.poisson(freq * (last - start)) + 1
    return pd.DataFrame(dict(segment=seg, first_order_bad=first_bad, orders=orders,
                             weeks_since_last=(26 - last + r.uniform(0, 1, n)).round(1)))
