"""
@File        :   run_spider.py
@Description :   execute the spider to crawl search data
@Time        :   2024/10/16
"""

from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'search'])