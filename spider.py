import os
import re
import time
import json
import logging
import random
from urllib.parse import quote
from tqdm import tqdm
from playwright.sync_api import sync_playwright
from config import (
    KEYWORD_COOLDOWN_MIN, KEYWORD_COOLDOWN_MAX,
    LONG_REST_INTERVAL, LONG_REST_MIN, LONG_REST_MAX
)
from maple_crawler.utils import random_viewport, parse_cookie_string, stealth_init_script, build_headers

# # 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("xhs_downloader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("XHS_Downloader")
logger.setLevel(logging.DEBUG)

# # 使用您提供的Cookie
USER_COOKIE=""
if __name__ == "__main__":
    print("=" * 50)
    print("小红书图片下载工具")
    print("=" * 50)

    keywords_path = "keywords.txt"
    max_items = 1000000

    if not os.path.exists(keywords_path):
        logger.error(f"未找到关键词文件: {keywords_path}")
        exit(1)

    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    from maple_crawler.xhs import XHSCrawler
    total_success = 0
    start_time = time.time()

    with sync_playwright() as p:
        # 启动浏览器
        try:
            if os.name == 'nt':
                chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
            else:
                chrome_path = "/usr/bin/google-chrome"
            browser = p.chromium.launch(executable_path=chrome_path, headless=False, args=["--disable-blink-features=AutomationControlled"])
        except Exception:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])

        # 创建并复用同一个浏览器上下文，保持登录态
        headers_for_context = build_headers(USER_COOKIE, referer='https://www.xiaohongshu.com/')
        user_agent = headers_for_context.get('User-Agent')
        vp = random_viewport()
        context = browser.new_context(
            user_agent=user_agent,
            viewport=vp,
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            bypass_csp=True
        )
        try:
            context.add_init_script(stealth_init_script())
        except Exception:
            pass
        try:
            context.add_cookies(parse_cookie_string(USER_COOKIE))
        except Exception:
            pass

        page = context.new_page()

        for idx, keyword in enumerate(keywords, 1):
            logger.info(f"\n{'='*20} [关键词 {idx}/{len(keywords)}] {keyword} {'='*20}")
            print(f"\n{'='*20} [关键词 {idx}/{len(keywords)}] {keyword} {'='*20}")
            safe_keyword = re.sub(r'[\\/:*?"<>|]', '', keyword).strip()
            safe_dir = os.path.join('xhs_images', safe_keyword[:40])
            os.makedirs(safe_dir, exist_ok=True)
            crawler = XHSCrawler(user_cookie=USER_COOKIE, save_dir=safe_dir, max_workers=8)
            # 传递 browser 实例
            success_count = crawler.crawl_search(keyword, max_images=max_items, browser=browser, context=context, page=page)
            total_success += success_count
            print(f"本关键词下载完成: {success_count} 张图片")
            logger.info(f"本关键词下载完成: {success_count} 张图片")
            
            # 每个关键词之间添加较长的冷却时间，避免触发反爬
            if idx < len(keywords):
                cooldown_time = random.uniform(KEYWORD_COOLDOWN_MIN, KEYWORD_COOLDOWN_MAX)
                logger.info(f"关键词冷却中，等待 {cooldown_time:.1f} 秒后继续...")
                print(f"⏳ 关键词冷却中，等待 {cooldown_time:.1f} 秒后继续...")
                time.sleep(cooldown_time)
                
                # 每N个关键词后增加更长的休息时间
                if idx % LONG_REST_INTERVAL == 0:
                    long_rest = random.uniform(LONG_REST_MIN, LONG_REST_MAX)
                    logger.info(f"已完成 {idx} 个关键词，长时间休息 {long_rest:.1f} 秒...")
                    print(f"🛑 已完成 {idx} 个关键词，长时间休息 {long_rest:.1f} 秒...")
                    time.sleep(long_rest)

        try:
            page.close()
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass

    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"全部任务完成! 共下载 {total_success} 张图片")
    print(f"总耗时: {elapsed_time:.1f} 秒 ({elapsed_time/60:.1f} 分钟)")
    print("=" * 50)