"""
@File        :   run_spider.py
@Description :   execute the spider to crawl search data
"""

from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'search'])