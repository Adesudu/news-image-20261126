"""Entrypoint for the news-image-20261126 bounty.

Renders a one-page newspaper front page summing up the world news of
Thursday 26 November 2026 and writes it to entry.png in the output
directory. The render is deterministic: the same bytes every run.
"""

import os

from render import render_page_png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = render_page_png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote {} ({} bytes)".format(path, len(data)))


if __name__ == "__main__":
    main()
