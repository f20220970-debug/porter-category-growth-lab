# Category playbook (built on the simulated results in this repo)

## A. Partner acquisition: playbooks for the two cheapest channels

### Referral (₹563 per month-1-retained partner)
- **Who refers:** partners with 4+ weeks of activity and a rating of 4.7 or above. Their referrals arrive pre-screened.
- **Reward:** split, with half paid at the referee's first trip and half when the referee completes 20 trips in month 1. That pays for retention, not sign-ups.
- **Fix the leak (30% lost before documents):** in-app document upload with the referrer named on the screen, plus a WhatsApp reminder at 24 and 72 hours.
- **SOP for opportunity mining:** each week, list the cities × categories where fulfilment is below 65% (from the pricing module) and run referral pushes there first.
- **Track weekly:** referral leads, document completion %, first-trip %, M1 %, cost per M1 partner.

### Fleet-owner tie-ups (₹895 per M1 partner, 64.7% lead → first trip)
- **Target:** owners with 5+ vehicles in truck categories, where fulfilment gains are worth the most.
- **Offer:** a single onboarding day for the whole fleet, batch document verification, and a weekly payout statement per vehicle.
- **Risk:** concentration. Cap any one owner at 10% of a city's truck supply.
- **SOP:** an owner-level dashboard (vehicles onboarded, active, trips, cancellations) reviewed every fortnight.

## B. Driver-support flow redesign

| Issue | Today | Redesign |
| --- | --- | --- |
| Payout delay | 1.1 handoffs on average, 76–108 min | Self-serve payout status (expected date, reason); one finance owner; chat only |
| Pricing dispute | 0.9 handoffs, 62–95 min | Show the fare breakup in-app; the agent can approve adjustments up to a limit with no handoff |
| Document update | 0.8 handoffs, 75–108 min | Re-upload flow with an auto-check; human review only on failure |
| Order cancellation, app/login | short already | No change; monitor |

**Success metrics:** median resolution time, % resolved with 0 handoffs, reopen rate within 7 days, and the M1 retention of partners who raised a ticket in week 1.

**Test design:** roll out city by city (stepped wedge) so each city is its own before/after and is compared with cities not yet switched.

## C. New category launch: decision checklist

1. **Demand proof:** search and quote volume for the category over 4 weeks; share of quotes lost to "vehicle not available".
2. **Pricing benchmark:** competitor fares for 5 standard routes per city at peak and off-peak; set the launch price inside that band and test ±10% by switchback from week 2.
3. **Supply readiness:** partners needed = peak bookings per hour × average trip time ÷ target utilisation; do not launch a city below that.
4. **Experience benchmark:** time to allocate, on-time pickup %, cancellations, damage claims, against the closest existing category.
5. **Go / no-go after 6 weeks:** fulfilment ≥ 75%, contribution per order positive after incentives, repeat rate in 30 days at least as high as the closest category.
