#import curio
import asyncio
from weakref import proxy
import aiohttp
import time
import lxml.html
from dataclasses import dataclass, field, replace
import requests
from fake_useragent import UserAgent

@dataclass
class Article:
    entity: dict
    url: str = field(default='')
    create_date: str = field(default='')
    header: str = field(default='')
    text: str = field(default='')
        
    def parse(self, element):
        data = {_: ' '.join(element.xpath(self.entity[_])) for _ in self.entity}
        return replace(self, **data)


class Proxies:
    proxy_list = []
    proxy_index = 0

    def __init__ (self, url: str):
        print (f'{time.ctime()} Получаем список прокси ...')
        self._get_proxies_from_site(url)

    def _get_proxies_from_site(self, url: str) ->list:
        # Заточен для получения прокси с сайта free-proxy-list
        html_page = requests.get(url).text
        html_page = lxml.html.fromstring(html_page)
        proxies = html_page.xpath('.//table/tbody/tr')
        self.proxy_list =  [f'http://{rec[0].text}:{rec[1].text}' for rec in proxies if rec[4].text=='anonymous' and rec[6].text=='no']

    async def get_article(self, article: Article, href: str) -> Article:
        article.url = href
        fail_attempt = 0
        while self.proxy_index < len(self.proxy_list):
            current_proxy = self.proxy_list[self.proxy_index]
            print (f'{time.ctime()} Страница: {href} Прокси использовано/всего {self.proxy_index + 1}/{len(self.proxy_list)}')
            async with aiohttp.ClientSession() as session:
                ua = UserAgent()
                try:
                    async with session.get(href, headers={'User-Agent': ua.random}, proxy=proxy) as resp:                
                        resp = await resp.text()
                        element = lxml.html.fromstring(resp)
                        article = article.parse(element)
                except:
                    # если ошибка соединения - следующий прокси
                    print (f'Получить данные через прокси {current_proxy} не удалось')
                    self.proxy_index += 1
            if article.header:    
                return article
            # если ничего не распарсилось (например, страница не существует)
            self.proxy_index += 1
            fail_attempt += 1
            if fail_attempt > 2:
                print ('Невозможно распознать страницу')
                return
        print ('Прокси закончились!!')
        return

def get_parse_list():
    data = [
        {
            'schema': {
                'create_date': './/article/span/text()',
                'header': './/article/h1/text()',
                'text': './/article/div/p/text()'
            },
            'href_list': [f'http://www.scrf.gov.ru/news/allnews/{num}/' for num in range (3000, 3100)]
        }
    ]
    return data


async def main():
    source_list = get_parse_list()
    proxy = Proxies('https://free-proxy-list.net/')

    for source in source_list:
        article = Article(source['schema'])
        source_hrefs = source['href_list']     
        for href  in source_hrefs:
            data = await proxy.get_article(article, href)
            if data:
                print (data.header)

if __name__ == '__main__':
    asyncio.run(main())


'''
proxy = Proxies('https://free-proxy-list.net/')
entity = {
    'create_date': './/article/span/text()',
    'header': './/article/h1/text()',
    'text': './/article/div/p/text()'
}
Article.set_entity(entity)
proxy.get_page('http://www.scrf.gov.ru/news/allnews/3000/')
'''
#print (p.proxy_list)


'''
async def f(n):
    print (f'Начало выполнения {n}: {time.ctime()}')
    await curio.sleep(n)
    print (f'Конец выполнения {n}: {time.ctime()}')


async def parent():
    print (f'Старт программы: {time.ctime()}')
    # spawn запускает конкурентную функцию
    f_small = await curio.spawn(f, 2)
    f_big = await curio.spawn(f, 5)

    # join означает что нужно отследивать окончание функции и получение результата
    await f_small.join()
    await f_big.join()

if __name__ == '__main__':
    curio.run(parent, with_monitor=True)
'''