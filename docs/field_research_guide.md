# Field research guide: testing each finding with drivers, customers and internal teams

The simulations in this repo show **where** things break. Conversations show **why**. Before acting on any finding, I'd test it with the people involved. This guide is the plan for doing that.

## 1. Who to talk to (sampled from the data, not by convenience)

| Finding to test | Talk to | How many |
| --- | --- | --- |
| A week-1 payout issue halves M1 retention | New partners who churned after a payout ticket; new partners still active after one | 10 + 10 |
| Digital-ads leads drop at document upload (66%) | Leads who started but did not finish documents | 10 |
| Trucks are under-priced at peak | Truck partners who decline peak requests; SME customers who book trucks weekly | 8 + 8 |
| Handoffs drive support time | Support agents on payout and pricing queues; partners with reopened tickets | 5 + 10 |
| A bad first order kills customer retention | Customers whose first pickup was late or cancelled and who never returned | 10 |

## 2. How to run a driver conversation (10 minutes, at a hub or waiting point, in the driver's language)

1. **Start from a real event, not an opinion:** "Tell me about the last time your payout was late. What did you do first?"
2. **Follow the money and the time:** "How much did you expect? When did it arrive? What did you do while waiting?"
3. **Ask about alternatives:** "On days when Porter is slow, where else do you get trips?"
4. **Ask about the decision that matters:** "What would make you stop driving with Porter? What nearly did?"
5. **Close:** "If you could change one thing in the app tomorrow, what would it be?"

Avoid leading questions ("Would a payout guarantee help?") and hypotheticals ("Would you pay more for…?").

## 3. Internal teams to involve

| Team | What to bring them | What to ask |
| --- | --- | --- |
| Customer / partner support | The handoff analysis and redesign | Which issues they can close without a handoff today, and what blocks the rest |
| Design | The document-upload leak and the support redesign | A low-fidelity flow to test with 5 partners before building |
| Data analytics | The pricing and retention findings | Whether real event data shows the same pattern, and what's missing from the simulation |
| City operations | The pricing playbook per city × category | Local factors the data misses (festivals, market days, permit rules for trucks) |

## 4. From conversations back to numbers

- Group the notes into themes; a theme counts when 3 or more people raise it independently.
- Turn each theme into a testable hypothesis with a metric: "a payout-status screen will cut payout tickets 30% and lift M1 retention 5 points".
- Run it as an experiment (switchback for pricing, city-by-city rollout for support), then return to the same people to check whether it felt better on the ground.
