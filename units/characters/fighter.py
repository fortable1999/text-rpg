from units.characters import Character
from settings import TURN_CONST


class Fighter(Character):

    name = "Fighter"
    initiative = 10.0

    unit_hp = 10
    unit_mp = 10
    unit_hp_max = 10
    unit_mp_max = 10
    unit_damage = "1d2"
    unit_attack = 0
    unit_defence = 1
    action_list = {
        "short_sword": {
            'skill_attack': 1,
            'skill_damage': '1d4',
            'skill_cost': 0,
            'skill_cooldown': TURN_CONST,
            'skill_effect': None,
        }
    }

    def action(self, world):
        command, target_idx = self.get_command(world)
        if command == "short_sword":
            world.attack(world.unit_list.index(self), target_idx, command)