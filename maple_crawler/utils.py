import os
import re
import time
import random
from urllib.parse import parse_qs
from typing import Optional


def clean_filename(name):
    return re.sub(r'[^\w\u4e00-\u9fff\s]', '', name)[:100]


def simulate_human_delay(min_delay=0.5, max_delay=3.0):
    # 缩短延迟，防止超时
    time.sleep(random.uniform(0.05, 0.3))


def get_random_user_agent():
    browsers = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}) Gecko/20100101 Firefox/{version}",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
    ]
    template = random.choice(browsers)
    if "Chrome" in template:
        version = f"{random.randint(120, 126)}.0.{random.randint(0, 9999)}.{random.randint(0, 999)}"
    elif "Firefox" in template:
        version = f"{random.randint(115, 125)}.0"
    else:
        version = f"{random.randint(15, 17)}.{random.randint(0,5)}"
    return template.format(version=version)


def random_viewport(min_w=800, max_w=1600, min_h=600, max_h=1200):
    """返回一个随机视窗尺寸，用于 Playwright context 创建或更新。"""
    return {"width": random.randint(min_w, max_w), "height": random.randint(min_h, max_h)}


def build_headers(user_cookie: Optional[str] = None, referer: Optional[str] = None):
    """构造一组随机化的请求头（User-Agent 可变、Referer 可选）。"""
    ua = get_random_user_agent()
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(["zh-CN,zh;q=0.9", "en-US,en;q=0.9", "zh-TW,zh;q=0.9"]),
        "Referer": referer or random.choice(["https://www.google.com/", "https://www.bing.com/", "https://www.baidu.com/"])
    }
    if user_cookie:
        headers["Cookie"] = user_cookie
    return headers


def stealth_init_script():
    """返回一段用于在 browser context 注入的脚本，屏蔽常见的自动化指纹。"""
    return """
        delete navigator.__proto__.webdriver;
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        Object.defineProperty(navigator, 'language', {get: () => 'zh-CN'});
    """


def random_mouse_movements(page, moves: int = 6):
    """在页面上进行一些随机鼠标移动与少量点击，模拟真实用户操作。"""
    try:
        # 取得视窗尺寸（兼容不同 Playwright 版本）
        try:
            size = page.viewport_size or page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
        except Exception:
            size = page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")

        w = int(size.get("width", 1200))
        h = int(size.get("height", 800))

        for i in range(moves):
            x = random.randint(int(w * 0.05), int(w * 0.95))
            y = random.randint(int(h * 0.05), int(h * 0.95))
            steps = random.randint(6, 20)
            try:
                page.mouse.move(x, y, steps=steps)
            except Exception:
                pass
            time.sleep(random.uniform(0.01, 0.15))
    except Exception:
        return


def interact_like_human(page):
    """组合多种小动作：滚动、鼠标移动、随机悬停，降低行为模式一致性。"""
    try:
        # 小滚动
        try:
            page.evaluate("window.scrollBy(0, window.innerHeight * 0.2)")
        except Exception:
            pass
        time.sleep(random.uniform(0.05, 0.2))

        random_mouse_movements(page, moves=random.randint(3, 8))
        # 不再点开/hover任何元素
    except Exception:
        return


def simulate_human_scroll(page, scroll_count=3):
    for i in range(scroll_count):
        scroll_height = page.evaluate("document.body.scrollHeight")
        scroll_amount = random.randint(int(scroll_height * 0.3), int(scroll_height * 0.8))
        scroll_speed = random.randint(100, 500)
        scroll_time = scroll_amount / scroll_speed
        page.evaluate(f"""
            new Promise(resolve => {{
                const start = performance.now();
                const scrollTo = {scroll_amount};
                function scrollStep(timestamp) {{
                    const elapsed = timestamp - start;
                    const progress = Math.min(elapsed / {scroll_time * 1000}, 1);
                    const currentScroll = progress * scrollTo;
                    window.scrollTo(0, currentScroll);
                    if (progress < 1) {{
                        requestAnimationFrame(scrollStep);
                    }} else {{
                        resolve();
                    }}
                }}
                requestAnimationFrame(scrollStep);
            }});
        """)
        time.sleep(random.uniform(0.1, 0.5))


def simulate_full_scroll(page, passes=3):
    for i in range(passes):
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception:
            break
        time.sleep(random.uniform(0.2, 0.6))


def parse_cookie_string(cookie_str):
    cookies = []
    if not cookie_str:
        return cookies
    for item in cookie_str.split(';'):
        item = item.strip()
        if not item:
            continue
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({'name': name, 'value': value, 'domain': '.xiaohongshu.com', 'path': '/'})
    return cookies
