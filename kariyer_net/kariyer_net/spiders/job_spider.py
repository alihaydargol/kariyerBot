from time import sleep

import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from ..items import KariyerNetItem


exceptional_urls = []

class JobSpider(scrapy.Spider):
    name = "jobs"
    # allowed_domains = ["https://www.kariyer.net/"]

    start_urls = ['https://www.kariyer.net/is-ilanlari']


    def __init__(self):
        self.driver = webdriver.Firefox()

    def try_again(self, appeared, loading):
        delay = 1
        while not appeared or loading:
            sleep(delay)
            scrapy_selector = Selector(text=self.driver.page_source)
            appeared = scrapy_selector.xpath("//div[@class='content knetLoadingWrapper']")
            loading = scrapy_selector.xpath("//div[@class='knetLoadingBig']")
            delay += 1
            if delay > 3:
                break

    def parse(self, response):
        self.driver.get(response.url)
        scrapy_selector = Selector(text=self.driver.page_source)
        links = scrapy_selector.xpath('//a[@class="link position"]/@href').extract()



        for link in links:
            items = KariyerNetItem()
            self.driver.get("https://www.kariyer.net" + link)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(self.driver, 10).until_not(
                EC.presence_of_element_located((By.XPATH, "//div[@class='knetLoadingBig']")))
            scrapy_selector = Selector(text=self.driver.page_source)

            appeared = scrapy_selector.xpath("//div[@class='content knetLoadingWrapper']")
            loading = scrapy_selector.xpath("//div[@class='knetLoadingBig']")

            #aradigimiz element gelmediyse diye yada sayfa hala yukleniyorsa diye kontrol et
            self.try_again(appeared, loading)

            element = scrapy_selector.xpath("//div[@class='content knetLoadingWrapper']").extract()

            loading = scrapy_selector.xpath("//div[@class='content knetLoadingWrapper']").xpath("//div[@class='knetLoadingBig']")

            if loading or len(element) == 0:
                exceptional_urls.append(link)
                self.logger.warning("exceptional url" + str(link))
                continue

            print(element)
            items['title'] = scrapy_selector.xpath("//a[@id='jobTitle']/text()").extract()
            items['company'] = scrapy_selector.xpath("//a[@id='jobCompany']/text()").extract()
            items['location'] = scrapy_selector.xpath("//span[@id='jobCity']/text()").extract()
            items['description'] = scrapy_selector.xpath("//div[@class='genel-nitelikler']/text()").extract()
            #ilan-detay-mid-wrapper



            # scrapy_selector = Selector(text=self.driver.page_source)

            main_content = scrapy_selector.xpath(
                """//h3[contains(., 'GENEL NİTELİKLER VE İŞ TANIMI')]/following-sibling::node()//text()""").extract()



'''
        for link in links:
            self.driver.get("https://www.kariyer.net/"+link)

            #scrapy_selector = Selector(text=self.driver.page_source)
            genel = scrapy_selector.xpath(
                """//h3[contains(., 'GENEL NİTELİKLER VE İŞ TANIMI')]/following-sibling::node()//text()""").extract()

            print(genel)
            if genel:
                items = KariyerNetItem()
                items['ilan_baslik'] = scrapy_selector.xpath('//a[@id="jobTitle"]/text()').extract()
                items['sirket_adi'] = scrapy_selector.xpath('//a[@id="jobCompany"]/text()').extract()
                items['genel_nit_is_tanimi'] = genel
                # items['is_tanimi'] = scrapy_selector.xpath("""//div//h3[starts-with(., 'İŞ TANIMI')]/following-sibling::node()/descendant-or-self::text()""").extract()
                items['tecrube'] = scrapy_selector.xpath(
                    '//div[@class="sub-box aday-kriterleri"]/div[2]/div[1]/div[2]/p/text()').extract()
                items['egitim'] = scrapy_selector.xpath(
                    '//div[@class="sub-box aday-kriterleri"]/div[2]/div[3]/div[2]/p/text()').extract()
                # items['yabanci_dil'] = scrapy_selector.xpath('//div[@class="sub-box aday-kriterleri"]/div[2]/div[4]/div[2]/p/text()').extract()
                items['sektor'] = scrapy_selector.xpath(
                    '//div[@class="sub-box pozisyon-bilgileri"]/div[2]/div[1]/div[2]/p/text()').extract()
                items['departman'] = scrapy_selector.xpath(
                    '//div[@class="sub-box pozisyon-bilgileri"]/div[2]/div[2]/div[2]/p/text()').extract()
                items['calisma_sekli'] = scrapy_selector.xpath(
                    '//div[@class="sub-box pozisyon-bilgileri"]/div[2]/div[3]/div[2]/p/text()').extract()
                items['sehir'] = scrapy_selector.xpath(
                    '//div[@class="sub-box pozisyon-bilgileri"]/div[2]/div[6]/div[2]/p/text()').extract()
                items['label'] = "deneme"
                sleep(1)

                yield items
'''
