import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

class WeiboSpider(scrapy.Spider):
    name = "weibo"
    
    def __init__(self, url=None, *args, **kwargs):
        super(WeiboSpider, self).__init__(*args, **kwargs)
        # Weibo AI search URL, you can change the query keyword and tab
        # The timestamp in the URL will change, so you can only use the URL of the sample page to crawl
        # start url
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = [
                "https://ai.s.weibo.com/web/other/ai/blogs2?dt=1731291448&query=%E4%B8%81%E4%BF%8A%E6%99%96%E5%9B%BD%E9%99%85%E9%94%A6%E6%A0%87%E8%B5%9B%E5%A4%BA%E5%86%A0&tab="
            ]

        chrome_options = Options()
        chrome_options.add_argument("--headless")   # headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)
        try:
            # wait for the page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.van-list'))
            )

            # This is a dynamic page (Javascript), we need to simulate scrolling to load all content
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # `div.cardblog` is the container class for each weibo post
            weibo_posts = self.driver.find_elements(By.CSS_SELECTOR, 'div.cardblog')
            
            for post in weibo_posts:
                # get the current window handle
                main_window = self.driver.current_window_handle
                # click on the post to open the detail page
                # extract user_id, weibo_id and full content in the detail page
                self.driver.execute_script("arguments[0].click();", post)
    
                # wait for the new tab to open
                WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
                # switch to the new window
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # extract user_id
                user_id_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.woo-avatar-main'))
                )
                user_id = user_id_element.get_attribute('usercard')

                # get weibo ID
                current_url = self.driver.current_url
                # URL format: https://weibo.com/user_id/weibo_id
                weibo_id = current_url.split('/')[-1].split('?')[0]

                # full content
                content_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.detail_wbtext_4CRf9'))
                )
                content = content_element.text

                # close the new tab
                self.driver.close()
                # switch back to the main window
                self.driver.switch_to.window(main_window)

                username = post.find_element(By.CSS_SELECTOR, 'div.name').text
                if username and user_id and content:
                    yield {
                        'username': username.strip(),
                        'user_id': user_id.strip(),
                        'weibo_id': weibo_id.strip(),
                        'content': content.strip()
                    }
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
        finally:
            self.driver.quit()