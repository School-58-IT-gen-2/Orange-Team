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
                 player_lvl=10,
                 completed_challenges='',
                 unlocked_disguises='',
                 unlocked_locations='',
                 player=Player(),
                 message=-1,
                 challenges={},
                 npcs={},
                 targets=[],
                 events={},
                 locations={},
                 items={},
                 disguises={},
                 carry_on_items=[],
                 loadout={}
                 ):
        
        self.suspicion_count = suspicion_count
        self.kills = kills
        self.bodies = bodies
        self.time = time
        self.suit_only = suit_only
        self.illegal_item = illegal_item
        self.thrown_weapon = thrown_weapon
        self.player_lvl = player_lvl
        self.completed_challenges = completed_challenges
        self.unlocked_disguises = unlocked_disguises
        self.unlocked_locations = unlocked_locations
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
        self.loadout = loadout
