import os
import re
import time
import json
import random
import requests
import shutil
import uuid
import concurrent.futures
from typing import Dict, Set
import logging
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs, urlencode
# from playwright.sync_api import sync_playwright
from tqdm import tqdm

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
USER_COOKIE = ''


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

    for idx, keyword in enumerate(keywords, 1):
        logger.info(f"\n{'='*20} [关键词 {idx}/{len(keywords)}] {keyword} {'='*20}")
        print(f"\n{'='*20} [关键词 {idx}/{len(keywords)}] {keyword} {'='*20}")
        # 每个关键词单独子文件夹，保留中文，去除非法文件名字符
        safe_keyword = re.sub(r'[\\/:*?"<>|]', '', keyword).strip()
        safe_dir = os.path.join('xhs_images', safe_keyword[:40])
        os.makedirs(safe_dir, exist_ok=True)
        crawler = XHSCrawler(user_cookie=USER_COOKIE, save_dir=safe_dir, max_workers=8)
        crawler.crawl_search(keyword, max_images=max_items)
        success_count = len(crawler.metadata)
        total_success += success_count
        print(f"本关键词下载完成: {success_count} 张图片")
        logger.info(f"本关键词下载完成: {success_count} 张图片")

    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"全部任务完成! 共下载 {total_success} 张图片")
    print(f"总耗时: {elapsed_time:.1f} 秒 ({elapsed_time/60:.1f} 分钟)")
    print("=" * 50)