import os
import requests
from datetime import datetime

# 1. 核心配置：确保从 Action 环境中获取
REPO = os.getenv("GITHUB_REPOSITORY") # 例如 "sicheng-svg/sicheng-svg"
TOKEN = os.getenv("GITHUB_TOKEN")

# 确保在本地测试时也能运行
if not REPO:
    REPO = "sicheng-svg/sicheng-svg"  # 替换为你自己的用户名/仓库
    print(f"Warning: GITHUB_REPOSITORY not set. Using default: {REPO}")

# 2. 核心函数：抓取日记数据
def fetch_diary_issues():
    # 彻底删除硬编码的示例！
    
    # 调用 GitHub API 抓取带有 diary 标签的最新 15 个 issues (每行约 5 个)
    url = f"https://api.github.com/repos/{REPO}/issues?labels=diary&state=all&per_page=15"
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching issues: {response.status_code}")
        return []
    
    issues = response.json()
    formatted_diary = []
    
    for issue in issues:
        # 格式化日期：'2026-03-17'
        created_at = datetime.strptime(issue["created_at"][:10], "%Y-%m-%d").strftime("%Y-%m-%d")
        
        # 处理标题：截断并添加省略号，防止文本溢出
        title = issue["title"]
        # 每行卡片约 12-15 个汉字或 35 个字符
        max_title_len = 35 
        if len(title) > max_title_len:
            title = title[:max_title_len].rstrip() + "..."
            
        formatted_diary.append({
            "date": created_at,
            "title": title
        })
        
    return formatted_diary

# 3. 辅助函数：生成单行 SVG 元素
def build_row_svg_elements(items, start_y):
    svg_elements = ""
    current_x = 0
    box_height = 110
    gap = 15
    base_card_width = 200 # 基准卡片宽度

    for item in items:
        # 这里彻底删除了关于图片处理的分支！
        
        # 动态计算宽度：基准宽度 + 标题长度系数 (简单处理)
        # 标题全英文会宽一些，全中文会窄一些。这里简单按字符数估算。
        text_width_factor = len(item["title"]) * 5 
        # 这里使用标题字数模运算作为确定性的宽度增量：
        card_width = base_card_width + text_width_factor + (len(item["title"]) % 4 * 15)
        
        # 绘制外框 (亮色主题)
        svg_elements += f'<rect x="{current_x}" y="{start_y}" width="{card_width}" height="{box_height}" class="box"/>\n'
        
        # 绘制日期 (亮色主题)
        svg_elements += f'<text x="{current_x + 15}" y="{start_y + 30}" class="date">[{item["date"]}]</text>\n'
        
        # 绘制标题 (亮色主题, 限制字数)
        svg_elements += f'<text x="{current_x + 15}" y="{start_y + 60}" class="text">{item["title"]}</text>\n'
        
        current_x += card_width + gap
    
    # 返回该行的 SVG 元素和总宽度
    return svg_elements, current_x

# 4. 主函数：生成最终 SVG
def generate_automated_white_masonry_svg():
    # 画布整体尺寸
    width = 800
    height = 400
    # 动画设置：30秒滚动一圈，更平滑
    duration = "30s"

    # 获取真实数据
    all_diary_items = fetch_diary_issues()
    
    # 动态分配 Issue 到三行，体现多行交错布局
    row1_items = [item for i, item in enumerate(all_diary_items) if i % 3 == 0]
    row2_items = [item for i, item in enumerate(all_diary_items) if i % 3 == 1]
    row3_items = [item for i, item in enumerate(all_diary_items) if i % 3 == 2]

    # 行高与间距设置
    row_y_positions = [20, 150, 280] # 三行的 Y 坐标
    
    # 生成各行 SVG
    row1_svg, w1 = build_row_svg_elements(row1_items, row_y_positions[0])
    row2_svg, w2 = build_row_svg_elements(row2_items, row_y_positions[1])
    row3_svg, w3 = build_row_svg_elements(row3_items, row_y_positions[2])

    # 找出最长的一行作为整体循环的平移基准跨度
    max_width = max(w1, w2, w3)

    # 错误处理：如果没有日记，展示默认友好提示
    if not all_diary_items:
        max_width = 800 # 保证动画正常
        default_message_svg = f"""
        <rect x="0" y="145" width="800" height="110" class="box"/>
        <text x="400" y="195" class="text" text-anchor="middle">👋 还没有更新日记哦。在 Issues 里新建一条 diary 标签记录吧！</text>
        """
        row1_svg, row2_svg, row3_svg = default_message_svg, "", ""

    # SVG 模板拼接 - 已全部调整为白色/白色亮色模式主题
    svg_content = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <style>
        /* 亮色主题卡片和边框 */
        .box {{ fill: #f6f8fa; stroke: #d1d5da; stroke-width: 1.5px; rx: 8px; }}
        /* 深色主题文本 */
        .text {{ font-family: 'Fira Code', monospace, 'Microsoft YaHei', sans-serif; font-size: 14px; fill: #24292e; font-weight: bold; }}
        /* 亮色日期蓝色 */
        .date {{ font-family: 'Fira Code', monospace; font-size: 12px; fill: #0366d6; }}
    </style>
    
    <rect width="100%" height="100%" fill="#ffffff" rx="8"/>
    
    <g>
        <animateTransform attributeName="transform" type="translate" from="0 0" to="-{max_width} 0" begin="0s" dur="{duration}" repeatCount="indefinite" />
        
        <g>
            {row1_svg}
            {row2_svg}
            {row3_svg}
        </g>
        
        <g transform="translate({max_width}, 0)">
            {row1_svg}
            {row2_svg}
            {row3_svg}
        </g>
    </g>
</svg>"""

    with open("diary.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"生成成功！已切换为全自动化亮色日记墙。抓取到 {len(all_diary_items)} 条记录。")

if __name__ == "__main__":
    generate_automated_white_masonry_svg()
