# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Adesudu/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Adesudu/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A one-page newspaper front page summing up the world news of Thursday 26 November 2026, drawn by a pure-Python program: Jensen Huang resigns as Nvidia chief, SpaceX is cleared for a million satellites, Russia's own tally of nearly 500,000 war dead, Democrats retake Congress, BepiColombo reaches Mercury, and ten more stories from the day.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024, deterministic — the same bytes on every run). No network, no third-party packages: the page is rasterised with a hand-drawn 5x7 bitmap font and encoded as PNG with the standard library alone (`render.py`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=qq4pkark&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
