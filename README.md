# dogg-seedvault — a federated node of the global tick network

**A heirloom seed vault: 12 common Southern varieties (USDA zone 8a, Atlanta) with days-to-maturity and sow/harvest windows, plus a running countdown to the next sow date.**

This repo keeps its own append-only chain of rapp/1 frames in `seedvault/`. Once a day
a GitHub Action reads the current tick anchor from the spine at
[kody-w/dogg](https://github.com/kody-w/dogg) and appends one frame of this node's
outlook, referencing that tick — so this chain joins every other node's data on the
same clock.

## What it carries

Twelve heirloom crops chosen because they're common, easy to save true-from-seed, and
between them cover cool-season and warm-season Southern growing: tomato (Cherokee
Purple), bean (Kentucky Wonder), squash (Yellow Crookneck), okra (Clemson Spineless),
collards (Georgia Southern), corn (Hickory King), pepper (Pimento L), cucumber (Boston
Pickling), melon (Moon and Stars), sweet potato (Georgia Jet), pea (Green Arrow), and
lettuce (Black Seeded Simmons). Each frame's `payload.seedvault.vault` carries, per
variety: `name`, `days_to_maturity`, `sow_window` (`[start_month, end_month]`),
`last_frost_month`, `first_frost_month`. Three scalars ride alongside: `varieties`
(count), `days_to_next_sow` (days from this frame's date to the nearest upcoming sow
window across all 12), and `frost_free_days` (the zone's average growing-season length).

## Why it matters offline / for heirlooms

Every other tick-network node so far watches something that only exists live — a price,
a rate, a market. A seed vault is the opposite kind of fact: it's a fixed almanac (which
month to sow what, and how long until harvest) that stays true whether or not the
internet, an exchange, or a market API is up. It's here because the network should carry
at least one thread of data useful *after* the lights go out — a growing calendar you can
read off a chain of hashes with nothing but `tools/rapp.py` and a Python interpreter,
the way an heirloom seed itself carries next year's crop with nothing but soil.

## Precision and limits

This is a **fixed reference table, not a live measurement.** `sow_window`,
`days_to_maturity`, and the frost months are conventional zone-8a planting-almanac
values for one place (Atlanta, GA) — they do not adjust for the actual weather in any
given year, a specific microclimate, or any zone but 8a. `frost_free_days` (240) is a
long-run average, not this year's forecast. `days_to_next_sow` is exact arithmetic from
the frame's own UTC date, not a soil-temperature reading. Treat this chain as a stable
starting calendar to garden from, not a substitute for watching your own ground.

**Verify it yourself:** `python3 tools/verify_thread.py` re-checks every frame with the
reference implementation from [kody-w/rapp-1](https://github.com/kody-w/rapp-1). CI runs
the same oracle on every push.

**Start your own node:** fork this repo, edit `THEME` / `STREAM` / the almanac tables at
the top of `tools/collect.py`, and enable the scheduled workflow. Your chain, your
outlook, same clock — announce it on the spine's registry
([kody-w/dogg](https://github.com/kody-w/dogg) issues) so agents can find it.

## Trust

<!--trust-->
No ratings yet — used this chain? [Rate it](../../issues/new?template=rate.yml): valid ratings publish automatically as verifiable frames.
<!--/trust-->

## Summon this node

A MISSION chant — 14 words — carries the `seedvault:@kody-w/dogg-seedvault` dimension's identity, its tick, a hash prefix that pins the exact frame, and a quantized snapshot of tick, varieties, days_to_next_sow.

```
KNELL CAST MAGE FORGE FORGE STAIR FONT ANVIL SKEWER THEME HEX JAW DISMISS GEM
```

`dogg:1:14:BIALIYAAAeOMwB2mtWTY-gGf`

Tap to decode: [https://kody-w.github.io/dogg/recite.html#dogg:1:14:BIALIYAAAeOMwB2mtWTY-gGf](https://kody-w.github.io/dogg/recite.html#dogg:1:14:BIALIYAAAeOMwB2mtWTY-gGf)

This chant carries three things: which dimension it names (`seedvault:@kody-w/dogg-seedvault`), which tick and frame it was cut from (tick 1, hash prefix `38e33`), and the field values above, quantized (log-quantized, ~0.3% relative (1e-6 … 1e15)) — enough to recognize the node and sanity-check a claim about it without touching the network.

This is a snapshot of one tick (tick 1) — the numbers move as the stream advances, so re-mint with `python3 tools/dogg.py mission seedvault:@kody-w/dogg-seedvault` for the latest.
