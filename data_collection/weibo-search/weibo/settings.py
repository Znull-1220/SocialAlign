# -*- coding: utf-8 -*-

BOT_NAME = 'weibo'
SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
LOG_LEVEL = 'ERROR'
# time to wait after accessing a page and before accessing the next page, default is 10 seconds
DOWNLOAD_DELAY = 10

# Change `cookie` to your own cookie
DEFAULT_REQUEST_HEADERS = {
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'cookie': 'YOUR_COOKIE',
}
ITEM_PIPELINES = {
    'weibo.pipelines.DuplicatesPipeline': 300,  # remove duplicates
    'weibo.pipelines.CsvPipeline': 301,         # write to csv file
}

# Change the keyword for searching
KEYWORD_LIST = ["xxx"]   # or KEYWORD_LIST = 'keyword_list.txt' 

# obtain all Weibo posts
WEIBO_TYPE = 1
CONTAIN_TYPE = 0
# Search IP address. We do not need to change this value in our task.
REGION = ['全部']
# Change the start date for searching
START_DATE = '2024-10-27'
# end date should be the last day of the date you want to search
END_DATE = '2024-10-28'
# the threshold of further search, if the number of pages is greater than or equal to this value
FURTHER_THRESHOLD = 46
# image file path
IMAGES_STORE = './'
# video file path
FILES_STORE = './'

