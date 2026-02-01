import os
import uuid
import json
import concurrent.futures
from typing import Dict, Set
from .downloader import download_media
from .utils import clean_filename
import logging
logger = logging.getLogger("XHS_Downloader")

class BaseCrawler:
    def __init__(self, user_cookie: str = None, max_workers: int = 5):
        self.user_cookie = user_cookie
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.image_url_set: Set[str] = set()
        self.metadata: Dict[str, str] = {}

    def schedule_download(self, url: str, save_dir: str, headers: dict) -> None:
        if not url or url in self.image_url_set:
            return
        self.image_url_set.add(url)

        ext = '.jpg'
        parsed_path = url.split('?')[0]
        if '.' in parsed_path:
            possible_ext = os.path.splitext(parsed_path)[1]
            if possible_ext and len(possible_ext) <= 6:
                ext = possible_ext

        filename = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(save_dir, filename)

        future = self.executor.submit(download_media, url, save_path, headers, "image")

        def _cb(fut):
            try:
                ok = fut.result()
                if ok:
                    self.metadata[url] = filename
                    logger.info(f"下载完成: {filename}")
                else:
                    logger.error(f"下载失败: {url}")
            except Exception as e:
                logger.error(f"下载任务异常: {e}")

        future.add_done_callback(_cb)

    def shutdown(self):
        self.executor.shutdown(wait=True)

    def save_metadata(self, path: str):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存元数据: {path}")
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
