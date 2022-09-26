from dataclasses import dataclass, field, replace
import dataclasses
import flatdict
from geopy.geocoders import Nominatim

# Примеры исходных данных разной структуры
company1 = {
    'name': 'Рога и копыта',
    'inn': 234567890098,
    'contact': {
        'phone': '89003441267',
        'email': 'company@email.com',
        'address': 'Ростов Береговая 1',
    }
}

company2 = {
    'FULLNAME': 'ООО Рога и копыта',
    'INN': 1234567890,
    'TELEPHOME': '89003441267',
    'MAIL': 'company123@email.com',
    'ADDR': 'Ростов-на-дону, Нагибина 20'
}

# Задача 1 если субъект имеет вложенную структуру - развернуть его в плоский вид

# Задача 2 сопоставить имена исходных ключей с атрибутами Company
# задаем соотвествие для каждого атрибута класса Company возмоные интерпретации

entity = {
    'inn': ['inn', 'INN'],
    'name': ['name', 'FULLNAME']
}

@dataclass
class Coordinates:
    lat: float
    lon: float

@dataclass
class Company:
    entity = {}

    inn: str = field(compare=True)                 
    name: str = field(compare=False, default='') 
    address: str = field(default='', compare=False)
    other: str = field(default='', compare=False)

    def __post_init__(self):                    # ... но необходимо определить в post_init
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


Company.add_entity(entity)
Company.add_entity({"address": ["ADDR", "contact.address"]})
c1 = Company.create_instance_from_data(company1)
c2 = Company.create_instance_from_data(company2)
print (c1 == c2)
print (c1.coord, c2.coord)


'''
@dataclass
class Coordinates:
    lat: float
    lon: float

@dataclass
class Organization:
    name: str = field(compare=False)                        # поля без значения по умолчанию должны описыватся вначале
    inn: str = field(compare=True)    # compare позволяет указать какие поля будут проверяться при сравнении значений на равенство   
    address: str = ''                                # после них можно создавать поля ср значение по умолчанию
    phone: set[str] = field(default_factory=set)
    coord: Coordinates = field(init=False, compare=False)   # не задавать значения при создании эеземпляра ...

    def __post_init__(self):                    # ... но необходимо определить в post_init
        # проверяем корректность ввода инн
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
        
    def __iadd__ (self, other):
        self.phone |= set(other.phone)
        return self    

# если указан адрес - автоматически при создании объекта получаем геокоординаты
#org = Organization(name='qqq', inn='3333333333', address='Ростов на дону Нагибина 40')
#print (org)

# по инн спроверяем являются ли два объекта одной и той же компанией
org1 = Organization(name='qqq', inn='2222222222')
org2 = Organization(name='q', inn='111111111111', phone=['1234'])
print (org1 == org2)

# объединяем инфу о компаниях с одинаковым инн
org1 += org2
print (org1)
'''