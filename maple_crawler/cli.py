import argparse
import logging
from .xhs import XHSCrawler

logger = logging.getLogger("XHS_Downloader")


def build_parser():
    p = argparse.ArgumentParser(description='crawler_framework CLI — run site crawlers')
    p.add_argument('--site', default='xhs', choices=['xhs'], help='site plugin to use')
    p.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    p.add_argument('--max', '-m', type=int, default=100, help='最大下载数量')
    p.add_argument('--workers', '-w', type=int, default=4, help='并发下载线程数')
    p.add_argument('--out', '-o', default='xhs_images', help='输出目录')
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.site == 'xhs':
        crawler = XHSCrawler(user_cookie=None, save_dir=args.out, max_workers=args.workers)
        crawler.crawl_search(args.keyword, max_images=args.max)
        crawler.shutdown()
        crawler.save_metadata(f"{args.out}/metadata_{args.keyword}.json")
        logger.info(f"完成: 已下载 {len(crawler.metadata)} 个媒体到 {args.out}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
import argparse
import logging
from .xhs import XHSCrawler

logger = logging.getLogger("XHS_Downloader")


def build_parser():
    p = argparse.ArgumentParser(description='Crawler Framework CLI')
    p.add_argument('--site', default='xhs', help='site plugin to use (xhs)')
    p.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    p.add_argument('--max', '-m', type=int, default=100, help='最大抓取数量')
    p.add_argument('--workers', '-w', type=int, default=5, help='并发下载线程数')
    p.add_argument('--save', '-s', default='xhs_images', help='保存目录')
    p.add_argument('--cookie', '-c', default=None, help='Cookie 字符串覆盖配置')
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # 目前只实现 xhs 插件，未来可按 args.site 动态加载
    if args.site != 'xhs':
        logger.error('当前只支持 site=xhs')
        return 1

    crawler = XHSCrawler(user_cookie=args.cookie, save_dir=args.save, max_workers=args.workers)
    crawler.crawl_search(args.keyword, max_images=args.max)
    crawler.shutdown()
    crawler.save_metadata(f"{args.save}/metadata_{args.keyword}.json")
    logger.info(f"完成: 已下载 {len(crawler.metadata)} 个媒体")
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
