import requests
import logging
import time
import random

logger = logging.getLogger("XHS_Downloader")


def download_media(url, save_path, headers, media_type="image", retries=3, backoff_factor=0.6, proxies=None):
    """下载媒体，支持 data:base64；带重试与退避。"""
    # data: URI 支持
    try:
        if url.startswith('data:'):
            header, b64 = url.split(',', 1)
            import base64
            data = base64.b64decode(b64)
            with open(save_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        logger.error(f"解析 data URI 失败: {e}")
        return False

    attempt = 0
    while attempt < retries:
        try:
            # 小的随机延迟作为速率限制
            time.sleep(random.uniform(0.05, 0.25))
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies)
            if resp.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(resp.content)
                return True
            else:
                logger.debug(f"非200响应 {resp.status_code}，url={url}")
                # 针对 429 做特殊退避
                if resp.status_code == 429:
                    retry_after = None
                    try:
                        retry_after = int(resp.headers.get('Retry-After'))
                    except Exception:
                        retry_after = None
                    if retry_after and retry_after > 0:
                        sleep_time = retry_after + random.uniform(0.5, 2.0)
                    else:
                        sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0.5, 2.0)
                    logger.info(f"收到429，等待 {sleep_time:.1f}s 后重试")
                    time.sleep(sleep_time)
                    attempt += 1
                    continue
        except Exception as e:
            logger.debug(f"下载尝试失败 (#{attempt+1}) {url}: {e}")

        attempt += 1
        sleep_time = backoff_factor * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
        time.sleep(sleep_time)

    logger.error(f"下载失败 {url} after {retries} attempts")
    return False
