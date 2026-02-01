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
from playwright.sync_api import sync_playwright
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
USER_COOKIE = 'abRequestId=c22a669f-bd28-54b3-acd8-25ad5f230e25; xsecappid=xhs-pc-web; a1=19be62f0a727575s2vz9dz5uohq1lh205ei2pr45940000581736; webId=294237e92318706cb21c3844c12a32e0; gid=yjDdKJiyKd2SyjDdKJi80dF4WJW2W2MJhujf32ju27lxAJ48y1xJ8U8882YyWqK82DS44D04; acw_tc=0a0b112717690952225761795e1306d8aea29cf0ad87bae18bfce2858a5738; web_session=0400698f250bd15676e2ad0a473b4b1b11383b; id_token=VjEAAGLwCqEhPzQeTgriN8T3WV08nNVhjp2FxIvgRtXTrTDPyy9uUv9p7jqMvw7jzuBSBgT55GqXYMOxNHyfG47PS+WcNLRUGdkdBmIYsCQpA/qAXNdKFGbeIGT7C+TT/gDJROpv; webBuild=5.7.4; websectiga=3fff3a9f9f07284b62c0f2ebf91a3b10193175c06e4f71492b60e056edcdebb2; sec_poison_id=12eae983-ed06-4b76-8f14-f041b79ff143; loadts=1769096519256'

# def clean_filename(name):
#     """清理文件名，移除非法字符"""
#     return re.sub(r'[^\w\u4e00-\u9fff\s]', '', name)[:100]

# def simulate_human_delay(min_delay=0.5, max_delay=3.0):
#     """模拟人类操作延迟"""
#     delay = random.uniform(min_delay, max_delay)
#     time.sleep(delay)

# def download_media(url, save_path, headers, media_type="image"):
#     """下载图片并保存到本地"""
#     try:
#         response = requests.get(url, headers=headers, timeout=15)
#         if response.status_code == 200:
#             with open(save_path, 'wb') as f:
#                 f.write(response.content)
#             return True
#     except Exception as e:
#         logger.error(f"下载失败 {url}: {str(e)}")
#     return False


# class BaseCrawler:
#     """简单可扩展的爬虫基类。子类实现 `crawl()` 方法完成特定站点爬取逻辑。"""
#     def __init__(self, user_cookie: str = None, max_workers: int = 5):
#         self.user_cookie = user_cookie
#         self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
#         self.image_url_set: Set[str] = set()
#         self.metadata: Dict[str, str] = {}  # url -> filename

#     def schedule_download(self, url: str, save_dir: str, headers: dict) -> None:
#         if not url or url in self.image_url_set:
#             return
#         self.image_url_set.add(url)

#         # 生成 uuid 名称并保留扩展名
#         ext = '.jpg'
#         parsed = urlparse(url)
#         path = parsed.path or ''
#         if '.' in path:
#             possible_ext = os.path.splitext(path)[1]
#             if possible_ext and len(possible_ext) <= 6:
#                 ext = possible_ext

#         filename = f"{uuid.uuid4()}{ext}"
#         save_path = os.path.join(save_dir, filename)

#         # 提交下载任务
#         future = self.executor.submit(download_media, url, save_path, headers, "image")

#         # 当完成时记录结果
#         def _cb(fut):
#             try:
#                 ok = fut.result()
#                 if ok:
#                     self.metadata[url] = filename
#                     logger.info(f"下载完成: {filename}")
#                 else:
#                     logger.error(f"下载失败: {url}")
#             except Exception as e:
#                 logger.error(f"下载任务异常: {e}")

#         future.add_done_callback(_cb)

#     def shutdown(self):
#         self.executor.shutdown(wait=True)

#     def save_metadata(self, path: str):
#         try:
#             with open(path, 'w', encoding='utf-8') as f:
#                 json.dump(self.metadata, f, ensure_ascii=False, indent=2)
#             logger.info(f"已保存元数据: {path}")
#         except Exception as e:
#             logger.error(f"保存元数据失败: {e}")


# class XHSCrawler(BaseCrawler):
#     """小红书爬虫实现（基于原有逻辑），发现图片即调度下载。"""
#     def __init__(self, user_cookie: str, save_dir: str = 'xhs_images', max_workers: int = 5):
#         super().__init__(user_cookie=user_cookie, max_workers=max_workers)
#         self.save_dir = clean_filename(save_dir)
#         os.makedirs(self.save_dir, exist_ok=True)

#     def crawl_search(self, search_keyword: str, max_images: int = 100):
#         user_agent = get_random_user_agent()
#         headers = {
#             'Referer': 'https://www.xiaohongshu.com/',
#             'User-Agent': user_agent,
#             'Cookie': self.user_cookie or ''
#         }

#         logger.info(f"开始爬取(流式下载): '{search_keyword}' (目标数量: {max_images})")

#         with sync_playwright() as p:
#             # 尝试启动浏览器（与原逻辑一致）
#             try:
#                 if os.name == 'nt':
#                     chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
#                 else:
#                     chrome_path = "/usr/bin/google-chrome"
#                 browser = p.chromium.launch(
#                     executable_path=chrome_path,
#                     headless=False,
#                     args=["--disable-blink-features=AutomationControlled", "--disable-infobars"]
#                 )
#             except Exception:
#                 browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])

#             context = browser.new_context(user_agent=user_agent, viewport={"width": 1280, "height": 720}, locale='zh-CN', timezone_id='Asia/Shanghai', bypass_csp=True)
#             # 添加 cookie
#             try:
#                 context.add_cookies(parse_cookie_string(self.user_cookie))
#             except Exception:
#                 pass

#             page = context.new_page()
#             captured_notes = {}
#             # 用于游标分页的追踪
#             last_api_base = None
#             last_api_params = {}
#             last_cursor = None

#             def handle_response(response):
#                 nonlocal last_api_base, last_api_params, last_cursor
#                 url = response.url
#                 if "/search/notes" in url or "/fe_api/burdock/webb/v1/search/notes" in url:
#                     try:
#                         # 记录最后一次调用的 API 基地址与参数，便于后续用 requests 直接翻页
#                         up = urlparse(url)
#                         last_api_base = f"{up.scheme}://{up.netloc}{up.path}"
#                         last_api_params = {k: v[0] for k, v in parse_qs(up.query).items()}

#                         data = response.json()
#                         # 尝试多种字段获取笔记
#                         items = data.get("data", {}).get("items") or data.get("data", {}).get("notes") or []
#                         for note in items:
#                             nid = note.get('id') or note.get('note_card', {}).get('note_id')
#                             if nid and nid not in captured_notes:
#                                 captured_notes[nid] = note

#                         # 尝试从返回数据提取游标信息（通用字段集合）
#                         d = data.get('data', {})
#                         for key in ('cursor', 'next_cursor', 'max_time', 'last_time', 'next_max_time', 'last_id', 'page'):
#                             if key in d:
#                                 last_cursor = d.get(key)
#                                 break
#                         # 有些接口在顶层返回 pagination
#                         if not last_cursor and isinstance(data.get('pagination'), dict):
#                             for key in ('cursor', 'next_cursor', 'last_id'):
#                                 if key in data['pagination']:
#                                     last_cursor = data['pagination'].get(key)
#                                     break
#                     except Exception:
#                         pass

#             page.on('response', handle_response)
#             page.goto(f"https://www.xiaohongshu.com/search_result?keyword={quote(search_keyword)}", timeout=60000)
#             page.wait_for_load_state('networkidle', timeout=30000)
#             time.sleep(random.uniform(1.5, 3.0))

#             scroll_count = 0
#             max_scroll = 200

#             while len(self.image_url_set) < max_images and scroll_count < max_scroll:
#                 scroll_count += 1
#                 simulate_full_scroll(page, passes=random.randint(2, 4))
#                 time.sleep(random.uniform(2.5, 5.0))

#                 # 从已捕获笔记中提取图片并立即下载
#                 for note in list(captured_notes.values()):
#                     if len(self.image_url_set) >= max_images:
#                         break
#                     note_card = note.get('note_card', {})
#                     if not note_card:
#                         continue
#                     cover_info = note_card.get('cover', {})
#                     if cover_info:
#                         cover_url = cover_info.get('url_default') or cover_info.get('url_pre')
#                         if cover_url:
#                             self.schedule_download(cover_url, self.save_dir, headers)

#                     images = note_card.get('image_list', [])
#                     for img in images:
#                         if len(self.image_url_set) >= max_images:
#                             break
#                         trace_id = img.get('trace_id') or img.get('traceId')
#                         if trace_id:
#                             img_url = f"https://ci.xiaohongshu.com/{trace_id}?imageView2/2/w/format/jpg"
#                             self.schedule_download(img_url, self.save_dir, headers)

#                 # 作为补充，从 DOM 抓取图片 URL
#                 try:
#                     dom_images = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src || i.getAttribute('data-src')).filter(Boolean)")
#                     for src in dom_images:
#                         if len(self.image_url_set) >= max_images:
#                             break
#                         if src.startswith('//'):
#                             src = 'https:' + src
#                         if src not in self.image_url_set:
#                             self.schedule_download(src, self.save_dir, headers)
#                 except Exception:
#                     pass

#                 logger.info(f"已调度下载数量(去重后): {len(self.image_url_set)}/{max_images}, 滚动次数: {scroll_count}/{max_scroll}")

#                 # 如果页面滚动无法继续获得新数据，尝试使用捕获到的 API 地址与游标直接拉取更多数据
#                 if last_api_base and last_cursor and len(self.image_url_set) < max_images:
#                     try:
#                         logger.info(f"尝试使用 API 游标翻页: {last_api_base} cursor={last_cursor}")
#                         # 构造 headers 与 cookies
#                         ses_headers = headers.copy()
#                         # 使用 requests 直接翻页，直到没有新数据或达到目标数量
#                         more_fetched = 0
#                         session = requests.Session()
#                         # 将 last_api_params 复制避免修改原始
#                         params = dict(last_api_params)
#                         # 如果参数里已有 cursor-like 字段，替换，否则添加通用字段
#                         cursor_keys = ('cursor', 'next_cursor', 'max_time', 'last_time', 'last_id', 'page')
#                         placed = False
#                         for k in cursor_keys:
#                             if k in params:
#                                 params[k] = last_cursor
#                                 placed = True
#                                 break
#                         if not placed:
#                             # 放到一个常见的字段名
#                             params['cursor'] = last_cursor

#                         while len(self.image_url_set) < max_images:
#                             resp = session.get(last_api_base, params=params, headers=ses_headers, timeout=10)
#                             if resp.status_code != 200:
#                                 break
#                             j = None
#                             try:
#                                 j = resp.json()
#                             except Exception:
#                                 break
#                             items = j.get('data', {}).get('items') or j.get('data', {}).get('notes') or []
#                             if not items:
#                                 break
#                             for note in items:
#                                 nid = note.get('id') or note.get('note_card', {}).get('note_id')
#                                 if nid and nid not in captured_notes:
#                                     captured_notes[nid] = note
#                                     # 立即调度下载
#                                     note_card = note.get('note_card', {})
#                                     cover_info = note_card.get('cover', {})
#                                     if cover_info:
#                                         cover_url = cover_info.get('url_default') or cover_info.get('url_pre')
#                                         if cover_url:
#                                             self.schedule_download(cover_url, self.save_dir, headers)
#                                     images = note_card.get('image_list', [])
#                                     for img in images:
#                                         if len(self.image_url_set) >= max_images:
#                                             break
#                                         trace_id = img.get('trace_id') or img.get('traceId')
#                                         if trace_id:
#                                             img_url = f"https://ci.xiaohongshu.com/{trace_id}?imageView2/2/w/format/jpg"
#                                             self.schedule_download(img_url, self.save_dir, headers)
#                                     more_fetched += 1
#                             # 更新游标
#                             d = j.get('data', {})
#                             new_cursor = None
#                             for key in ('cursor', 'next_cursor', 'max_time', 'last_time', 'next_max_time', 'last_id', 'page'):
#                                 if key in d:
#                                     new_cursor = d.get(key)
#                                     break
#                             if not new_cursor and isinstance(j.get('pagination'), dict):
#                                 for key in ('cursor', 'next_cursor', 'last_id'):
#                                     if key in j['pagination']:
#                                         new_cursor = j['pagination'].get(key)
#                                         break
#                             if not new_cursor or new_cursor == last_cursor:
#                                 break
#                             last_cursor = new_cursor
#                             # 将新 cursor 放回 params
#                             for k in cursor_keys:
#                                 if k in params:
#                                     params[k] = last_cursor
#                                     break
#                             else:
#                                 params['cursor'] = last_cursor
#                             time.sleep(random.uniform(0.5, 1.5))
#                         logger.info(f"API 翻页通过游标额外抓取 {more_fetched} 条笔记")
#                     except Exception as e:
#                         logger.debug(f"API 游标翻页失败: {e}")

#             # 等待所有下载完成并保存映射
#             self.shutdown()
#             self.save_metadata(os.path.join(self.save_dir, f"metadata_{clean_filename(search_keyword)}.json"))

#             try:
#                 page.close()
#             except Exception:
#                 pass
#             try:
#                 context.close()
#             except Exception:
#                 pass
#             try:
#                 browser.close()
#             except Exception:
#                 pass


# def get_random_user_agent():
#     """生成随机User-Agent"""
#     browsers = [
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}) Gecko/20100101 Firefox/{version}",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
#     ]
    
#     template = random.choice(browsers)
    
#     if "Chrome" in template:
#         version = f"{random.randint(120, 126)}.0.{random.randint(0, 9999)}.{random.randint(0, 999)}"
#     elif "Firefox" in template:
#         version = f"{random.randint(115, 125)}.0"
#     elif "Safari" in template:
#         version = f"{random.randint(15, 17)}.{random.randint(0, 5)}"
    
#     return template.format(version=version)

# def simulate_human_scroll(page, scroll_count=3):
#     """模拟人类滚动行为"""
#     logger.info(f"模拟人类滚动行为 ({scroll_count}次)...")
    
#     for i in range(scroll_count):
#         scroll_height = page.evaluate("document.body.scrollHeight")
#         scroll_amount = random.randint(int(scroll_height * 0.3), int(scroll_height * 0.8))
#         scroll_speed = random.randint(100, 500)
#         scroll_time = scroll_amount / scroll_speed
        
#         page.evaluate(f"""
#             new Promise(resolve => {{
#                 const start = performance.now();
#                 const scrollTo = {scroll_amount};
                
#                 function scrollStep(timestamp) {{
#                     const elapsed = timestamp - start;
#                     const progress = Math.min(elapsed / {scroll_time * 1000}, 1);
#                     const currentScroll = progress * scrollTo;
                    
#                     window.scrollTo(0, currentScroll);
                    
#                     if (progress < 1) {{
#                         requestAnimationFrame(scrollStep);
#                     }} else {{
#                         resolve();
#                     }}
#                 }}
                
#                 requestAnimationFrame(scrollStep);
#             }});
#         """)
        
#         pause_time = random.uniform(1.0, 4.0)
#         time.sleep(pause_time)
        
#         logger.debug(f"滚动 {i+1}/{scroll_count} 完成 (距离: {scroll_amount}px, 暂停: {pause_time:.1f}秒)")

# def simulate_full_scroll(page, passes=3):
#     """多次向页面底部滚动以触发懒加载（更激进）"""
#     logger.info(f"执行全页滚动 {passes} 次以触发懒加载...")
#     for i in range(passes):
#         try:
#             page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#         except Exception:
#             break
#         sleep_time = random.uniform(1.5, 4.0)
#         time.sleep(sleep_time)
#         logger.debug(f"全页滚动 {i+1}/{passes} 完成，暂停 {sleep_time:.1f} 秒")

# def parse_cookie_string(cookie_str):
#     """将Cookie字符串解析为字典列表"""
#     cookies = []
#     for item in cookie_str.split(';'):
#         item = item.strip()
#         if not item:
#             continue
#         if '=' in item:
#             name, value = item.split('=', 1)
#             cookies.append({
#                 'name': name,
#                 'value': value,
#                 'domain': '.xiaohongshu.com',
#                 'path': '/'
#             })
#     return cookies

# def get_xhs_images(search_keyword, max_images=100, save_dir="xhs_images"):
#     """爬取小红书搜索结果的图片"""
#     cleaned_dir = clean_filename(save_dir)
#     os.makedirs(cleaned_dir, exist_ok=True)
#     image_list = []
#     user_agent = get_random_user_agent()
#     logger.info(f"开始爬取: '{search_keyword}' (目标数量: {max_images})")

#     with sync_playwright() as p:
#         try:
#             if os.name == 'nt':
#                 chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
#             else:
#                 chrome_path = "/usr/bin/google-chrome"
#             browser = p.chromium.launch(
#                 executable_path=chrome_path,
#                 headless=False,
#                 args=[
#                     "--disable-blink-features=AutomationControlled",
#                     "--disable-infobars",
#                     "--start-maximized",
#                     "--disable-web-security",
#                     "--disable-site-isolation-trials",
#                     "--disable-features=IsolateOrigins,site-per-process"
#                 ]
#             )
#             logger.info("使用系统自带的Chrome浏览器")
#         except Exception as e:
#             logger.error(f"系统Chrome启动失败: {str(e)}")
#             try:
#                 browser = p.chromium.launch(
#                     headless=False,
#                     args=[
#                         "--disable-blink-features=AutomationControlled",
#                         "--disable-infobars",
#                         "--start-maximized",
#                         "--disable-web-security",
#                         "--disable-site-isolation-trials",
#                         "--disable-features=IsolateOrigins,site-per-process"
#                     ]
#                 )
#                 logger.info("使用Playwright自带的Chromium")
#             except Exception as e2:
#                 logger.error(f"浏览器启动失败: {str(e2)}")
#                 browser = None

#         if browser:
#             try:
#                 context = browser.new_context(
#                     user_agent=user_agent,
#                     viewport={"width": 1280, "height": 720},
#                     locale="zh-CN",
#                     timezone_id="Asia/Shanghai",
#                     bypass_csp=True
#                 )
#                 context.add_init_script("""
#                     delete navigator.__proto__.webdriver;
#                     Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#                     Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#                     Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
#                     Object.defineProperty(navigator, 'language', {get: () => 'zh-CN'});
#                 """)
#                 cookies_list = parse_cookie_string(USER_COOKIE)
#                 context.add_cookies(cookies_list)
#                 logger.info(f"已添加 {len(cookies_list)} 个Cookie")
#                 page = context.new_page()
#                 page.goto("https://www.xiaohongshu.com/", timeout=60000)
#                 time.sleep(2)
#                 page = context.new_page()

#                 # 新增：用set存储已处理的note_id，累积所有笔记
#                 all_notes = dict()  # note_id: note

#                 def handle_response(response):
#                     url = response.url
#                     if "/search/notes" in url or "/fe_api/burdock/webb/v1/search/notes" in url:
#                         try:
#                             data = response.json()
#                             items = data.get("data", {}).get("items") or data.get("data", {}).get("notes") or []
#                             for note in items:
#                                 note_id = note.get("id") or note.get("note_card", {}).get("note_id")
#                                 if note_id and note_id not in all_notes:
#                                     all_notes[note_id] = note
#                             if items:
#                                 logger.info(f"捕获到AJAX响应，累计笔记总数: {len(all_notes)}")
#                         except Exception as e:
#                             logger.error(f"解析AJAX响应失败: {str(e)}")

#                 page.on("response", handle_response)
#                 encoded_keyword = quote(search_keyword)
#                 search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}"
#                 logger.info(f"访问搜索页面: {search_url}")
#                 page.goto(search_url, timeout=60000)
#                 page.wait_for_load_state("networkidle", timeout=30000)
#                 time.sleep(random.uniform(2.0, 5.0))

#                 scroll_count = 0
#                 max_scroll = 100  # 提高滚动上限以抓取更多内容
#                 last_image_count = 0
#                 image_url_set = set()

#                 while len(image_list) < max_images and scroll_count < max_scroll:
#                     scroll_count += 1
#                     # 使用更激进的全页滚动触发懒加载
#                     simulate_full_scroll(page, passes=random.randint(2, 4))
#                     wait_time = random.uniform(3.0, 6.0)
#                     logger.info(f"等待 {wait_time:.1f}秒加载更多内容...")
#                     time.sleep(wait_time)

#                     # 尝试等待搜索API响应，若有新的响应会被 handle_response 捕获
#                     try:
#                         page.wait_for_response(lambda r: "/search/notes" in r.url or "/fe_api/burdock/webb/v1/search/notes" in r.url, timeout=3000)
#                         logger.debug("检测到新的搜索API响应")
#                     except Exception:
#                         logger.debug("等待搜索API响应超时（或无新响应）")

#                     # 新增：从DOM中抓取图片作为备选来源（防止AJAX响应无法捕获）
#                     try:
#                         dom_images = page.evaluate("""
#                             () => {
#                                 const imgs = Array.from(document.querySelectorAll('img'));
#                                 return imgs.map(i => i.src || i.getAttribute('data-src') || i.getAttribute('data-original')).filter(Boolean);
#                             }
#                         """)
#                         for src in dom_images:
#                             if not src:
#                                 continue
#                             if src.startswith('//'):
#                                 src = 'https:' + src
#                             if src.startswith('/'):
#                                 src = 'https://www.xiaohongshu.com' + src
#                             # 只保留常见图片域名或ci.xiaohongshu的资源
#                             if 'ci.xiaohongshu.com' in src or 'xiaohongshu.com' in src or src.endswith(('.jpg', '.jpeg', '.png', '.gif')):
#                                 if src not in image_url_set and len(image_list) < max_images:
#                                     image_list.append(src)
#                                     image_url_set.add(src)
#                         if dom_images:
#                             logger.info(f"从DOM抓取到图片: {len(dom_images)}，累计图片: {len(image_list)}")
#                     except Exception as e:
#                         logger.debug(f"DOM图片抓取失败: {e}")

#                     # 新增：遍历所有累计的note，提取图片并去重
#                     new_images_added = False
#                     for note in all_notes.values():
#                         if len(image_list) >= max_images:
#                             break
#                         note_card = note.get("note_card", {})
#                         if not note_card:
#                             continue
#                         cover_info = note_card.get("cover", {})
#                         if cover_info:
#                             cover_url = cover_info.get("url_default") or cover_info.get("url_pre")
#                             if cover_url and cover_url not in image_url_set:
#                                 image_list.append(cover_url)
#                                 image_url_set.add(cover_url)
#                                 new_images_added = True
#                                 logger.debug(f"添加封面图: {cover_url}")
#                         images = note_card.get("image_list", [])
#                         for img in images:
#                             if len(image_list) >= max_images:
#                                 break
#                             trace_id = img.get("trace_id") or img.get("traceId")
#                             if trace_id:
#                                 img_url = f"https://ci.xiaohongshu.com/{trace_id}?imageView2/2/w/format/jpg"
#                                 if img_url not in image_url_set:
#                                     image_list.append(img_url)
#                                     image_url_set.add(img_url)
#                                     new_images_added = True
#                                     logger.debug(f"添加图片: {img_url}")

#                     logger.info(f"当前图片总数: {len(image_list)}/{max_images}, 滚动次数: {scroll_count}/{max_scroll}")
#                     if not new_images_added:
#                         logger.info("没有新图片，停止滚动")
#                         break

#                 logger.info(f"最终获取图片数量: {len(image_list)}")
#             except Exception as e:
#                 logger.error(f"Playwright操作失败: {str(e)}")
#             finally:
#                 if page:
#                     page.close()
#                 if context:
#                     context.close()
#                 browser.close()
#         else:
#             # 浏览器启动失败时的备选方案
#             headers = {
#                 'User-Agent': user_agent,
#                 'Referer': 'https://www.xiaohongshu.com/',
#                 'Cookie': USER_COOKIE
#             }
#             try:
#                 search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(search_keyword)}"
#                 response = requests.get(search_url, headers=headers, timeout=15)
#                 html_content = response.text
#                 soup = BeautifulSoup(html_content, 'html.parser')
#                 media_items = soup.select('div.note-item img')
                
#                 for item in media_items:
#                     if len(image_list) >= max_images:
#                         break
#                     img_url = item.get('src') or item.get('data-src')
#                     if img_url:
#                         if not img_url.startswith('http'):
#                             img_url = 'https:' + img_url
#                         image_list.append(img_url)
                
#                 logger.info(f"直接请求找到 {len(image_list)} 个图片")
#             except Exception as e:
#                 logger.error(f"直接请求失败: {str(e)}")
#                 return 0
    
#     # 下载图片文件
#     headers = {
#         'Referer': 'https://www.xiaohongshu.com/',
#         'User-Agent': user_agent,
#         'Cookie': USER_COOKIE
#     }
    
#     logger.info(f"开始下载 {len(image_list)} 个图片文件")
#     success_count = 0
#     safe_keyword = clean_filename(search_keyword)
    
#     for i, url in enumerate(image_list[:max_images]):
#         simulate_human_delay()  # 随机延迟防止请求过快
        
#         filename = f"{i+1}_{safe_keyword}.jpg"
#         save_path = os.path.join(cleaned_dir, filename)
        
#         if download_media(url, save_path, headers):
#             logger.info(f"✅ 已下载 [{i+1}/{len(image_list)}]: {os.path.basename(save_path)}")
#             success_count += 1
#         else:
#             logger.error(f"❌ 下载失败: {url}")
    
#     logger.info(f"下载完成! 成功: {success_count}/{min(len(image_list), max_images)}")
#     return success_count

if __name__ == "__main__":
    print("=" * 50)
    print("小红书图片下载工具")
    print("=" * 50)
    
    keyword =  "宠物监控视频"
    max_items = 200
    
    logger.info(f"搜索关键词: {keyword}")
    logger.info(f"最大下载数量: {max_items}")
    
    start_time = time.time()
    # 使用新框架的 XHSCrawler 进行流式爬取与下载
    from maple_crawler.xhs import XHSCrawler
    crawler = XHSCrawler(user_cookie=USER_COOKIE, save_dir='xhs_images', max_workers=8)
    crawler.crawl_search(keyword, max_images=max_items)

    success_count = len(crawler.metadata)
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 50)
    print(f"任务完成! 成功下载 {success_count} 张图片")
    print(f"总耗时: {elapsed_time:.1f} 秒 ({elapsed_time/60:.1f} 分钟)")
    print("=" * 50) 