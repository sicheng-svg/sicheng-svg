import os
import requests

# 1. 配置
REPO = os.getenv("GITHUB_REPOSITORY") # 自动获取，例如 "sicheng-svg/sicheng-svg"
TOKEN = os.getenv("GITHUB_TOKEN")

def fetch_latest_diary():
    # 利用 GitHub API 获取带有 diary 标签的最新 issue
    url = f"https://api.github.com/repos/{REPO}/issues?labels=diary&state=all&per_page=3"
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200 or not response.json():
        return "👋 欢迎来到我的主页！最近还没有更新日记哦~"
    
    # 拼接最近几条日记的标题或内容
    issues = response.json()
    diary_text = " 🌟 ".join([f"[{issue['created_at'][:10]}] {issue['title']}" for issue in issues])
    return diary_text + " 🌟 "

def generate_svg(text):
    # 使用 SVG 的 animateTransform 实现平滑向左滚动
    # 宽度设为 800，高度设为 40，配色贴合你的深色主题
    svg_template = f"""<svg width="800" height="40" xmlns="http://www.w3.org/2000/svg">
    <style>
        .text {{ font-family: 'Fira Code', monospace, sans-serif; font-size: 16px; fill: #58A6FF; }}
    </style>
    <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
    <g>
        <text x="800" y="25" class="text" white-space="nowrap">
            {text}
        </text>
        <animateTransform attributeName="transform" type="translate" from="0 0" to="-1500 0" begin="0s" dur="20s" repeatCount="indefinite" />
    </g>
</svg>"""
    
    with open("diary.svg", "w", encoding="utf-8") as f:
        f.write(svg_template)

if __name__ == "__main__":
    text = fetch_latest_diary()
    generate_svg(text)
    print("SVG Generated Successfully!")
