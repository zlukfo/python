# Парсинг sitemap
# на входе - ссылка на корневой sitemap
# на выходе - файл со списком ссылок на конечные страницы
from lxml import etree
from io import BytesIO 
from urllib.request import urlopen, Request
import gzip

def _get_obj_url(url:str):
    match url.split('.')[-1]:
        case 'xml':
            return urlopen(url)
        case 'gz':
            req = Request(url)
            req.add_header('Accept-Encoding', 'gzip')
            response = urlopen(req)
            content = gzip.decompress(response.read())
            return BytesIO(content)
        case _:
            return BytesIO(b'<sitemapindex></sitemapindex>')


def get_sitemap_url(url: str, type_sitemap_url):
    sitemaps = []
    obj = _get_obj_url(url)
    for _, elem in etree.iterparse(obj):
        if 'loc' in elem.tag.split('}'):    # такое решение чтобы не заморачиваться с неймспейсами
            match elem.text.split('.')[-1]:
                case 'xml' | 'gz':
                    sitemaps.append(elem.text)
                case _:
                    yield elem.text
    
    for sitemap_url in sitemaps:
        obj = _get_obj_url(sitemap_url)
        for _, elem in etree.iterparse(obj):
            if 'loc' in elem.tag.split('}'):
                yield elem.text


def main(root_sitemap_url: str, result_filename: str):
    type_sitemap_url = root_sitemap_url.split('.')[-1]
    urls = get_sitemap_url (root_sitemap_url, type_sitemap_url)
    counter = 0
    with open(result_filename, 'w', encoding='utf-8') as fdw:
        for url in urls:
            fdw.write(f'{url}\n')
            counter +=1
            print (counter, sep='', end='\r')

if __name__ == '__main__':
    RESULT_FILENAME = 'C:\\tmp\\docs\\#learning\\article\\Python\\example\\lenta_link.txt'
    #ROOT_SITEMAP_URL = 'http://www.rbc.ru/sitemap_index.xml'
    ROOT_SITEMAP_URL = 'https://lenta.ru/sitemap.xml.gz'
    main(ROOT_SITEMAP_URL, RESULT_FILENAME)