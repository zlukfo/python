from dataclasses import dataclass
import dataclasses
@dataclass
class Coordinates:
    lat: float
    lon: float

MyCoordClass = Coordinates


e = MyCoordClass(10,10)
MyCoordClass = dataclasses.make_dataclass(MyCoordClass.__name__, fields=['h', 'lat'], bases=(Coordinates,) )
e = MyCoordClass(10,10,100)
print (e)