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
                 start_location='',
                 start_disguise='',
                 start_items='',
                 player_lvl=10,
                 completed_challenges='',
                 player=Player(),
                 message=-1,
                 challenges={},
                 npcs={},
                 targets=[],
                 events={},
                 locations={},
                 items={},
                 disguises={},
                 carry_on_items=[]
                 ):
        
        self.suspicion_count = suspicion_count
        self.kills = kills
        self.bodies = bodies
        self.time = time
        self.suit_only = suit_only
        self.illegal_item = illegal_item
        self.thrown_weapon = thrown_weapon
        self.start_location = start_location
        self.start_disguise = start_disguise
        self.start_items = start_items
        self.player_lvl = player_lvl
        self.completed_challenges = completed_challenges
        self.player = player
        self.message = message
        self.challenges = challenges
        self.npcs = npcs
        self.targets = targets
        self.events = events
        self.locations = locations
        self.carry_on_items = carry_on_items
        self.items = items
        self.disguises = disguises