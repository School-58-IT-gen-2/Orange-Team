from model.player.player import Player


class PlayerInfo:
    """Класс, описывающий данные пользователя"""
    def __init__(self,
                 suspicion_count=0,
                 kills=0,
                 bodies=0,
                 time=0,
                 suit_only=True,
                 illegal_item='',
                 thrown_weapon=False,
                 player_lvl=6,
                 saved_data={},
                 player=Player(),
                 message=-1,
                 carry_on_items=[],
                 loadout={},
                 locations_values={},
                 mission='ica'
                 ):
        
        self.suspicion_count = suspicion_count
        self.kills = kills
        self.bodies = bodies
        self.time = time
        self.suit_only = suit_only
        self.illegal_item = illegal_item
        self.thrown_weapon = thrown_weapon
        self.player_lvl = player_lvl
        self.saved_data = saved_data
        self.mission = mission
        self.completed_challenges = self.saved_data[self.mission]['challenges']
        self.unlocked_disguises = self.saved_data[self.mission]['disguises']
        self.unlocked_locations = self.saved_data[self.mission]['locations']
        self.player = player
        self.message = message
        self.locations_values = locations_values
        self.carry_on_items = carry_on_items
        self.challenges = self.locations_values[self.mission]['challenges']
        self.npcs = self.locations_values[self.mission]['npcs']
        self.targets = self.locations_values[self.mission]['targets']
        self.events = self.locations_values[self.mission]['events']
        self.locations = self.locations_values[self.mission]['locations']
        self.items = self.locations_values[self.mission]['items']
        self.disguises = self.locations_values[self.mission]['disguises']
        self.loadout = loadout

    def change_mission(self, mission: str):
        "Смена миссии и замена соответствующих данных"
        self.mission = mission
        self.completed_challenges = self.saved_data[self.mission]['challenges']
        self.unlocked_disguises = self.saved_data[self.mission]['disguises']
        self.unlocked_locations = self.saved_data[self.mission]['locations']
        self.challenges = self.locations_values[self.mission]['challenges']
        self.npcs = self.locations_values[self.mission]['npcs']
        self.targets = self.locations_values[self.mission]['targets']
        self.events = self.locations_values[self.mission]['events']
        self.locations = self.locations_values[self.mission]['locations']
        self.items = self.locations_values[self.mission]['items']
        self.disguises = self.locations_values[self.mission]['disguises']