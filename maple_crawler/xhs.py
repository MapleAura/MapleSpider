import os
import time
import random
import requests
from urllib.parse import quote, urlparse, parse_qs
from playwright.sync_api import sync_playwright
from .base import BaseCrawler
from .utils import get_random_user_agent, simulate_full_scroll, parse_cookie_string
from .utils import clean_filename, build_headers, random_viewport, stealth_init_script, interact_like_human
import logging
logger = logging.getLogger("XHS_Downloader")

class XHSCrawler(BaseCrawler):
    def __init__(self, user_cookie: str, save_dir: str = 'xhs_images', max_workers: int = 5):
        super().__init__(user_cookie=user_cookie, max_workers=max_workers)
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def crawl_search(self, search_keyword: str, max_images: int = 100):
        headers = build_headers(self.user_cookie, referer='https://www.xiaohongshu.com/')
        user_agent = headers.get('User-Agent')

        logger.info(f"开始爬取(流式下载): '{search_keyword}' (目标数量: {max_images})")

        with sync_playwright() as p:
            try:
                if os.name == 'nt':
                    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
                else:
                    chrome_path = "/usr/bin/google-chrome"
                browser = p.chromium.launch(executable_path=chrome_path, headless=False, args=["--disable-blink-features=AutomationControlled"]) 
            except Exception:
                browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"]) 

            vp = random_viewport()
            context = browser.new_context(user_agent=user_agent, viewport=vp, locale='zh-CN', timezone_id='Asia/Shanghai', bypass_csp=True)
            try:
                # 注入防指纹脚本并添加 cookies
                context.add_init_script(stealth_init_script())
            except Exception:
                pass
            try:
                context.add_cookies(parse_cookie_string(self.user_cookie))
            except Exception:
                pass

            page = context.new_page()
            captured_notes = {}
            last_api_base = None
            last_api_params = {}
            last_cursor = None

            def handle_response(response):
                nonlocal last_api_base, last_api_params, last_cursor
                url = response.url
                if "/search/notes" in url or "/fe_api/burdock/webb/v1/search/notes" in url:
                    try:
                        up = urlparse(url)
                        last_api_base = f"{up.scheme}://{up.netloc}{up.path}"
                        last_api_params = {k: v[0] for k, v in parse_qs(up.query).items()}
                        data = response.json()
                        items = data.get("data", {}).get("items") or data.get("data", {}).get("notes") or []
                        for note in items:
                            nid = note.get('id') or note.get('note_card', {}).get('note_id')
                            if nid and nid not in captured_notes:
                                captured_notes[nid] = note
                        d = data.get('data', {})
                        for key in ('cursor', 'next_cursor', 'max_time', 'last_time', 'next_max_time', 'last_id', 'page'):
                            if key in d:
                                last_cursor = d.get(key)
                                break
                        if not last_cursor and isinstance(data.get('pagination'), dict):
                            for key in ('cursor', 'next_cursor', 'last_id'):
                                if key in data['pagination']:
                                    last_cursor = data['pagination'].get(key)
                                    break
                    except Exception:
                        pass

            page.on('response', handle_response)
            page.goto(f"https://www.xiaohongshu.com/search_result?keyword={quote(search_keyword)}", timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(random.uniform(1.5, 3.0))
            # 做一些人为交互以降低被检测概率
            try:
                interact_like_human(page)
            except Exception:
                pass

            scroll_count = 0
            max_scroll = 200
            no_new_image_rounds = 0
            max_no_new_image_rounds = 5  # 连续5次无新增即判定到底
            last_image_count = 0

            while len(self.image_url_set) < max_images and scroll_count < max_scroll:
                scroll_count += 1
                try:
                    if random.random() < 0.6:
                        interact_like_human(page)
                except Exception:
                    pass
                simulate_full_scroll(page, passes=random.randint(2, 4))
                time.sleep(random.uniform(2.5, 5.0))

                for note in list(captured_notes.values()):
                    if len(self.image_url_set) >= max_images:
                        break
                    note_card = note.get('note_card', {})
                    if not note_card:
                        continue
                    cover_info = note_card.get('cover', {})
                    if cover_info:
                        cover_url = cover_info.get('url_default') or cover_info.get('url_pre')
                        if cover_url:
                            self.schedule_download(cover_url, self.save_dir, headers)
                    images = note_card.get('image_list', [])
                    for img in images:
                        if len(self.image_url_set) >= max_images:
                            break
                        trace_id = img.get('trace_id') or img.get('traceId')
                        if trace_id:
                            img_url = f"https://ci.xiaohongshu.com/{trace_id}?imageView2/2/w/format/jpg"
                            self.schedule_download(img_url, self.save_dir, headers)

                try:
                    dom_images = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src || i.getAttribute('data-src')).filter(Boolean)")
                    for src in dom_images:
                        if len(self.image_url_set) >= max_images:
                            break
                        if src.startswith('//'):
                            src = 'https:' + src
                        if src not in self.image_url_set:
                            self.schedule_download(src, self.save_dir, headers)
                except Exception:
                    pass

                logger.info(f"已调度下载数量(去重后): {len(self.image_url_set)}/{max_images}, 滚动次数: {scroll_count}/{max_scroll}")

                # 判断是否到底：连续多次无新增图片
                if len(self.image_url_set) == last_image_count:
                    no_new_image_rounds += 1
                    logger.info(f"本轮无新增图片，连续无新增次数: {no_new_image_rounds}")
                else:
                    no_new_image_rounds = 0
                last_image_count = len(self.image_url_set)
                if no_new_image_rounds >= max_no_new_image_rounds:
                    logger.info(f"连续{max_no_new_image_rounds}次无新增图片，判定已到底，提前切换关键词。")
                    break

                if last_api_base and last_cursor and len(self.image_url_set) < max_images:
                    try:
                        logger.info(f"尝试使用 API 游标翻页: {last_api_base} cursor={last_cursor}")
                        ses_headers = headers.copy()
                        more_fetched = 0
                        session = requests.Session()
                        ses_headers = headers.copy()
                        params = dict(last_api_params)
                        cursor_keys = ('cursor', 'next_cursor', 'max_time', 'last_time', 'last_id', 'page')
                        placed = False
                        for k in cursor_keys:
                            if k in params:
                                params[k] = last_cursor
                                placed = True
                                break
                        if not placed:
                            params['cursor'] = last_cursor

                        while len(self.image_url_set) < max_images:
                            resp = session.get(last_api_base, params=params, headers=ses_headers, timeout=10)
                            if resp.status_code != 200:
                                break
                            j = None
                            try:
                                j = resp.json()
                            except Exception:
                                break
                            items = j.get('data', {}).get('items') or j.get('data', {}).get('notes') or []
                            if not items:
                                break
                            for note in items:
                                nid = note.get('id') or note.get('note_card', {}).get('note_id')
                                if nid and nid not in captured_notes:
                                    captured_notes[nid] = note
                                    note_card = note.get('note_card', {})
                                    cover_info = note_card.get('cover', {})
                                    if cover_info:
                                        cover_url = cover_info.get('url_default') or cover_info.get('url_pre')
                                        if cover_url:
                                            self.schedule_download(cover_url, self.save_dir, headers)
                                    images = note_card.get('image_list', [])
                                    for img in images:
                                        if len(self.image_url_set) >= max_images:
                                            break
                                        trace_id = img.get('trace_id') or img.get('traceId')
                                        if trace_id:
                                            img_url = f"https://ci.xiaohongshu.com/{trace_id}?imageView2/2/w/format/jpg"
                                            self.schedule_download(img_url, self.save_dir, headers)
                                    more_fetched += 1
                            d = j.get('data', {})
                            new_cursor = None
                            for key in ('cursor', 'next_cursor', 'max_time', 'last_time', 'next_max_time', 'last_id', 'page'):
                                if key in d:
                                    new_cursor = d.get(key)
                                    break
                            if not new_cursor and isinstance(j.get('pagination'), dict):
                                for key in ('cursor', 'next_cursor', 'last_id'):
                                    if key in j['pagination']:
                                        new_cursor = j['pagination'].get(key)
                                        break
                            if not new_cursor or new_cursor == last_cursor:
                                break
                            last_cursor = new_cursor
                            for k in cursor_keys:
                                if k in params:
                                    params[k] = last_cursor
                                    break
                            else:
                                params['cursor'] = last_cursor
                            time.sleep(random.uniform(0.5, 1.5))
                        logger.info(f"API 翻页通过游标额外抓取 {more_fetched} 条笔记")
                    except Exception as e:
                        logger.debug(f"API 游标翻页失败: {e}")

            self.shutdown()
            self.save_metadata(os.path.join(self.save_dir, f"metadata_{clean_filename(search_keyword)}.json"))

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
