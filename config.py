# 爬虫防反爬配置参数
# 根据实际情况调整这些参数以避免触发登录验证

# 关键词之间的冷却时间（秒）
KEYWORD_COOLDOWN_MIN = 15  # 最小冷却时间
KEYWORD_COOLDOWN_MAX = 30  # 最大冷却时间

# 每N个关键词后进行长时间休息
LONG_REST_INTERVAL = 5  # 每5个关键词
LONG_REST_MIN = 60  # 最小休息时间（秒）
LONG_REST_MAX = 90  # 最大休息时间（秒）

# 页面滚动之间的延迟（秒）
SCROLL_DELAY_MIN = 4.0  # 最小延迟
SCROLL_DELAY_MAX = 8.0  # 最大延迟

# 初始页面加载后的等待时间（秒）
PAGE_LOAD_WAIT_MIN = 3.0  # 最小等待
PAGE_LOAD_WAIT_MAX = 6.0  # 最大等待

# API翻页请求之间的延迟（秒）
API_REQUEST_DELAY_MIN = 3.0  # 最小延迟
API_REQUEST_DELAY_MAX = 6.0  # 最大延迟

# 说明：
# 1. 如果还是触发登录验证，可以增大这些数值
# 2. 如果爬取速度太慢，可以适当减小（但有风险）
# 3. 建议在非高峰时段运行爬虫，成功率更高
# 4. 如果频繁触发验证，建议：
#    - 增加 KEYWORD_COOLDOWN 到 30-60秒
#    - 减少 LONG_REST_INTERVAL 到 3-5个关键词
#    - 增加 LONG_REST 到 120-180秒
