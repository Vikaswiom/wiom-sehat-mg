# सेहत गारंटी — Sehat MG (Quality MG)

The CSP-facing screen for **Sehat MG**: the ₹10,000/month guarantee for active CSPs who are **not eligible for Install MG**. They earn it by keeping their **network healthy** instead of by installing connections.

**Live:** https://vikaswiom.github.io/wiom-sehat-mg/?cspId=a0b6t9

Design system, card rhythm and copy register are inherited verbatim from
[wiom-mbg-kamai-kavach](https://vikaswiom.github.io/wiom-mbg-kamai-kavach/).

---

## How it renders

The page is opened with a CSP id and fetches that CSP's real numbers:

```
/?cspId=a0b6t9      →  Track A · Optical Power 49%  (1,683 of 3,450 pings OK)
/?cspId=a0a6y4      →  Track B · समय पर समाधान 86%  (165 of 191 within 4h)
```

Accepts `cspId`, `cspid`, `csp_id` or `id`, any casing. Unknown id → a calm
"आपका हिसाब अभी तैयार नहीं है" state, never a fabricated number.

A CSP is on **exactly one track**, decided **only** by their Optical Power at month start, and the track is **locked for the month**:

| | **Track A — इलाज** | **Track B — फिट रखना** |
|---|---|---|
| Assigned if | Optical Power **< 75%** | Optical Power **≥ 75%** |
| Graded on | Optical Power **≥ 80%** | समय पर समाधान **≥ 80%** |
| The other metric | **ignored** | **ignored** |

Payout is **binary** — ₹10,000 or ₹0 — paid **Day-1 of the next month**, same run as Install MG.
No downside: install and service earnings are untouched. The screen says all of this out loud,
because "only one number counts" is the single most confusable thing about the program.

RAG: **🟢 ≥80 · 🟠 75–79 · 🔴 <75**

---

## ⚠️ The formula in the program note is inverted

`SEHAT_MG_LOGIC.md` states `% Optical Power = 100 − T1_OOR_RATE`. **That is backwards.**

```
% Optical Power = OPTICAL_NUMERATOR / OPTICAL_DENOMINATOR      ← share of IN-RANGE pings
                = T1_OOR_RATE                                   (NOT 100 − T1_OOR_RATE)
```

`T1_OOR_RATE` is an **OK-rate despite its name**. The proof is the service's own banding:

| Band | `T1_OOR_RATE` range | | Band | `T2_SPEED_OK_RATE` range |
|---|---|---|---|---|
| VG | 95.1 – 100 | | VG | 90 – 100 |
| GOOD | 90 – 94.9 | | GOOD | 85.1 – 89.9 |
| BASE | below | | BASE | below |

T1 bands **identically to T2**, and `T2_SPEED_OK_RATE` is unambiguously "higher is better".
If T1 really were an out-of-range rate, the service would be calling *95–100% of pings out of range*
"very good", which is nonsense.

**Why the note got it wrong:** its `[VERIFIED]` proof used `a0b6t9`, which sits at ~49% — the one
place on the scale where an inversion is nearly invisible (48.65 vs 51.35 both look plausible).

**What it costs if you ship the inverted version:** median Optical Power reads as 24% instead of 76%,
and **986 of 1,053 CSPs** get dumped into Track A. With the correct formula the split is **485 A /
513 B / 55 unclassified** — near-even, which is exactly the character the note's own cohort shows
(50 A / 48 B). That corroboration is the second, independent check.

---

## Data

| Field | Source | Formula / window |
|---|---|---|
| % Optical Power | `TELEMETRY_ROLLUP_RECORDS` | `SUM(OPTICAL_NUMERATOR)/SUM(OPTICAL_DENOMINATOR)×100` · rolling **15** telemetry days (T1) |
| % समय पर समाधान | `COMPLAINT_RESOLUTION_LEDGER` | `COUNT_IF(RESOLVED_WITHIN_TAT)/COUNT(*)×100` · `TAT_WINDOW_HOURS = 4` · each CSP's own **60**-day snapshot lookback (M3) |
| Track A/B/U | `DAILY_METRIC_SNAPSHOTS` | Optical Power on the **1st of the month** · <75 → A · ≥75 → B · no telemetry → U |
| Active connections | `DAILY_METRIC_SNAPSHOTS` | `ACTIVE_CONNECTION_COUNT` |

All in `PROD_DB.CSP_QUALITY_SERVICE_CSP_QUALITY_SERVICE` — the same engine the CSP app's
**सेवा स्थिति** screen reads. Recomputed from source (not read off the snapshot) so the screen can
show each CSP the same numerator/denominator their ₹10,000 is graded on. Agreement with the
snapshot: mean |diff| **0.29 pt**, within 0.5 pt for **866/997** CSPs.

### Refresh

```bash
python refresh.py      # runs query.sql → writes data.json   (needs C:\credentials\.env)
```

`data.json` = `{meta, data: {"<cspId>": {ok, all, sok, stot, cn, tr, op0}}}` — **raw inputs only**,
77 KB, 1,053 CSPs. Every displayed number (%, gap to 80, bar width, RAG) is derived client-side,
so there is no second place for the formula to drift.

**Going live per tap:** set `PROXY_URL` in `index.html` to an Apps Script `/exec` that queries
Metabase for the requested `cspId`. It returns the same raw shape; nothing else changes.

---

## Known gaps

1. **The graded window is not the window the screen shows.** Payout grades on a month-end window
   (OP = last 5 days, SLA = last 15-day average); the screen shows the quality-service rolling
   numbers (15-day OP, 60-day SLA). A CSP must not be graded on a number the app never displayed —
   align the two, or state it on the screen.
2. **No live open-ticket feed.** Every unresolved row in `COMPLAINT_RESOLUTION_LEDGER` is **7+ days
   old** (567 aged 7–30d, 432 over 30d, **zero** under 24h), so those are stale hygiene artifacts,
   not a work queue. Track B's action card is therefore built on the real breach count, not a fake
   4-hour countdown. A genuine open-ticket list needs the ops ticketing system.
3. **75% split vs 80% target.** A CSP at OP 76% lands in Track B and can bank ₹10,000 on SLA alone
   while their optical never reaches 80%. Confirm this is intended.
4. **Payout source of truth** — the note says OSS/NMS + ticketing; what is live and reproducible is
   `CSP_QUALITY_SERVICE`. Pick one.
5. **55 CSPs have no optical telemetry** and cannot be track-assigned. They currently default to
   SLA-only (Track B). Confirm, or handle manually.
6. **Enrollment** is not wired — the screen assumes the CSP is already in. Reuse the Install-MG
   single-accept flow.
