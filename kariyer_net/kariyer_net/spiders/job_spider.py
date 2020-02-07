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
    start_urls = ['https://www.kariyer.net/is-ilanlari/#&cp=%d' % (n+1) for n in range(0, 3)]

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
        for url in self.start_urls:
            self.driver.get(url)
            scrapy_selector = Selector(text=self.driver.page_source)
            links = scrapy_selector.xpath('//a[@class="link position"]/@href').extract()
            print(url)
            print("Number of links")
            print(len(links))
            print("response url = " + response.url)
            #print("At the page " + self.start_urls.index(response.url))
            print(links)
            for link in links:
                items = KariyerNetItem()
                print("At the link ")
                print(links.index(link))
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
                    self.logger.warning("exceptional url --> " + str(link))
                    continue

                items['title'] = scrapy_selector.xpath("//a[@id='jobTitle']/text()").extract()
                items['company'] = scrapy_selector.xpath("//a[@id='jobCompany']/text()").extract()
                items['location'] = scrapy_selector.xpath("//span[@id='jobCity']/text()").extract()
                items['description'] = scrapy_selector.xpath("//div[@class='genel-nitelikler']/text()").extract()
                items['experience'] = scrapy_selector.xpath("//div[@class='sub-box aday-kriterleri']//div[1]//div[2]/p/text()").extract()

                titles = scrapy_selector.xpath("//div[@class='sub-box aday-kriterleri']/div[@class='content knetLoadingWrapper']/div[@class='row']//p//strong/text()").extract()
                requirement = scrapy_selector.xpath("//div[@class='sub-box aday-kriterleri']//div[2]//div[2]/p/text()").extract()

                for title in titles:
                    index = titles.index(title)
                    if title is "Askerlik Durumu:" or "Military Status:":
                        items['military_obligation'] = requirement[index]
                    if title is "Eğitim Seviyesi:" or "Level of education:":
                        items['education'] = requirement[index]
                    if title is "Yabancı Dil:" or "Languages:":
                        items['languages'] = requirement[index]
                    if title is "Tecrübe:" or "Years of Experience:":
                        items['experience'] = requirement[index]

                titles.clear()
                requirement.clear()

                titles = scrapy_selector.xpath("//div[@class='sub-box pozisyon-bilgileri']/div[@class='content knetLoadingWrapper']/div[@class='row']//p//strong/text()").extract()
                requirement = scrapy_selector.xpath("//div[@class='sub-box pozisyon-bilgileri']//div[2]//div[2]/p/text()").extract()

                for title in titles:
                    index = titles.index(title)
                    if title is "Firma Sektörü:" or "Company Industry:":
                        items['industry'] = requirement[index]
                    if title is "Departman:" or "Job Role:":
                        items['job_role'] = requirement[index]
                    if title is "Çalışma Şekli :" or "Job Type :":
                        items['job_type'] = requirement[index]
                    if title is "Pozisyon Seviyesi:" or "Position Level:":
                        items['position_level'] = requirement[index]
                    if title is "Personel Sayısı:" or  "Number of vacancies:":
                        items['personel_count'] = requirement[index]
                items['application_count'] = scrapy_selector.xpath("//div[@class='basvuru-sayisi']//p//strong/text()").extract()

        yield items



