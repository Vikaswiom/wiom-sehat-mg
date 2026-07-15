# सेहत गारंटी — Sehat MG (Quality MG)

The CSP-facing screen for **Sehat MG**: the ₹10,000/month guarantee for active CSPs who are **not eligible for Install MG**. They earn it by keeping their **network healthy** instead of by installing connections.

**Live:** https://vikaswiom.github.io/wiom-sehat-mg/?cspId=a0b6t9

Design system, card rhythm and copy register are inherited verbatim from
[wiom-mbg-kamai-kavach](https://vikaswiom.github.io/wiom-mbg-kamai-kavach/).

Logic audited against the program note `Sehat_MG_Quality_Program.html` (Version 2.0, July 2026).
Every case below matches the spec; deviations are called out in **Known gaps**.

---

## Spec conformance — every case

Audited against `Sehat_MG_Quality_Program.html`:

| Spec rule | Where | Screen |
|---|---|---|
| % Optical Power = in-range OK pings ÷ total, 15 telemetry days | §10 | `ok/all` ✅ |
| % Resolve On Time = within-4hr ÷ total, 60-day lookback | §10 | `sok/stot` ✅ |
| Track split: OP <75 → A (Ilaaj), ≥75 → B (Fit rakhna) | §4, §10 | month-start OP ✅ |
| Both tracks target 80%; only the track's one metric is graded | §4, §5 | ✅ stated explicitly |
| RAG: 🟢 healthy ≥80 · 🟠 within 5% (75–79) · 🔴 <75 | §7 | ✅ |
| **Grade window: Track A = last 5 days · Track B = last 15 days** | §5 | ✅ named in guarantee card; delay card steps up when inside it |
| Binary ₹10,000, Day-1 next month, same run as Install MG | §5 | ✅ |
| Unclassified (no telemetry) → SLA-only default | §10 | ✅ "🩺 सर्विस ट्रैक" — does **not** claim the network is "fit" |
| Track B message: "network already healthy — keep it *and* sharpen service" | §4 callout | ✅ |
| Daily checkup: current %, 80% line, RAG, days left, one next action | §7 | ✅ |

The seven live states (Track A/B × 🔴🟠🟢, plus Unclassified) all render from `data.json`; offer →
sign-up → pass/fail are lifecycle states handled by the Install-MG enrollment + payout runs (§6),
not by this daily tile.

---

## ⚠️ How the app must open this page

**A bare link does not become dynamic on its own.**

```
https://vikaswiom.github.io/wiom-sehat-mg              ❌ page cannot know who tapped it
https://vikaswiom.github.io/wiom-sehat-mg/?cspId=a0b6t9  ✅
```

The page has no way to identify the viewer — it can only read an id that is **already in the URL it
was opened with**. Whatever the app / CleverTap campaign does today to build the Kamai Kavach link
(`?cspId=a0b6f0`), it must do the same here. In a CleverTap campaign that is the profile token:

```
https://vikaswiom.github.io/wiom-sehat-mg/?cspId={{Profile.cspid}}
```

Opened with no id, the page shows a calm *"ये पेज आपकी CSP ID के साथ खुलता है"* state — it never
invents a number.

**To make the wiring impossible to get wrong, the id is accepted in any of these shapes:**

| # | Shape | Example |
|---|---|---|
| 1 | Query string *(preferred — matches MBG)* | `/?cspId=a0b6t9` · also `cspid`, `csp_id`, `id`, any casing |
| 2 | Path segment | `/wiom-sehat-mg/a0b6t9` (routed by `404.html`) |
| 3 | Hash | `/#a0b6t9` or `/#cspId=a0b6t9` |
| 4 | Native webview injection | `window.CSP_ID`, `window.cspId`, or `Android.getCspId()` |
| 5 | Session memory | remembered in `sessionStorage` across in-app navigation |

Anything that doesn't look like a CSP id (`^[a-z][a-z0-9]{4,9}$`) is ignored.

## How it renders

```
/?cspId=a0b6t9      →  Track A · Optical Power 49%  (1,683 of 3,450 pings OK)
/?cspId=a0a6y4      →  Track B · समय पर समाधान 86%  (165 of 191 within 4h)
```

A CSP id that isn't in `data.json` → *"आपका हिसाब अभी तैयार नहीं है"*, never a fabricated number.

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
| **Weak connections** (Track A "whom to treat") | `DBT.HOURLY_DEVICE_PING_INFLUX` | per-device 15-day avg `OPTICAL_AVG` below **−25 dBm** = out-of-range; worst-first ONT serials + dBm. Join `CSP_ACCOUNT.partner_id`. `query.sql` → `weak_query.sql` |

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

1. **The graded window is not the window the screen shows** (now disclosed, not silent). §5 grades
   on a month-end window (OP = last 5 days, SLA = last 15-day average); §7/§10 say the daily tile
   shows the rolling number (15-day OP, 60-day SLA). The screen keeps the rolling number (spec-correct
   for the daily checkup) but **names the exact grade window in the guarantee card** ("महीने के
   आख़िरी 5/15 दिन"), and the delay card **steps up as that window opens** (§7 window-mode reminders).
   Fully closing it needs a last-5-day / last-15-day aggregate baked into `data.json` — cheap to add
   when Growth confirms it should replace, not just annotate, the rolling number.
2. **"Whom to treat" ONT list — now live** (§7's "most valuable feature"). Track A's action card lists
   the CSP's worst-first out-of-range ONTs (serial + dBm) from `DBT.HOURLY_DEVICE_PING_INFLUX`, whose
   per-device `OPTICAL_AVG` **does** carry optical signal (not just uptime). Two caveats to close later:
   (a) that source lags ~12 days (freshest optical snapshot was Jul 3), so a just-fixed ONT may still
   show — fine for a worst-first to-do list, not for grading; (b) the public `data.json` deliberately
   carries **only the device serial + dBm, no customer name/phone/address** — when the authenticated
   app build (`PROXY_URL`) lands, the list can add customer/area behind auth. `weak_dbm_floor` (−25) is
   calibrated so the in-range share reproduces the app's T1 (a0b6t9 ~49%).
3. **No live open-ticket feed.** Every unresolved row in `COMPLAINT_RESOLUTION_LEDGER` is **7+ days
   old** (567 aged 7–30d, 432 over 30d, **zero** under 24h), so those are stale hygiene artifacts,
   not a work queue. Track B's action card is therefore built on the real breach count, not a fake
   4-hour countdown. A genuine open-ticket list needs the ops ticketing system.
4. **75% split vs 80% target.** A CSP at OP 76% lands in Track B and can bank ₹10,000 on SLA alone
   while their optical never reaches 80%. Confirm this is intended.
5. **Payout source of truth** — the note says OSS/NMS + ticketing; what is live and reproducible is
   `CSP_QUALITY_SERVICE`. Pick one.
6. **55 CSPs have no optical telemetry** and cannot be track-assigned. They currently default to
   SLA-only ("🩺 सर्विस ट्रैक", not "फिट रखना"). Confirm, or handle manually (§10).
7. **Enrollment** is not wired — the screen assumes the CSP is already in. Reuse the Install-MG
   single-accept flow (§6).
