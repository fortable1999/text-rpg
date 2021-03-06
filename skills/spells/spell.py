from skills.skill import AbstractSkill
from utils import dice
from skills.spells import const as spells_const
from utils import (cast_spell_success_print,
                   cast_spell_failed_print)
from encounter import const as encounter_const


class Spell(AbstractSkill):
    """
    Abstract class for Spell
    """

    level = 0

    spell_type = None
    spell_target_type = None

    def effect(self, world, *args):
        raise NotImplementedError("Spell class need effect function")
        

class SingleTargetSpellMixin(object):
    """
    for spell has caster/target
    """

    def unit_is_alive(self, world, unit_uuid):
        unit = self.get_target(world, unit_uuid)
        return not unit.is_dead

    def get_target(self, world, unit_uuid):
        return world.get_unit_by_uuid(unit_uuid)
        
    def get_caster(self, world):
        return world.get_unit_by_idx(world.current_act_unit_id)


class SingleTargetHealSpellMixin(SingleTargetSpellMixin):
    """
    For spells like:
        cure_minor_wounds,
        cure_light_wounds,
        ...
    """

    heal_hp = 0
    heal_hp_dice = None

    spell_type = spells_const.HEAL_SPELL
    spell_target_type = spells_const.SINGLE_TARGET_SPELL

    def get_heal_hp(self, world, *args):
        """docstring for ge"""
        heal_hp = self.get_heal_hp_dice(world, *args)
        heal_hp += self.get_heal_hp_modifier(world, *args)
        return heal_hp

    def get_heal_hp_dice(self, world, *args):
        heal_hp = 0
        if hasattr(self, 'heal_hp') and self.heal_hp:
            heal_hp += self.heal_hp
        if hasattr(self, 'heal_hp_dice') and self.heal_hp_dice:
            heal_hp += dice(self.heal_hp_dice)
        return heal_hp

    def get_heal_hp_modifier(self, world, *args):
        return 0

    def effect(self, world, target_uuid, *args):
        """docstring for ef"""
        target_idx = world.get_unit_idx_by_uuid(target_uuid)
        target = self.get_target(world, target_uuid)
        caster = self.get_caster(world)
        if target.is_dead:
            cast_spell_failed_print(
                spell_name=self.name,
                target_name=target.name,
                message="(Target lost)")
            return False

        cure_hp = self.get_heal_hp(world, *args)

        if target.unit_hp + cure_hp > target.unit_hp_max:
            cure_hp = target.unit_hp_max - target.unit_hp

        world.unit_list[target_idx].unit_hp += cure_hp
        cast_spell_success_print(
            spell_name=self.name,
            target_name=target.name,
            message="cure \033[91m%s\033[0m by %d hp" % (target.name, cure_hp))
        return True


class SingleTargetDamageSpellMixin(SingleTargetSpellMixin):
    """
    For spells like:
        ray_of_frost,
        ...
    """

    damage = 0
    damage_dice = None

    spell_type = spells_const.DAMAGE_SPELL
    spell_target_type = spells_const.SINGLE_TARGET_SPELL

    def get_total_damage(self, world, *args):
        """docstring for ge"""
        total_damage = self.get_damage_dice(world, *args)
        total_damage += self.get_damage_modifier(world, *args)
        return total_damage

    def get_damage_dice(self, world, is_critical, *args):
        damage = 0
        if hasattr(self, 'damage') and self.damage:
            damage += self.damage
            if is_critical:
                damage += self.damage
        if hasattr(self, 'damage_dice') and self.damage_dice:
            damage += dice(self.damage_dice)
            if is_critical:
                damage += dice(self.damage_dice)
        return damage

    def get_damage_modifier(self, world, *args):
        return 0

    def effect(self, world, target_uuid, *args):
        target_idx = world.get_unit_idx_by_uuid(target_uuid)
        target = self.get_target(world, target_uuid)
        caster_idx = world.current_act_unit_id
        caster = self.get_caster(world)
        if target.is_dead:
            cast_spell_failed_print(
                spell_name=self.name,
                target_name=target.name,
                message="(Target lost)")
            return False


        attack_roll = world.touch_attack_roll(caster_idx,
                                              target_idx,
                                              "dex")
        if attack_roll == encounter_const.ATTACK_ROLL_HIT:
            damage = self.get_total_damage(world, False, *args)
            world.unit_list[target_idx].unit_hp -= damage
            cast_spell_success_print(
                spell_name=self.name,
                target_name=target.name,
                message=("damage \033[91m%s\033[0m by %d points hp (HP: %d)"
                    % (target.name, damage, world.unit_list[target_idx].unit_hp)))
        elif attack_roll == encounter_const.ATTACK_ROLL_CRITICAL:
            damage = self.get_total_damage(world, True, *args)
            world.unit_list[target_idx].unit_hp -= damage
            cast_spell_success_print(
                spell_name=self.name,
                target_name=target.name,
                message=("(Critical) damage \033[91m%s\033[0m by %d points hp (HP: %d)"
                    % (target.name, damage, world.unit_list[target_idx].unit_hp)))
        else:
            cast_spell_failed_print(
                spell_name=self.name,
                target_name=target.name,
                message="Failed to hit.")
