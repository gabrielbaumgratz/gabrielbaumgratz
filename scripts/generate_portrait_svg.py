from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import xml.sax.saxutils as saxutils

img_path = "C:/Users/gabri/.gemini/antigravity/scratch/github-profile/photo.jpg"
out_svg = "C:/Users/gabri/.gemini/antigravity/scratch/github-profile/portrait-ascii.svg"

img = Image.open(img_path)
w, h = img.size

# Head & shoulders portrait crop
crop_box = (int(w * 0.28), int(h * 0.22), int(w * 0.72), int(h * 0.64))
cropped = img.crop(crop_box)

# Grayscale & sharpening
gray = cropped.convert("L")
sharpened = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=240, threshold=2))
enhancer = ImageEnhance.Contrast(sharpened)
gray_contrast = enhancer.enhance(1.6)

# Downsample to terminal grid: 68 columns
target_cols = 68
aspect_ratio = cropped.size[1] / cropped.size[0]
target_rows = int(target_cols * aspect_ratio * 0.52) # ~ 34 rows

resized = gray_contrast.resize((target_cols, target_rows), Image.Resampling.LANCZOS)
arr = np.array(resized)

RAMP = "   .:-=+*#%@"
ramp_len = len(RAMP)

ascii_lines = []
for row in arr:
    line_chars = []
    for val in row:
        if val < 45:
            line_chars.append(" ")
        else:
            idx = int(((val - 45) / (255 - 45)) * (ramp_len - 1))
            idx = max(0, min(idx, ramp_len - 1))
            line_chars.append(RAMP[idx])
    line_str = "".join(line_chars)
    # Trim leading trailing spaces proportionally if needed, or keep fixed length
    ascii_lines.append(line_str)

# SVG Dimensions
svg_width = 370
svg_height = 280
font_size = 6.2
line_height = 6.8
start_y = 42
start_x = 14

styles = [
    ".bg { fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 6; }",
    ".bar { fill: #161b22; }",
    ".dot-red { fill: #ff5f56; }",
    ".dot-yellow { fill: #ffbd2e; }",
    ".dot-green { fill: #27c93f; }",
    ".title { fill: #8b949e; font-size: 11px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }",
    ".ascii-container { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 6.2px; fill: #8b949e; white-space: pre; }",
    "@keyframes rowReveal { 0% { opacity: 0; clip-path: inset(0 100% 0 0); } 100% { opacity: 1; clip-path: inset(0 0 0 0); } }",
    ".row { opacity: 0; animation: rowReveal 0.22s ease-out forwards; }"
]

for i in range(len(ascii_lines)):
    delay = 0.04 + (i * 0.024)
    styles.append(f".r{i} {{ animation-delay: {delay:.3f}s; }}")

style_block = "\n    ".join(styles)

text_tags = []
for i, line in enumerate(ascii_lines):
    escaped_line = saxutils.escape(line)
    y_pos = start_y + (i * line_height)
    text_tags.append(f'<text x="{start_x}" y="{y_pos:.1f}" class="row r{i}">{escaped_line}</text>')

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <defs>
    <style>
    {style_block}
    </style>
  </defs>

  <!-- Terminal Window Frame -->
  <rect width="{svg_width}" height="{svg_height}" class="bg" />
  <path d="M 0 6 C 0 2.68 2.68 0 6 0 L {svg_width-6} 0 C {svg_width-2.68} 0 {svg_width} 2.68 {svg_width} 6 L {svg_width} 28 L 0 28 Z" class="bar" />
  <circle cx="16" cy="14" r="5" class="dot-red" />
  <circle cx="32" cy="14" r="5" class="dot-yellow" />
  <circle cx="48" cy="14" r="5" class="dot-green" />
  <text x="70" y="18" class="title">gabriel-portrait.ascii [live]</text>

  <!-- ASCII Art Body -->
  <g class="ascii-container">
    {chr(10).join(text_tags)}
  </g>
</svg>"""

with open(out_svg, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Successfully generated {out_svg} with {len(ascii_lines)} rows.")
