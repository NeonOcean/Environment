from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
import protocolbuffers.S4Common_pb2 as S4Common_pb2
import protocolbuffers.Localization_pb2 as Localization_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Area.proto', package='EA.Sims4.Network', serialized_pb='\n\nArea.proto\x12\x10EA.Sims4.Network\x1a\x0eS4Common.proto\x1a\x12Localization.proto"=\n\x1bZoneConnectedLotVersionData\x12\r\n\x05lotID\x18\x01 \x02(\r\x12\x0f\n\x07version\x18\x02 \x02(\x04"A\n\x18ConnectedNeighborhoodLot\x12\r\n\x05lotId\x18\x01 \x02(\r\x12\x16\n\x0ezoneInstanceId\x18\x02 \x02(\x04"ô\x01\n\x11ZoneConnectedData\x123\n\rinstance_info\x18\x01 \x02(\x0b2\x1c.EA.Sims4.GameInstanceInfoPB\x12\x1e\n\x16active_lot_template_id\x18\x02 \x02(\r\x12C\n\x0clot_versions\x18\x03 \x03(\x0b2-.EA.Sims4.Network.ZoneConnectedLotVersionData\x12E\n\x11neighborhood_lots\x18\x04 \x03(\x0b2*.EA.Sims4.Network.ConnectedNeighborhoodLot"P\n\x08GSI_Open\x12\n\n\x02ip\x18\x01 \x02(\t\x12\x0c\n\x04port\x18\x02 \x02(\r\x12\x0f\n\x07zone_id\x18\x03 \x01(\x04\x12\x19\n\x11additional_params\x18\x04 \x01(\t"\x9f\x01\n\x18AchievementTrackerUpdate\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12"\n\x16achievements_completed\x18\x02 \x03(\x04B\x02\x10\x01\x12 \n\x14objectives_completed\x18\x03 \x03(\x04B\x02\x10\x01\x12\x14\n\x0cinit_message\x18\x04 \x01(\x08\x12\x13\n\x0bcheats_used\x18\x05 \x01(\x08"\x9e\x01\n\x15AcctGoalsStatusUpdate\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x19\n\rgoals_updated\x18\x02 \x03(\x04B\x02\x10\x01\x12\x17\n\x0bgoal_values\x18\x03 \x03(\x03B\x02\x10\x01\x12\x1b\n\x0fgoal_objectives\x18\x04 \x03(\x03B\x02\x10\x01\x12 \n\x14goals_that_are_money\x18\x05 \x03(\x08B\x02\x10\x01"²\x01\n\x0fGameTimeCommand\x12\x13\n\x0bclock_speed\x18\x01 \x02(\r\x12\x12\n\ngame_speed\x18\x02 \x02(\x02\x12\x13\n\x0bserver_time\x18\x03 \x02(\x04\x12\x16\n\x0esync_game_time\x18\x04 \x02(\x04\x12\x16\n\x0emonotonic_time\x18\x05 \x02(\x04\x12\x1a\n\x0bsuper_speed\x18\x06 \x01(\x08:\x05false\x12\x15\n\rserial_number\x18\x07 \x01(\x04"À\x01\n\x12SocialNotification\x126\n\x04type\x18\x01 \x02(\x0e2(.EA.Sims4.Network.SocialNotificationType\x12;\n\x10localized_string\x18\x02 \x02(\x0b2!.EA.Sims4.Network.LocalizedString\x12\x12\n\naccount_id\x18\x03 \x01(\x04\x12\x0e\n\x06sim_id\x18\x04 \x01(\x04\x12\x11\n\tevent_uid\x18\x06 \x01(\r*ª\x01\n\x16SocialNotificationType\x12\x08\n\x04CHAT\x10\x00\x12\r\n\tBUDDYLIST\x10\x01\x12\x14\n\x10BUDDYLIST_INVITE\x10\x02\x12\x08\n\x04WALL\x10\x03\x12\x0c\n\x08GAMEPLAY\x10\x04\x12\x07\n\x03MTX\x10\x05\x12\r\n\tIMMEDIATE\x10\x06\x12\x17\n\x13GAMEPLAY_ASPIRATION\x10\x07\x12\n\n\x06SYSTEM\x10\x08\x12\x0c\n\x08EXCHANGE\x10\t')
_SOCIALNOTIFICATIONTYPE = descriptor.EnumDescriptor(name='SocialNotificationType', full_name='EA.Sims4.Network.SocialNotificationType', filename=None, file=DESCRIPTOR, values=[descriptor.EnumValueDescriptor(name='CHAT', index=0, number=0, options=None, type=None), descriptor.EnumValueDescriptor(name='BUDDYLIST', index=1, number=1, options=None, type=None), descriptor.EnumValueDescriptor(name='BUDDYLIST_INVITE', index=2, number=2, options=None, type=None), descriptor.EnumValueDescriptor(name='WALL', index=3, number=3, options=None, type=None), descriptor.EnumValueDescriptor(name='GAMEPLAY', index=4, number=4, options=None, type=None), descriptor.EnumValueDescriptor(name='MTX', index=5, number=5, options=None, type=None), descriptor.EnumValueDescriptor(name='IMMEDIATE', index=6, number=6, options=None, type=None), descriptor.EnumValueDescriptor(name='GAMEPLAY_ASPIRATION', index=7, number=7, options=None, type=None), descriptor.EnumValueDescriptor(name='SYSTEM', index=8, number=8, options=None, type=None), descriptor.EnumValueDescriptor(name='EXCHANGE', index=9, number=9, options=None, type=None)], containing_type=None, options=None, serialized_start=1227, serialized_end=1397)
CHAT = 0
BUDDYLIST = 1
BUDDYLIST_INVITE = 2
WALL = 3
GAMEPLAY = 4
MTX = 5
IMMEDIATE = 6
GAMEPLAY_ASPIRATION = 7
SYSTEM = 8
EXCHANGE = 9
_ZONECONNECTEDLOTVERSIONDATA = descriptor.Descriptor(name='ZoneConnectedLotVersionData', full_name='EA.Sims4.Network.ZoneConnectedLotVersionData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='lotID', full_name='EA.Sims4.Network.ZoneConnectedLotVersionData.lotID', index=0, number=1, type=13, cpp_type=3, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='version', full_name='EA.Sims4.Network.ZoneConnectedLotVersionData.version', index=1, number=2, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=68, serialized_end=129)
_CONNECTEDNEIGHBORHOODLOT = descriptor.Descriptor(name='ConnectedNeighborhoodLot', full_name='EA.Sims4.Network.ConnectedNeighborhoodLot', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='lotId', full_name='EA.Sims4.Network.ConnectedNeighborhoodLot.lotId', index=0, number=1, type=13, cpp_type=3, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='zoneInstanceId', full_name='EA.Sims4.Network.ConnectedNeighborhoodLot.zoneInstanceId', index=1, number=2, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=131, serialized_end=196)
_ZONECONNECTEDDATA = descriptor.Descriptor(name='ZoneConnectedData', full_name='EA.Sims4.Network.ZoneConnectedData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='instance_info', full_name='EA.Sims4.Network.ZoneConnectedData.instance_info', index=0, number=1, type=11, cpp_type=10, label=2, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='active_lot_template_id', full_name='EA.Sims4.Network.ZoneConnectedData.active_lot_template_id', index=1, number=2, type=13, cpp_type=3, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='lot_versions', full_name='EA.Sims4.Network.ZoneConnectedData.lot_versions', index=2, number=3, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='neighborhood_lots', full_name='EA.Sims4.Network.ZoneConnectedData.neighborhood_lots', index=3, number=4, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=199, serialized_end=443)
_GSI_OPEN = descriptor.Descriptor(name='GSI_Open', full_name='EA.Sims4.Network.GSI_Open', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='ip', full_name='EA.Sims4.Network.GSI_Open.ip', index=0, number=1, type=9, cpp_type=9, label=2, has_default_value=False, default_value=b''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='port', full_name='EA.Sims4.Network.GSI_Open.port', index=1, number=2, type=13, cpp_type=3, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='zone_id', full_name='EA.Sims4.Network.GSI_Open.zone_id', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='additional_params', full_name='EA.Sims4.Network.GSI_Open.additional_params', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=b''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=445, serialized_end=525)
_ACHIEVEMENTTRACKERUPDATE = descriptor.Descriptor(name='AchievementTrackerUpdate', full_name='EA.Sims4.Network.AchievementTrackerUpdate', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='account_id', full_name='EA.Sims4.Network.AchievementTrackerUpdate.account_id', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='achievements_completed', full_name='EA.Sims4.Network.AchievementTrackerUpdate.achievements_completed', index=1, number=2, type=4, cpp_type=4, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')), descriptor.FieldDescriptor(name='objectives_completed', full_name='EA.Sims4.Network.AchievementTrackerUpdate.objectives_completed', index=2, number=3, type=4, cpp_type=4, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')), descriptor.FieldDescriptor(name='init_message', full_name='EA.Sims4.Network.AchievementTrackerUpdate.init_message', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='cheats_used', full_name='EA.Sims4.Network.AchievementTrackerUpdate.cheats_used', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=528, serialized_end=687)
_ACCTGOALSSTATUSUPDATE = descriptor.Descriptor(name='AcctGoalsStatusUpdate', full_name='EA.Sims4.Network.AcctGoalsStatusUpdate', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='account_id', full_name='EA.Sims4.Network.AcctGoalsStatusUpdate.account_id', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='goals_updated', full_name='EA.Sims4.Network.AcctGoalsStatusUpdate.goals_updated', index=1, number=2, type=4, cpp_type=4, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')), descriptor.FieldDescriptor(name='goal_values', full_name='EA.Sims4.Network.AcctGoalsStatusUpdate.goal_values', index=2, number=3, type=3, cpp_type=2, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')), descriptor.FieldDescriptor(name='goal_objectives', full_name='EA.Sims4.Network.AcctGoalsStatusUpdate.goal_objectives', index=3, number=4, type=3, cpp_type=2, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')), descriptor.FieldDescriptor(name='goals_that_are_money', full_name='EA.Sims4.Network.AcctGoalsStatusUpdate.goals_that_are_money', index=4, number=5, type=8, cpp_type=7, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01'))], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=690, serialized_end=848)
_GAMETIMECOMMAND = descriptor.Descriptor(name='GameTimeCommand', full_name='EA.Sims4.Network.GameTimeCommand', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='clock_speed', full_name='EA.Sims4.Network.GameTimeCommand.clock_speed', index=0, number=1, type=13, cpp_type=3, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='game_speed', full_name='EA.Sims4.Network.GameTimeCommand.game_speed', index=1, number=2, type=2, cpp_type=6, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='server_time', full_name='EA.Sims4.Network.GameTimeCommand.server_time', index=2, number=3, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='sync_game_time', full_name='EA.Sims4.Network.GameTimeCommand.sync_game_time', index=3, number=4, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='monotonic_time', full_name='EA.Sims4.Network.GameTimeCommand.monotonic_time', index=4, number=5, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='super_speed', full_name='EA.Sims4.Network.GameTimeCommand.super_speed', index=5, number=6, type=8, cpp_type=7, label=1, has_default_value=True, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='serial_number', full_name='EA.Sims4.Network.GameTimeCommand.serial_number', index=6, number=7, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=851, serialized_end=1029)
_SOCIALNOTIFICATION = descriptor.Descriptor(name='SocialNotification', full_name='EA.Sims4.Network.SocialNotification', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='type', full_name='EA.Sims4.Network.SocialNotification.type', index=0, number=1, type=14, cpp_type=8, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='localized_string', full_name='EA.Sims4.Network.SocialNotification.localized_string', index=1, number=2, type=11, cpp_type=10, label=2, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='account_id', full_name='EA.Sims4.Network.SocialNotification.account_id', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='sim_id', full_name='EA.Sims4.Network.SocialNotification.sim_id', index=3, number=4, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='event_uid', full_name='EA.Sims4.Network.SocialNotification.event_uid', index=4, number=6, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1032, serialized_end=1224)
_ZONECONNECTEDDATA.fields_by_name['instance_info'].message_type = S4Common_pb2._GAMEINSTANCEINFOPB
_ZONECONNECTEDDATA.fields_by_name['lot_versions'].message_type = _ZONECONNECTEDLOTVERSIONDATA
_ZONECONNECTEDDATA.fields_by_name['neighborhood_lots'].message_type = _CONNECTEDNEIGHBORHOODLOT
_SOCIALNOTIFICATION.fields_by_name['type'].enum_type = _SOCIALNOTIFICATIONTYPE
_SOCIALNOTIFICATION.fields_by_name['localized_string'].message_type = Localization_pb2._LOCALIZEDSTRING
DESCRIPTOR.message_types_by_name['ZoneConnectedLotVersionData'] = _ZONECONNECTEDLOTVERSIONDATA
DESCRIPTOR.message_types_by_name['ConnectedNeighborhoodLot'] = _CONNECTEDNEIGHBORHOODLOT
DESCRIPTOR.message_types_by_name['ZoneConnectedData'] = _ZONECONNECTEDDATA
DESCRIPTOR.message_types_by_name['GSI_Open'] = _GSI_OPEN
DESCRIPTOR.message_types_by_name['AchievementTrackerUpdate'] = _ACHIEVEMENTTRACKERUPDATE
DESCRIPTOR.message_types_by_name['AcctGoalsStatusUpdate'] = _ACCTGOALSSTATUSUPDATE
DESCRIPTOR.message_types_by_name['GameTimeCommand'] = _GAMETIMECOMMAND
DESCRIPTOR.message_types_by_name['SocialNotification'] = _SOCIALNOTIFICATION

class ZoneConnectedLotVersionData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _ZONECONNECTEDLOTVERSIONDATA

class ConnectedNeighborhoodLot(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CONNECTEDNEIGHBORHOODLOT

class ZoneConnectedData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _ZONECONNECTEDDATA

class GSI_Open(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _GSI_OPEN

class AchievementTrackerUpdate(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _ACHIEVEMENTTRACKERUPDATE

class AcctGoalsStatusUpdate(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _ACCTGOALSSTATUSUPDATE

class GameTimeCommand(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _GAMETIMECOMMAND

class SocialNotification(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SOCIALNOTIFICATION
