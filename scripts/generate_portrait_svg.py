from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import xml.sax.saxutils as saxutils

img_path = "C:/Users/gabri/.gemini/antigravity/scratch/github-profile/nobg_preview.png"
out_svg = "C:/Users/gabri/.gemini/antigravity/scratch/github-profile/portrait-ascii.svg"

img = Image.open(img_path)

# Crop head, cap, and shoulders directly from background-removed image
# Cap starts at y=280
crop_box = (260, 275, 720, 680)
cropped = img.crop(crop_box)

rgb = cropped.convert("RGB")
alpha = np.array(cropped.split()[-1])

gray = rgb.convert("L")
sharpened = gray.filter(ImageFilter.UnsharpMask(radius=2.5, percent=280, threshold=2))
enhancer = ImageEnhance.Contrast(sharpened)
gray_contrast = enhancer.enhance(1.8)

target_cols = 66
aspect = cropped.size[1] / cropped.size[0]
target_rows = int(target_cols * aspect * 0.52) # ~ 30 rows

resized_gray = gray_contrast.resize((target_cols, target_rows), Image.Resampling.LANCZOS)
resized_alpha = Image.fromarray(alpha).resize((target_cols, target_rows), Image.Resampling.LANCZOS)

arr_gray = np.array(resized_gray)
arr_alpha = np.array(resized_alpha)

RAMP = "   .:-=+*#%@"
ramp_len = len(RAMP)

ascii_lines = []
for r in range(target_rows):
    line_chars = []
    for c in range(target_cols):
        # Background pixels become pure spaces
        if arr_alpha[r, c] < 150:
            line_chars.append(" ")
        else:
            val = arr_gray[r, c]
            idx = int((val / 255.0) * (ramp_len - 1))
            idx = max(0, min(idx, ramp_len - 1))
            line_chars.append(RAMP[idx])
    ascii_lines.append("".join(line_chars))

# Trim empty top rows if any (keep 1 for margin)
while len(ascii_lines) > 0 and ascii_lines[0].strip() == "" and len(ascii_lines) > 26:
    ascii_lines.pop(0)

# SVG Dimensions
svg_width = 370
svg_height = 280
font_size = 6.4
line_height = 7.3
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
  <text x="70" y="18" class="title">gabriel-portrait.ascii [no-background]</text>

  <!-- ASCII Art Body -->
  <g class="ascii-container">
    {chr(10).join(text_tags)}
  </g>
</svg>"""

with open(out_svg, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Generated {out_svg} with {len(ascii_lines)} rows from no-background photo.")
