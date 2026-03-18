#!/usr/bin/env python3
"""从 diary.json 生成三行错位滚动的 diary.svg（卡片高度自适应）"""

import json
import html

# ============ 配置 ============
CARD_W = 240
GAP = 20
CARD_STEP = CARD_W + GAP  # 260

CARD_PAD_TOP = 30      # 日期区域高度
LINE_HEIGHT = 19        # 每行文字间距
LINE_START_Y = 48       # 第一行文字 y 坐标
TAG_GAP = 16            # 最后一行文字到 tag 的间距
TAG_H = 20              # tag 底部留白
CARD_PAD_BOTTOM = 12    # 卡片底部 padding

ROW_CONFIGS = [
    {"speed": 28, "offset": 0},
    {"speed": 34, "offset": -120},
    {"speed": 31, "offset": -60},
]

SVG_W = 850
HEADER_H = 40
ROW_GAP = 15  # 行与行之间的间距


def calc_card_height(card):
    """根据文字行数计算卡片高度"""
    n_lines = len(card.get("lines", []))
    return CARD_PAD_TOP + n_lines * LINE_HEIGHT + TAG_GAP + TAG_H + CARD_PAD_BOTTOM


def escape(text):
    return html.escape(text)


# ============ 加载数据 ============
with open("diary.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

# 将卡片分成3行（轮流分配）
rows = [[] for _ in ROW_CONFIGS]
for i, card in enumerate(cards):
    rows[i % len(rows)].append(card)

# 计算每行的高度（取该行最高卡片）
row_heights = []
for row_cards in rows:
    if row_cards:
        max_h = max(calc_card_height(c) for c in row_cards)
    else:
        max_h = 110
    row_heights.append(max_h)

# 计算总 SVG 高度
SVG_H = HEADER_H + sum(row_heights) + ROW_GAP * len(ROW_CONFIGS) + 10


def render_card(card, x, y, row_h):
    """渲染单张卡片，高度使用该行统一高度"""
    parts = []
    parts.append(f'      <g transform="translate({x}, {y})">')
    parts.append(f'        <rect class="card" width="{CARD_W}" height="{row_h}" />')
    parts.append(f'        <text class="date" x="14" y="24">{escape(card["date"])}</text>')

    lines = card.get("lines", [])
    for j, line in enumerate(lines):
        ly = LINE_START_Y + j * LINE_HEIGHT
        parts.append(f'        <text class="text" x="14" y="{ly}">{escape(line)}</text>')

    tag = card.get("tag", "")
    if tag:
        tag_y = row_h - CARD_PAD_BOTTOM
        parts.append(f'        <text class="tag" x="14" y="{tag_y}">{escape(tag)}</text>')

    parts.append(f'      </g>')
    return "\n".join(parts)


def render_row(row_cards, row_index, y_offset):
    """渲染一行（含两组卡片实现无缝循环）"""
    cfg = ROW_CONFIGS[row_index]
    n = len(row_cards)
    if n == 0:
        return ""

    total_w = n * CARD_STEP
    row_h = row_heights[row_index]
    clip_h = row_h + ROW_GAP
    clip_id = f"clip{row_index}"

    parts = []
    parts.append(f'  <clipPath id="{clip_id}"><rect x="0" y="{y_offset}" width="{SVG_W}" height="{clip_h}" /></clipPath>')
    parts.append(f'  <g clip-path="url(#{clip_id})">')
    parts.append(f'    <g class="row{row_index}">')

    # 第1组
    for i, card in enumerate(row_cards):
        x = i * CARD_STEP
        parts.append(render_card(card, x, y_offset + 5, row_h))

    # 第2组（无缝循环）
    for i, card in enumerate(row_cards):
        x = total_w + i * CARD_STEP
        parts.append(render_card(card, x, y_offset + 5, row_h))

    parts.append(f'    </g>')
    parts.append(f'  </g>')

    return "\n".join(parts)


def build_svg():
    """构建完整 SVG"""
    # 动画 keyframes
    keyframes = []
    for i, cfg in enumerate(ROW_CONFIGS):
        n = len(rows[i])
        if n == 0:
            continue
        total_w = n * CARD_STEP
        offset = cfg["offset"]
        speed = cfg["speed"]
        keyframes.append(f"""      @keyframes row{i} {{
        0% {{ transform: translateX({offset}px); }}
        100% {{ transform: translateX({offset - total_w}px); }}
      }}
      .row{i} {{ animation: row{i} {speed}s linear infinite; }}""")

    styles = "\n".join(keyframes)

    # 计算每行 y 偏移
    row_svgs = []
    y_offset = HEADER_H
    for i in range(len(ROW_CONFIGS)):
        row_svgs.append(render_row(rows[i], i, y_offset))
        y_offset += row_heights[i] + ROW_GAP

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
  <defs>
    <style>
{styles}
      .card {{
        rx: 10; ry: 10;
        fill: #0d1117;
        stroke: #21262d;
        stroke-width: 1;
      }}
      .date {{
        font-family: 'Segoe UI', Ubuntu, sans-serif;
        font-size: 11px;
        fill: #58A6FF;
      }}
      .text {{
        font-family: 'Segoe UI', Ubuntu, sans-serif;
        font-size: 12.5px;
        fill: #c9d1d9;
      }}
      .tag {{
        font-family: 'Segoe UI', Ubuntu, sans-serif;
        font-size: 10px;
        fill: #8b949e;
      }}
    </style>
    <linearGradient id="fade-left" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#010409" stop-opacity="1"/>
      <stop offset="5%" stop-color="#010409" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fade-right" x1="0" y1="0" x2="1" y2="0">
      <stop offset="95%" stop-color="#010409" stop-opacity="0"/>
      <stop offset="100%" stop-color="#010409" stop-opacity="1"/>
    </linearGradient>
  </defs>

  <rect width="{SVG_W}" height="{SVG_H}" rx="12" fill="#010409" />
  <text x="20" y="28" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="15" font-weight="600" fill="#58A6FF">💭 Thoughts &amp; Notes</text>

{chr(10).join(row_svgs)}

  <rect width="{SVG_W}" height="{SVG_H}" fill="url(#fade-left)" pointer-events="none" />
  <rect width="{SVG_W}" height="{SVG_H}" fill="url(#fade-right)" pointer-events="none" />
</svg>"""

    return svg


if __name__ == "__main__":
    svg_content = build_svg()
    with open("diary.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    for i, row in enumerate(rows):
        max_lines = max(len(c.get("lines", [])) for c in row) if row else 0
        print(f"  Row {i+1}: {len(row)} cards, max {max_lines} lines, height {row_heights[i]}px")
    print(f"Generated diary.svg ({sum(len(r) for r in rows)} cards, SVG height {SVG_H}px)")
