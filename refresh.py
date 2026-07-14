"""
Sehat MG — refresh data.json from Snowflake (via Metabase /api/dataset).

    python refresh.py

Writes data.json = { "meta": {...}, "data": { "<cspId>": {ok, all, sok, stot, cn, tr, op0} } }
Those are the RAW inputs. Every displayed number (Optical Power %, SLA %, gap to 80,
RAG band, bar width) is derived from them client-side in index.html, so the CSP sees
exactly the numerator/denominator behind their grade.

  ok / all   Optical Power  = ok / all * 100     (TELEMETRY_ROLLUP_RECORDS, rolling 15 telemetry days)
  sok / stot Service SLA    = sok / stot * 100   (COMPLAINT_RESOLUTION_LEDGER, CSP's own 60-day lookback)
  cn         active connections            op0  Optical Power at month start (track is locked off this)
  tr         'A' (op0 < 75) | 'B' (op0 >= 75) | 'U' (no optical telemetry)

NOTE ON THE FORMULA — this is the one thing to not get wrong:
  % Optical Power = OPTICAL_NUMERATOR / OPTICAL_DENOMINATOR  (share of IN-RANGE pings).
  The column T1_OOR_RATE is an OK-rate despite its name. Proof: the service's own
  T1_BAND assigns VG at 95-100 and GOOD at 90-95, banding identically to
  T2_SPEED_OK_RATE, whose direction is unambiguous. Reading it as "out of range"
  (i.e. 100 - rate) inverts every CSP and puts 986/1053 into Track A.
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone, timedelta

ENV = r"C:\credentials\.env"
SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query.sql")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

key = os.environ.get("METABASE_API_KEY")
if not key and os.path.exists(ENV):
    for line in open(ENV, encoding="utf-8"):
        if line.startswith("METABASE_API_KEY"):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
if not key:
    sys.exit("METABASE_API_KEY not found (env var or C:\\credentials\\.env)")

req = urllib.request.Request(
    "https://metabase.wiom.in/api/dataset",
    data=json.dumps({
        "database": 113,
        "type": "native",
        "native": {"query": open(SQL, encoding="utf-8").read()},
    }).encode(),
    headers={"X-API-KEY": key, "Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=600) as r:
    res = json.loads(r.read().decode())
if res.get("status") == "failed":
    sys.exit("query failed: " + str(res.get("error"))[:500])

cols = [c["name"] for c in res["data"]["cols"]]
rows = [dict(zip(cols, row)) for row in res["data"]["rows"]]

data, tracks = {}, {"A": 0, "B": 0, "U": 0}
for r in rows:
    cid = r["CSP_ID"]
    if not cid:
        continue
    tracks[r["TRACK"]] = tracks.get(r["TRACK"], 0) + 1
    rec = {"tr": r["TRACK"], "cn": r["CONNS"] or 0}
    if r["ALL_PINGS"]:
        rec["ok"], rec["all"] = int(r["OK_PINGS"]), int(r["ALL_PINGS"])
    if r["SLA_TOT"]:
        rec["sok"], rec["stot"] = int(r["SLA_OK"]), int(r["SLA_TOT"])
    if r["OP_MONTH_START"] is not None:
        rec["op0"] = round(float(r["OP_MONTH_START"]), 1)
    data[cid.lower()] = rec

ist = datetime.now(timezone.utc) + timedelta(minutes=330)
out = {
    "meta": {
        "generated_at": ist.strftime("%Y-%m-%d %H:%M IST"),
        "csps": len(data),
        "tracks": tracks,
        "source": "PROD_DB.CSP_QUALITY_SERVICE_CSP_QUALITY_SERVICE",
        "optical_window_days": 15,
        "sla_tat_hours": 4,
        "target_pct": 80,
        "track_split_pct": 75,
    },
    "data": data,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"), ensure_ascii=False)

print(f"data.json  {len(data)} CSPs  {os.path.getsize(OUT)/1024:.0f} KB")
print(f"tracks     A(ilaaj) {tracks['A']}  B(fit-rakhna) {tracks['B']}  unclassified {tracks['U']}")
