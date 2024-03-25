from adapter.hitman_adapter import HitmanAdapter
from model.common.challenges import Challenge
from model.common.npcs import NPC

adapter = HitmanAdapter()

challenges = {i[0]: Challenge(i[0], i[2], False) for i in adapter.get_all('Challenges')}
npcs = {i[0]: NPC(i[2], i[3], True, i[6], i[4], i[0]) for i in adapter.get_all('NPCs')}

print(challenges)
print('\n\n\n')
print(npcs)