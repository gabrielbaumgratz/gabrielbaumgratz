from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import xml.sax.saxutils as saxutils

img_path = "C:/Users/gabri/.gemini/antigravity/scratch/github-profile/photo.jpg"
out_svg = "C:/Users/gabri/.gemini/antigravity/scratch/github-profile/portrait-ascii.svg"

img = Image.open(img_path)

# Precise centered crop on head, cap, and shoulders
# Head horizontal center is at x=459, cap top is at y=262
# Crop box (w=380, h=350):
crop_box = (269, 246, 649, 596)
cropped = img.crop(crop_box)

gray = cropped.convert("L")
arr = np.array(gray)

# Clear any stray noise in top corners
for y in range(arr.shape[0]):
    for x in range(arr.shape[1]):
        if y < 45 and (x < 110 or x > 270):
            arr[y, x] = 0

cleaned = Image.fromarray(arr)

# Sharpening to highlight cap logo, brim, eyes, and smile
sharpened = cleaned.filter(ImageFilter.UnsharpMask(radius=2.5, percent=300, threshold=2))
enhancer = ImageEnhance.Contrast(sharpened)
gray_contrast = enhancer.enhance(1.85)

# Target character grid: 66 columns
target_cols = 66
aspect = cropped.size[1] / cropped.size[0]
target_rows = int(target_cols * aspect * 0.52) # ~ 31 rows

resized = gray_contrast.resize((target_cols, target_rows), Image.Resampling.LANCZOS)
arr_small = np.array(resized)

RAMP = "   .:-=+*#%@"
ramp_len = len(RAMP)

ascii_lines = []
for row in arr_small:
    line_chars = []
    for val in row:
        if val < 46:
            line_chars.append(" ")
        else:
            idx = int(((val - 46) / (255 - 46)) * (ramp_len - 1))
            idx = max(0, min(idx, ramp_len - 1))
            line_chars.append(RAMP[idx])
    ascii_lines.append("".join(line_chars))

# Trim empty top rows if any (keep 1-2 for margin)
while len(ascii_lines) > 0 and ascii_lines[0].strip() == "" and len(ascii_lines) > 28:
    ascii_lines.pop(0)

svg_width = 370
svg_height = 280
font_size = 6.4
line_height = 7.1
start_y = 44
start_x = 16

styles = [
    ".bg { fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 6; }",
    ".bar { fill: #161b22; }",
    ".dot-red { fill: #ff5f56; }",
    ".dot-yellow { fill: #ffbd2e; }",
    ".dot-green { fill: #27c93f; }",
    ".title { fill: #8b949e; font-size: 11px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }",
    ".ascii-container { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 6.4px; fill: #8b949e; white-space: pre; }",
    "@keyframes rowReveal { 0% { opacity: 0; clip-path: inset(0 100% 0 0); } 100% { opacity: 1; clip-path: inset(0 0 0 0); } }",
    ".row { opacity: 0; animation: rowReveal 0.22s ease-out forwards; }"
]

for i in range(len(ascii_lines)):
    delay = 0.03 + (i * 0.022)
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
  <text x="70" y="18" class="title">gabriel-portrait.ascii [centered]</text>

  <!-- ASCII Art Body -->
  <g class="ascii-container">
    {chr(10).join(text_tags)}
  </g>
</svg>"""

with open(out_svg, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Generated {out_svg} with {len(ascii_lines)} rows perfectly centered.")
