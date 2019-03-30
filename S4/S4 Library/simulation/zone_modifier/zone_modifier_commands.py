from server_commands.argument_helpers import TunableInstanceParam
import services
import sims4.commands
ZONE_MODIFIER_CAP = 3

@sims4.commands.Command('zone_modifier.add_zone_modifier', command_type=sims4.commands.CommandType.DebugOnly)
def add_zone_modifier(zone_modifier:TunableInstanceParam(sims4.resources.Types.ZONE_MODIFIER), target_zone_id:int=None, _connection=None):
    if target_zone_id is None:
        target_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    if len(zone_data.lot_traits) == ZONE_MODIFIER_CAP:
        sims4.commands.output('There are already {} lot traits on the lot.  Remove one first.'.format(ZONE_MODIFIER_CAP), _connection)
        return
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id in zone_data.lot_traits:
        sims4.commands.output('{} is already a trait on the lot.'.format(zone_modifier), _connection)
        return
    zone_data.lot_traits.append(zone_modifier_id)
    services.get_zone_modifier_service().on_zone_modifiers_updated(target_zone_id)

@sims4.commands.Command('zone_modifier.remove_zone_modifier', command_type=sims4.commands.CommandType.DebugOnly)
def remove_zone_modifier(zone_modifier:TunableInstanceParam(sims4.resources.Types.ZONE_MODIFIER), target_zone_id:int=None, _connection=None):
    if target_zone_id is None:
        target_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id not in zone_data.lot_traits:
        sims4.commands.output('{} is not a trait on the lot.'.format(zone_modifier), _connection)
        return
    zone_data.lot_traits.remove(zone_modifier_id)
    services.get_zone_modifier_service().on_zone_modifiers_updated(target_zone_id)

@sims4.commands.Command('zone_modifier.remove_all_zone_modifiers', command_type=sims4.commands.CommandType.DebugOnly)
def remove_all_zone_modifiers(target_zone_id:int=None, _connection=None):
    if target_zone_id is None:
        target_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    traits_to_remove = list(zone_data.lot_traits)
    for trait in traits_to_remove:
        zone_data.lot_traits.remove(trait)
    services.get_zone_modifier_service().on_zone_modifiers_updated(target_zone_id)
