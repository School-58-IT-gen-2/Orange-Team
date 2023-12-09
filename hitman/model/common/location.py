class Location:

    def __init__(self, name, connetcted_locations, disguise, witnesses, items):
        self.__name = name
        self.__connected_locations = connetcted_locations
        self.__disguise = disguise
        self.__witnesses = witnesses
        self.__items = items

    def get_witnesses(self):
        return self.__witnesses

    def get_items(self):
        return self.__items

    def set_items(self, items):
        self.__items = items

    def get_connected_locations(self):
        return self.__connected_locations

    def get_name(self):
        return self.__name

    def get_disguise(self):
        return self.__disguise