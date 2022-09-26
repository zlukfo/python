# парсинг страниц новостных сайтов
# Не асинхронный вариант
# на входе - 1) схема разбора стариницы (xpath пути к дате публикации, заголовку, тексту) 2) массив прямых ссылок на страницы новостей
# на выходе корпус новостей - каталог в котором 1 файл - 1 новость
import time
import lxml.html
from dataclasses import dataclass, field, replace
from rutimeparser import parse
from pathlib import Path

import requests
from fake_useragent import UserAgent
import re

@dataclass
class Article:
    entity: dict
    url: str = field(default='')
    create_date: str = field(default='')
    header: str = field(default='')
    text: str = field(default='')
        
    def parse(self, xml_element):
        try:
            data = {_: ' '.join(xml_element.xpath(self.entity[_])) for _ in self.entity}
        except TypeError as e:
            print (e)
            return
        return replace(self, **data)
    
    def prepare(self):
        clear = re.compile('[\n\t\ ]+')
        self.header = clear.sub(' ', self.header)
        self.text = clear.sub(' ', self.text)
        try:
            self.create_date = parse(self.create_date).strftime(r"%Y/%m/%d %H:%M:%S")
        except:
            print ('Невозможно распарсить дату')


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

    def get_article(self, article: Article, href: str) -> Article:
        article.url = href
        ua = UserAgent()
        fail_attempt = 0
        while self.proxy_index < len(self.proxy_list):
            if fail_attempt > 2:
                print ('Невозможно распознать страницу')
                return

            current_proxy = self.proxy_list[self.proxy_index]
            print (f'{time.ctime()} Страница: {href} Прокси использовано/всего {self.proxy_index + 1}/{len(self.proxy_list)}')
            try:
                resp = requests.get(href, headers={'User-Agent': ua.random}, proxies={'http': current_proxy})
                resp = resp.text
            except:
                # если ошибка соединения - следующий прокси
                print (f'Получить данные через прокси {current_proxy} не удалось')
                self.proxy_index += 1
                fail_attempt += 1
                continue
            
            # !!! при тестах редкая ошибка вылезла здесь (вернуться позже)
            # ValueError: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
            element = lxml.html.fromstring(resp)
            article = article.parse(element)            
            if not article:
                print ('Ошибка в схеме данных')
                return    
            return article
        print ('Прокси закончились!!')
        return

def get_parse_list():
    data = {
            # совет безопасности РФ
            'sovbez':{
                'schema': {
                    'create_date': './/article/span/text()',
                    'header': './/article/h1/text()',
                    'text': './/article/div/p/text()'
                },
                'href_list': [f'http://www.scrf.gov.ru/news/allnews/{num}/' for num in range (1, 3500)]
            },
            'rbc':{
                'schema': {
                    'create_date': './/time/@content',   # в атрибуте
                    'header': './/h1/text()',
                    'text': './/div/p/text()'
                },
                'href_list': [line[:-1] for line in open('C:\\tmp\\docs\\#learning\\article\\Python\\example\\rbc_link.txt')]
            },
        }

    return data

    


def main2(source: str, proxy: str, corpus_path_parse: str, test=True):

    start_time = time.ctime()

    source = get_parse_list()[source]
    proxy = Proxies(proxy)

    article = Article(source['schema'])
    source_hrefs = source['href_list']

    if test == True:
        source_hrefs = source_hrefs[:3]

    for href  in source_hrefs:
        data = proxy.get_article(article, href)
        if data:
            data.prepare()
            with open(corpus_path_parse+f'\\{href.split("/")[-1]}.txt', 'w', encoding='utf-8') as fdw:
                fdw.write(f'{data.create_date}\n')
                fdw.write(f'{href}\n')
                fdw.write(f'{data.header}\n')
                fdw.write(f'{data.text}')

            print (data.header)

    print (f'СТАРТ - {start_time} ФИНИШ - {time.ctime()}')


def main(source: str, proxy: str, corpus_path_parse: str):

    start_time = time.ctime()

    source_list = get_parse_list()
    proxy = Proxies('https://free-proxy-list.net/')

    for source in source_list:
        article = Article(source['schema'])
        source_hrefs = source['href_list']     
        for href  in source_hrefs:
            data = proxy.get_article(article, href)
            if data:
                print (data.header)
    
    print (f'СТАРТ - {start_time} ФИНИШ - {time.ctime()}')


if __name__ == '__main__':
    SOURCE = 'rbc'
    PROXY = 'https://free-proxy-list.net/'
    CORPUS_PATH_PARSE = f'C:\\tmp\\docs\\#learning\\article\\Python\\example\\corpus\\{SOURCE}'
    Path(CORPUS_PATH_PARSE).mkdir(parents=True, exist_ok=True)
    #main()
    main2 (SOURCE, PROXY, CORPUS_PATH_PARSE, test=False)


