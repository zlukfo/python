# Структурирование данных из различных источников
**Теги**: структуры данных, dataclass, python, flatdict
**Пример**: example/example-1.py

**Задача**: Входные исходные данные из различных источников зачастую имеют различную структуру. 
Для того, чтобы выполнять операции с этими данными, например проверка на равенство, сохранение в БД и т.д.
необходимо привести эти данные к единой структуре. Нужен механизм, решающий данную задачу.

## Исходный пример
В качестве примера входных исходных данных будем рассматривать информацию об организациях. Есть два источника данных, предоставляющих информацию в формате JSON. Первый источник предоставляет данные такой структуры
``` json
{
    "name": "Рога и копыта",
    "inn": 1234567890,
    "contact": {
        "phone": "89003441267",
        "email": "company@email.com",
        "address": "Ростов Береговая 1",
    }
}
```
а второй источник - такой
``` json
{
    "FULLNAME": "ООО Рога и копыта",
    "INN": 1234567890,
    "TELEPHOME": "89003441267",
    "MAIL": "company123@email.com",
    "ADDR": "Ростов-на-дону, Нагибина 20"
}
```
## Алгоритм
### 1. Выделяем значимые атрибуты
Под значимыми понимаем атрибуты данных набор которых однозначно идентифицирует экземпляр данных

Например, для организаций значимыми атрибутами могут являться
- ИНН организации
- название
- фактический адрес
Но кроме этого, источники предоставляют другую дополнительную информацию, например контактный телефон и адрес электронной почты.
Этой информацией можно принебречь и не учитывать ее при преобразовании данных а можно также сохранять. В нашем примере примем решение, что дополнительная информация также важна для нас поэтому мы не будем ее игнорировать.

### 2. Описываем структуру данных
Для описания структуры данных удобно использовать датаклассы. Для нашего примера датакласс описывается так
``` python
from dataclasses import dataclass, field
@dataclass
class Company:
    inn: str = field(compare=True)
    name: str = field(default='')
    address: str = field(default='')
    other: list[dict] = field(default_factory=list[dict])
```
Пояснение
- *inn*: ИНН является единственным обязательным атрибутом при создании экземпляра структуры, без него однозначно идентифицировать информацию невозможно. Поэтому он не имеет свойства "значение по умолчанию" - *defaul*. Кроме того, по ИНН будет в будущем выполняться сравнение двух организаций на равенство - "если два экземпляра *Company* имеют одинаковый ИНН - значит это одна и таже организация". Для этого мы присвоили параметру *compare* значение True. 
- *name*, *address*: строковые атрибуты. при получении данных из источников их значения мопут отсутствовать, поэтому для них устанавливаем значение по-умолчанию *defaul* - пустая строка.
- *other*: в этом атрибуте будут сохраняться все дополнительные данные о компании, которые передает источник. Тип атрибута, список, является изменяемым и необязательным объектом Python, поэтому для чтобы корректно определить для него значение по умолчанию - используется *default_factory*

### 3. Задаем связи между структурой и входными данными
Здесь Необходимо описать какие поля источников данных соотвествуют каждому **значимому** атрибуту описанной выше структуры. Наверняка это можно сделать различными способами, но бы импользуем наиболее очевидный - зададим связи через json-объект
``` json
{
    "inn": ["inn", "INN"],
    "name": ["name", "FULLNAME"]
}
```
такой способ подойжет для источников данных с плоской структурой (источник 2). Что делать, если нужные данные находятся на втором, третьем и т.д. уровне вложенности, например *address* в источнике 1?

Здесь поможет библиотека *flatdict*, которая преобразует объекты с многоуровневой структурой в плоские. Используя эту библиотеку связи для поля адреса определим так
``` json
{
    "address": ["ADDR", "contact.address"]
}
``` 
### 4. Пишем функцию преобразования и собираем все вместе
Для того, чтобы наш класс заработал и был полезен, к нему нужно добавить два метода
- **add_entity(entity: dict)** - добавляет в класс описание связей между атрибутами и полями исходных данных
- **create_instance_from_data(data: dict)** - создает на исновании исходных данных экземпляр класса с заполненными значениями атрибутов.

Итак, первый рабочий вариант датакласса выглядит так

``` python
@dataclass
class Company:
    entity = {}

    inn: str = field(compare=True)                 
    name: str = field(compare=False, default='') 
    address: str = field(default='', compare=False)
    other: str = field(default='', compare=False)

    @classmethod
    def add_entity(cls, entity: dict):
        cls.entity |= {i:k for k,v in entity.items() for i in set(v)}

    @classmethod
    def create_instance_from_data(cls, data: dict):
        data = flatdict.FlatDict(data, delimiter='.')
        inc_data = {cls.entity[_]: data.get(_) for _ in data if _ in cls.entity}
        ex_data = {'other': [{_: data[_]} for _ in data if _ not in cls.entity]}
        instance = cls(**(inc_data|ex_data))
        return instance

``` 
Стоит обратить внимание, что 
- *entity* - это атрибут вспомогательный атрибут класса, не экземпляра
- *inn*, *name*, *address*, *other* - атрибуты экземпляров с данными, причем 1) обязательным при создании экземпляра является только *inn* - отсутсвует значение по умолчанию *default*, 2) сравнение экземпляров класса на раверство выполняется только по атрибуту *inn* - свойство *compare* - если два экземпляра класса имеют один инн - значит это одна и та же компания

Примеры использования класса
``` python
Company.add_entity(entity)
Company.add_entity({"address": ["ADDR", "contact.address"]})
c1 = Company.create_instance_from_data(company1)
c2 = Company.create_instance_from_data(company2)
print (c1 == c2)
```
В данном примере 
- в датакласс добавляются связи между атрибутами класса и ключами источников данных
- создается 2 экземпляра датакласса из источников с разной структурой
- выводятся результаты сравнения экземпляров (по инн)

### 5. Добавляем полезные методы работы с экземплярами 
Для нашего примера добавим несколько полезных функциональностей
1) при создании экземпляра из источника данных будем выполнять проверку - чтобы инн состоял из 10-и или 12-и цифр 
2) Если задан адрес компании попытаемся определить ее географические координаты - широту и долготу
3) Если информация об одной компании получена из разных источников (скорее всего разную структуру данных и содержит разные дополнительные данные) - напишем метод, позволяющий пополнить информацию в одном экземпляре за счет дополнительных данных из другого экземпляра

Первые две задачи удобно решаются внутри специального метода **__post_init__**, который вызывается сразу после инициализации экземпляра класса.

Сначала добавим простой класс для геокоординат
``` python
@dataclass
class Coordinates:
    lat: float
    lon: float
```
Затем, атрибут датакласса для зранения координат экземпляра
``` python
@dataclass
class Company:
    ...
    coord: Coordinates = field(init=False, compare=False)  
```
параметр *init=False* показывает, что значение атрибута *coord* будет задано не при инициализации класса, а в методе **__post_init__**

И, наконец, напишем функцию **__post_init__**
``` python
from geopy.geocoders import Nominatim
@dataclass
class Company:
    ...
    def __post_init__(self):           
        # проверяем корректность ввода инн
        self.inn = str(self.inn)
        if not self.inn.isdigit() or len(self.inn) not in [10,12]:
            raise ValueError("ИНН должен состоять из 10 или 12 цифр")        
        
        # пытаемся получить геокоординаты если введен адрес
        if self.address:
            print (f'Получаем геокоординаты компании "{self.name}" по адресу ...')
            geolocator = Nominatim(user_agent='my_app')
            location = geolocator.geocode(self.address)
            self.coord = Coordinates(lat=location.latitude, lon=location.longitude)
        else:
            self.coord = Coordinates(None, None)
```

Третью задачу будем решать так



--------------------
## Объекты
**Объект** - это любая сущность, которая а) характеризуется фиксированным набором свойств - структурой, б) однозначно определяется неизменяемыми значениями этих свойств

Например, сущность - организация. Структурой, описывающей данную сущность может быть следующий набор свойств
- название
- адрес
- инн
- телефон
- email
а объектом, характеризующим конкретную организацию - набор значений этих свойств
- название = "Рога и копыта"
- адрес = "Москва, Красная площадь, 1"
- инн = 1234567890
- телефон = "89004581214"
- email = "roga@mail.ru"
Очевидно, что сами свойства могут быть простыми, например, название - строка, инн - число,
так и иметь собственную составную структуру, например, адрес
- населенный пункт
- улица
- номер дома
Приведенный пример позволяет сформулировать первую важную задачу на этапе проектирования объекта
**Должен быть инструмент, который позволяет выполнять проверку корректности значений, присваиваемых свойствам объекта**

Например, адрес обязательно должен содержать название населенного пункта, улицу и номер, а инн - обязательно должен состоять только из цифр и иметь длину 10 или 12 цифр

Объекты сами по себе мало интересны. Интерес представляют операции над объектами, например
*Операции над одним объектом*
- по адресу получить географические координаты организации
- по инн проверить статус организации (действующая или закрыта)
*Операции над несколькими объектами*
- найти все компании, зарегестрированные по адресу
- по инн проверить являются ли две организации одинаковыми
- определить по email связанные организации (у которых email совпадает)
Отсюда вторая задача проектирования
**Должен быть механизм удобного добавления операций с объектами**

Итак, этап проектирования завершен, приступаем к кодингу - реализации последовательности операций над объектами -
добавление обьектов и совершение над ними различных операций. Отсюда третья задача 
**Должен быть инструмент, минимизирующий ошибки на этапе кодинга**

## Определение структуры объекта

``` python
from dataclasses import dataclass
@dataclass
class Organization:
    name: str
    inn: str
org = Organization(name="qqq", inn="123")
print (org)
```
------------------------------------------------
### Датаклассы
Датаклассы удобны для описания структуры данных

вопросы
- можно ли изменить состав атрибутов класса динамически

да можно вто так
``` python
from dataclasses import dataclass
import dataclasses
@dataclass
class Coordinates:
    lat: float
    lon: float
e = Coordinates(10,10)
Coordinates = dataclasses.make_dataclass(Coordinates.__name__, fields=[("h", float)], bases=(Coordinates,) )
e = Coordinates(10,10,100)
print (e)
```
если тип новых полей заранее не известен можно указать так fields=["h"]

задача - собираем инфу о компаниях и складываем ее в бд
## Практические задачи
1. Данные о компании могут поступать из различных источников и иметь разную структуру. Необходимо приводить их к единой структуре данных по заранее известному образцу
2. Нужен инструмент проверки - являются ди два экземпляра одной компанией или это разные
3. Если два экземпляра компании одинаковые - слить их в одну объединив информацию
4. конвертация экземпляра к виду для записи в бд например json, xml
5. проверка корректности данных атрибутов по маске