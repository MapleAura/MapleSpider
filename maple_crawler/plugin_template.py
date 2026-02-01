from .base import BaseCrawler

class ExampleSiteCrawler(BaseCrawler):
    """插件模板：展示如何实现一个站点爬虫插件。

    规范：子类应实现至少一个方法来触发爬取，例如 `crawl()` 或 `crawl_search()`，并在发现媒体时调用 `self.schedule_download(url, save_dir, headers)`。
    """
    def __init__(self, user_cookie=None, save_dir='examples', max_workers=4):
        super().__init__(user_cookie=user_cookie, max_workers=max_workers)
        self.save_dir = save_dir

    def crawl_search(self, keyword: str, max_items: int = 100):
        # 示例伪代码：
        # 1. 构造请求或使用 Playwright 打开页面
        # 2. 解析响应或 DOM，找到图片/视频 URL
        # 3. 对每个媒体 URL 调用 self.schedule_download(url, self.save_dir, headers)
        # 4. 在结束时调用 self.shutdown() 并 self.save_metadata(...)
        raise NotImplementedError('在插件中实现 crawl_search')
