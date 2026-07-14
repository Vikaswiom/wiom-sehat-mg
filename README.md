# सेहत गारंटी — Sehat MG (Quality MG)

CSP-facing screen for **Sehat MG**: the ₹10,000/month guarantee for the **99 active CSPs who are not eligible for Install MG**. They earn it by keeping their **network healthy** instead of by installing connections.

**Live:** https://vikaswiom.github.io/wiom-sehat-mg/

Design system, card rhythm and copy register are inherited verbatim from
[wiom-mbg-kamai-kavach](https://vikaswiom.github.io/wiom-mbg-kamai-kavach/) — same tokens, same
maroon header, same `.card` → bar-with-marker → yellow action card → purple guarantee card stack.

---

## The program in one line

A CSP is put on **exactly one track**, decided **only** by their current Optical Power, and the track is **locked for the month**:

| | **Track A — इलाज** | **Track B — फिट रखना** |
|---|---|---|
| Assigned if | Optical Power **< 75%** | Optical Power **≥ 75%** |
| Graded on | Optical Power **≥ 80%** | समय पर समाधान (Service SLA) **≥ 80%** |
| The other metric | **ignored** | **ignored** |

Payout is **binary** — ₹10,000 or ₹0 — paid **Day-1 of the next month**, in the same run as Install MG.
There is no downside: install/service earnings are untouched.

## URL contract

Same as the Kamai Kavach page:

- `?cspId=a0b6t9` — render that CSP
- `?case=b_red` — render a specific state

Case keys: `a_red · a_amber · a_green · b_red · b_amber · b_green · unclass · offered · pass · miss`

## The 10 states

| # | State | Shown |
|---|---|---|
| 1 | Track A · 🔴 | OP < 75% — weak-connection list, gap to 80 |
| 2 | Track A · 🟠 | OP 75–79% — "बस X% और" |
| 3 | Track A · 🟢 | OP ≥ 80% — "80% पूरा · ₹10,000 पक्का" |
| 4 | Track B · 🔴 | SLA < 75% — open tickets, 4-hr clock |
| 5 | Track B · 🟠 | SLA 75–79% |
| 6 | Track B · 🟢 | SLA ≥ 80% |
| 7 | Unclassified | no telemetry (Tirth Digital) → SLA-only default |
| 8 | Offered | pre-enroll opt-in, single accept |
| 9 | Month-end pass | celebration |
| 10 | Month-end miss | honest, no blame, install pay safe |

RAG bands: **🟢 ≥80 · 🟠 75–79 · 🔴 <75**

## Data

Both metrics come from `PROD_DB.CSP_QUALITY_SERVICE_CSP_QUALITY_SERVICE` — the same engine the CSP
app's **सेवा स्थिति** screen reads.

| Field | Source | Formula / window |
|---|---|---|
| % Optical Power | `TELEMETRY_ROLLUP_RECORDS` | `100 − SUM(OPTICAL_NUMERATOR)/SUM(OPTICAL_DENOMINATOR)×100` · rolling **15** telemetry days (T1) |
| % समय पर समाधान | `COMPLAINT_RESOLUTION_LEDGER` | `COUNT_IF(RESOLVED_WITHIN_TAT)/COUNT(*)×100` · `TAT_WINDOW_HOURS = 4` · **60**-day lookback (M3) |
| Track A/B | OP snapshot — Metabase card **11616** | OP < 75 → A · OP ≥ 75 → B |
| Weak-connection list | OOR daily GSheet · `HOURLY_DEVICE_PING_INFLUX` | hourly, per-customer — **action list only, not the grade** |
| What the app shows | `DAILY_METRIC_SNAPSHOTS` | `T1_OOR_RATE`, `M3_TAT_PASS_RATE`, `LOOKBACK_*` |

App-exact cohort card: **11615** — *"Priority CSPs — % OOR (T1) & % Resolve On Time (M3)"*, collection 1331.

> **Only `a0b6t9` carries real, verified numbers** (1675/3443 pings → OP 51.35%; 186/206 complaints →
> SLA 90.29%, both reproduced to the decimal against the app). Every other CSP on the case switcher is
> **illustrative sample data** — each case note says which is which. Wire `data.json` / a live proxy
> before this goes in front of CSPs.

## Going live

The page computes everything client-side from a `CASES` object. To go live, replace it the same way
the MBG page does: fetch a per-CSP snapshot (`data.json`, or a proxy that queries Metabase per tap),
keyed on `cspId`. Nothing else in the screen changes.

CleverTap poller tokens (identity = `cspid`, capital `Profile`, inline-only):

```
sehat_tagline · sehat_metric_label · sehat_value · sehat_barpct
sehat_rag_text · sehat_rag_color · sehat_rag_bg · sehat_gap_text
sehat_days · sehat_action_text · sehat_delay_text · sehat_track_task
```

## Open decisions (before launch)

1. **The graded window is not the window the screen shows.** Payout grades on a month-end window
   (OP = last 5 days, SLA = last 15-day average); the app shows the quality-service rolling numbers
   (15-day OP, 60-day SLA). A CSP must not be graded on a number the app never displayed — align the
   two, or say so on the screen.
2. **75% split vs 80% target.** A CSP at OP 76% lands in Track B and can win ₹10,000 on SLA alone,
   while their optical never reaches 80%. Confirm this is intended.
3. **Payout source of truth** — spec says OSS/NMS + ticketing; what is live and reproducible is
   `CSP_QUALITY_SERVICE`. Pick one.
4. **Card 11615 vs 11616** — confirm the single canonical cohort/track card.
5. **Tirth Digital** (no telemetry, 221 customers) — SLA-only default (as rendered) or manual.
6. **Deep-link** — the CTA lands on HOME only; the tappable ONT/ticket screen is a Phase-2 app build
   (`CI_BANNER` route reserved, not wired).
