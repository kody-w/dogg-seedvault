#!/usr/bin/env python3
"""A federated tick-network node: this repo's own append-only chain, keyed to the
global tick spine at kody-w/dogg.

Every run reads the spine's current tick anchor and appends one frame of this node's
themed snapshot, referencing that tick. Different repos, run by different people, each
with their own outlook — all joinable on the tick key. This node's outlook is a seed
vault: heirloom-variety sow/harvest windows for one USDA zone, computed offline from a
fixed almanac (no network source beyond the spine tick itself — a seed vault has to work
when nothing else does). Frames verify with the reference implementation (tools/rapp.py,
from kody-w/rapp-1); CI re-verifies the whole chain on every push.
"""
import json, sys, pathlib, datetime, urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import rapp as R
import chainio

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPINE_HEAD = "https://raw.githubusercontent.com/kody-w/dogg/main/ticks/HEAD.json"
TIMEOUT = 8

# ---- edit these for your node --------------------------------------------------------
THEME = "seedvault"
STREAM = "seedvault:@kody-w/dogg-seedvault"

# Fixed almanac for USDA zone 8a, Atlanta GA. Frost months are climatological averages
# (last spring frost ~mid-March, first fall frost ~mid-November) — not a live forecast.
ZONE = "8a (Atlanta)"
LAST_FROST_MONTH = 3
FIRST_FROST_MONTH = 11
FROST_FREE_DAYS = 240   # avg last frost (~Mar 20) to avg first frost (~Nov 15)

# 12 heirloom crops with their conventional zone-8a direct-sow (or transplant-out) window
# as [start_month, end_month], 1-12. days_to_maturity is the variety's typical days from
# sow/transplant to first harvest. Source: standard Southern-heirloom planting almanacs —
# a fixed reference table, not a live measurement.
VARIETIES = [
    {"name": "tomato Cherokee Purple",        "days_to_maturity": 80,  "sow_window": [4, 6]},
    {"name": "bean Kentucky Wonder",           "days_to_maturity": 65,  "sow_window": [4, 7]},
    {"name": "squash Yellow Crookneck",        "days_to_maturity": 55,  "sow_window": [4, 7]},
    {"name": "okra Clemson Spineless",         "days_to_maturity": 60,  "sow_window": [5, 6]},
    {"name": "collards Georgia Southern",      "days_to_maturity": 75,  "sow_window": [8, 9]},
    {"name": "corn Hickory King",              "days_to_maturity": 100, "sow_window": [4, 6]},
    {"name": "pepper Pimento L",               "days_to_maturity": 75,  "sow_window": [4, 6]},
    {"name": "cucumber Boston Pickling",       "days_to_maturity": 55,  "sow_window": [4, 7]},
    {"name": "melon Moon and Stars",           "days_to_maturity": 90,  "sow_window": [4, 6]},
    {"name": "sweet potato Georgia Jet",       "days_to_maturity": 90,  "sow_window": [5, 6]},
    {"name": "pea Green Arrow",                "days_to_maturity": 60,  "sow_window": [2, 3]},
    {"name": "lettuce Black Seeded Simmons",   "days_to_maturity": 45,  "sow_window": [2, 4]},
]
# ---------------------------------------------------------------------------------------

def utc():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"tick-node-{THEME}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())

def _days_to_month_start(today, month):
    """Days from today (UTC date) to the 1st of `month`, this year or next."""
    cand = datetime.date(today.year, month, 1)
    if cand < today:
        cand = datetime.date(today.year + 1, month, 1)
    return (cand - today).days

def build_vault(today):
    varieties = [
        {"name": v["name"], "days_to_maturity": v["days_to_maturity"],
         "sow_window": v["sow_window"], "last_frost_month": LAST_FROST_MONTH,
         "first_frost_month": FIRST_FROST_MONTH}
        for v in VARIETIES
    ]
    days_to_next_sow = min(_days_to_month_start(today, v["sow_window"][0]) for v in VARIETIES)
    return {"zone": ZONE, "varieties": varieties}, days_to_next_sow

def load_chain(d):
    return chainio.load_chain(d)

def main():
    spine = get(SPINE_HEAD)
    tick_n, tick_hash = spine["count"] - 1, spine["head_frame"]
    d = ROOT / THEME
    d.mkdir(exist_ok=True)
    chain = load_chain(d)
    head = chain[-1] if chain else None
    if head is not None and head["payload"].get("tick") == tick_n:
        print(f"{THEME}: tick {tick_n} already recorded — nothing to do")
        return
    today = datetime.datetime.now(datetime.timezone.utc).date()
    vault, days_to_next_sow = build_vault(today)
    data = {
        "vault": vault,
        "varieties": len(vault["varieties"]),
        "days_to_next_sow": days_to_next_sow,
        "frost_free_days": FROST_FREE_DAYS,
    }
    payload = {"tick": tick_n, "tick_frame": tick_hash, "spine": "kody-w/dogg",
               "fetched_utc": utc(), THEME: data, "sources_failed": []}
    if head is None:
        payload["about"] = (f"A federated node of the global tick network: this repo's "
                            f"own {THEME} outlook, one frame per observed tick, keyed to "
                            "the spine's tick anchors so it joins every other node's "
                            "data on the same clock. This node carries a heirloom seed "
                            "vault (12 varieties, zone 8a) so a growing calendar survives "
                            "even when nothing but this repo does.")
    f = R.build_frame(f"{THEME}.snapshot", STREAM, (head["seq"] + 1) if head else 0,
                      utc(), payload, prev=(head["payload_hash"] if head else None))
    ok, step, why = R.verify_frame(f, head=head, stream_id_of_record=STREAM)
    if not ok:
        raise ValueError(f"refusing invalid frame: {step}: {why}")
    chainio.append_frame(d, f, STREAM)
    print(f"{THEME} frame {f['seq']} @ spine tick {tick_n}: "
          f"{data['varieties']} varieties, next sow in {data['days_to_next_sow']}d")

if __name__ == "__main__":
    main()
