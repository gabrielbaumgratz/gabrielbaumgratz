#!/usr/bin/env python3
"""
Renders data/contributions.json into an animated monochrome terminal SVG heatmap.
"""
import json
import os

IN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_SVG = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

# Green level progression
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def main():
    if not os.path.exists(IN_PATH):
        print(f"File {IN_PATH} not found.")
        return

    with open(IN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total = data.get("total", 0)
    username = data.get("username", "developer")

    box_size = 11
    gap = 4
    start_x = 24
    start_y = 50

    rects = []
    for idx, d in enumerate(days):
        col = idx // 7
        row = idx % 7
        x = start_x + col * (box_size + gap)
        y = start_y + row * (box_size + gap)
        level = min(max(d.get("level", 0), 0), 4)
        color = COLORS[level]
        delay = min((col * 0.012) + (row * 0.018), 1.2)
        rects.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{box_size}" height="{box_size}" '
            f'rx="2" fill="{color}" style="animation-delay: {delay:.3f}s;" />'
        )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 170" width="860" height="170">
  <defs>
    <style>
      .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 6; }}
      .bar {{ fill: #161b22; }}
      .dot-red {{ fill: #ff5f56; }}
      .dot-yellow {{ fill: #ffbd2e; }}
      .dot-green {{ fill: #27c93f; }}
      .txt {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; fill: #8b949e; }}
      .highlight {{ fill: #58a6ff; font-weight: bold; }}
      .legend-txt {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 10px; fill: #8b949e; }}
      @keyframes popIn {{
        0% {{ opacity: 0; transform: scale(0.6); }}
        100% {{ opacity: 1; transform: scale(1); }}
      }}
      .cell {{
        transform-origin: center;
        opacity: 0;
        animation: popIn 0.28s ease-out forwards;
      }}
    </style>
  </defs>
  <rect width="860" height="170" class="bg" />
  <path d="M 0 6 C 0 2.68 2.68 0 6 0 L 854 0 C 857.32 0 860 2.68 860 6 L 860 26 L 0 26 Z" class="bar" />
  <circle cx="16" cy="13" r="4.5" class="dot-red" />
  <circle cx="30" cy="13" r="4.5" class="dot-yellow" />
  <circle cx="44" cy="13" r="4.5" class="dot-green" />
  <text x="64" y="17" class="txt">{username}@github: contributions.sh</text>

  <text x="24" y="42" class="txt">Annual Contributions: <tspan class="highlight">{total:,}</tspan> | Real-time synchronized SVG</text>

  <g>
    {''.join(rects)}
  </g>

  <!-- Legend -->
  <g transform="translate(680, 40)">
    <text x="0" y="9" class="legend-txt">Less</text>
    <rect x="30" y="0" width="10" height="10" rx="2" fill="#161b22" />
    <rect x="44" y="0" width="10" height="10" rx="2" fill="#0e4429" />
    <rect x="58" y="0" width="10" height="10" rx="2" fill="#006d32" />
    <rect x="72" y="0" width="10" height="10" rx="2" fill="#26a641" />
    <rect x="86" y="0" width="10" height="10" rx="2" fill="#39d353" />
    <text x="104" y="9" class="legend-txt">More</text>
  </g>
</svg>"""

    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Heatmap rendered to {OUT_SVG}")

if __name__ == "__main__":
    main()
