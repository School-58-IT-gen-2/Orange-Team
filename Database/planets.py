from adapter import AdapterDB

""" 
любые запросы хорошо чекать на ошибки, поскольку полеты данных - вещь непредсказуемая. 
Если данные не летят/не изменяются, это не всегда очевидно. 
А проверка на подключение поможет искать ошибки миллион лет, когда их на самом деле нет, вы просто до базы достучаться не можете 
    """


class PlanetInDB:
    def __init__(
        self,
        id: int,
        name=None,
    ) -> None:
        self.adapter_db = AdapterDB()
        self.id: int = id
        self.name: str | None = name
        self.__get_planet_by_id()

    def get_planets(self):
        """получить все планеты"""
        planets_list = self.adapter_db.get_all(table_name="Planets")
        return planets_list

    def __get_planet_by_id(self):
        """получить планету по её id"""
        planet = self.adapter_db.get_by_id(table_name="Planets", id=self.id)
        self.name = planet[0][0]


planet = PlanetInDB(id=14)
print(planet.name) 