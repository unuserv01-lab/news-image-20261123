# The World in One Day — Monday 23 November 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/unuserv01-lab/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/unuserv01-lab/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One front page summing up the world's news of **Monday 23 November 2026** —
38 verified stories across 9 regions, as of 00:30 UTC.

## What's on the page

- **Date hero** — MONDAY 23 NOVEMBER 2026, masthead + story counts
- **Data strip** — COP31 collapses, Iran hits Bahrain, Liverpool 4–0 United
- **3 big illustrated leads** — COP31 collapse in Antalya, Iran strikes on
  Bahrain and tankers in the Strait of Hormuz, Liverpool's 4–0 rout of
  Manchester United in Pochettino's first game
- **THE DAY IN TEN** — the ten biggest stories, with source + verification
  badge each
- **The full numbered list** — stories 14–38
- **WHERE IT HAPPENED** — world map with 9 pins
- **DATE CHECK** — what was deliberately left out, and why, plus two
  figure discrepancies (Indonesia factory fire toll; Poland missile IDs)
- **UTC timeline** — the day, hour by hour

Every story carries a named source and a verification badge:
CONFIRMED / OFFICIAL / REPORTED / CLAIMED. Nothing is invented; the
coverage window (as of 00:30 UTC, mostly Sunday 22 Nov events reported
overnight) is stated on the page itself.

## How it runs

`main.py` copies the pre-rendered `entry.png` (shipped in this repo) to
`$MAKEFUN_OUTPUT_DIR/entry.png`, stdlib only — no rendering at run time.
`render.py` + `stories.json` are the build evidence: run `render.py`
in-session to regenerate the identical 1024×1024 PNG deterministically.

## License

MIT — see `LICENSE`.
