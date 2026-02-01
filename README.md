crawler_framework
=================

一个轻量的爬虫框架（模块化），包含：

- `BaseCrawler`：下载调度、并发线程池、元数据保存。
- `XHSCrawler`：小红书示例实现（Playwright + DOM/AJAX混合抓取+游标翻页）。
- `downloader`：支持 `data:` base64 与 HTTP 下载。
- `plugin_template.py`：插件模板，便于扩展其它站点。

快速开始
--------

1. 安装依赖（建议使用虚拟环境）：

```bash
pip install -r requirements.txt
# Playwright 需要手动安装浏览器
python -m playwright install
```

2. 可直接以开发模式安装包（可选）：

```bash
pip install -e .
```

3. 运行示例（在工作目录下）：

```bash
python - <<'PY'
from crawler_framework.xhs import XHSCrawler
from spider import USER_COOKIE
c = XHSCrawler(USER_COOKIE, save_dir='xhs_images_example', max_workers=4)
c.crawl_search('宠物监控视频', max_images=50)
print('downloaded', len(c.metadata))
PY
```

扩展新站点
---------

复制 `crawler_framework/plugin_template.py`，并实现 `crawl_search` 或 `crawl` 方法；在发现媒体资源时调用：

```py
self.schedule_download(media_url, save_dir, headers)
```

下一步建议
---------

- 添加 CLI（`argparse`）以便从命令行运行关键词/线程/数量参数。
- 添加重试与速率限制到 `downloader`。 

如需我继续添加 CLI 或将包发布到内部私有 PyPI，请告诉我。