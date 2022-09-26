from fake_useragent import UserAgent
import aiohttp
import asyncio
import lxml.html
import requests
from dataclasses import dataclass, field, replace


@dataclass
class Article:
    entity = {}
    url: str
    create_date: str = field(default='')
    header: str = field(default='')
    text: str = field(default='')
    
    @classmethod
    def set_entity(cls, entity: dict):
        cls.entity = entity
    
    def parse(self, element):
        data = {_: ' '.join(element.xpath(self.entity[_])) for _ in self.entity}
        return replace(self, **data)
 

def get_proxy_list():
    print ('Получаем список прокси ...')
    result = requests.get("https://free-proxy-list.net/")
    html_page = lxml.html.fromstring(result.text)
    proxies = html_page.xpath('.//table/tbody/tr')
    proxies = ((rec[0].text, rec[1].text) for rec in proxies if rec[4].text=='anonymous' and rec[6].text=='no')
    return iter(proxies)



async def main(url_list: list):
    proxies = get_proxy_list()
    async with aiohttp.ClientSession() as session:
        ua = UserAgent()        
        for url in url_list:
            article = Article(url)
            try:
                proxy_address, proxy_port = next(proxies)
                proxy = f'http://{proxy_address}:{proxy_port}'
            except StopIteration:
                print ('Прокси закончились')
                break
            print (f'Запрос: {url}, прокси: {proxy}')
            async with session.get(url, headers={'User-Agent': ua.random}, proxy=proxy) as resp:
                res = await resp.text()
                element = lxml.html.fromstring(res)
                article = article.parse(element)
                print (article)
                print ('-----------------')
                #await asyncio.sleep(.5)

entity = {
    'create_date': './/article/span/text()',
    'header': './/article/h1/text()',
    'text': './/article/div/p/text()'
}
Article.set_entity(entity)
url_list = [f'http://www.scrf.gov.ru/news/allnews/{num}/' for num in range(3000, 3100)] 
asyncio.run(main(url_list))
