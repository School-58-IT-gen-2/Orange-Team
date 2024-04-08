class Location:
    """Класс, описывающий локации на миссии"""
    def __init__(self, name, connetcted_locations, disguise, witnesses, items):
        self.name = name
        self.connected_locations = connetcted_locations
        self.disguise = disguise
        self.witnesses = witnesses
        self.items = items