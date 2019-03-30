from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
import protocolbuffers.ResourceKey_pb2 as ResourceKey_pb2
import protocolbuffers.Localization_pb2 as Localization_pb2
import protocolbuffers.Lot_pb2 as Lot_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Clubs.proto', package='EA.Sims4.Network', serialized_pb='\n\x0bClubs.proto\x12\x10EA.Sims4.Network\x1a\x11ResourceKey.proto\x1a\x12Localization.proto\x1a\tLot.proto"Ë\x02\n\x0cClubCriteria\x12E\n\x08category\x18\x01 \x02(\x0e23.EA.Sims4.Network.ClubCriteria.ClubCriteriaCategory\x12:\n\x0ecriteria_infos\x18\x02 \x03(\x0b2".EA.Sims4.Network.ClubCriteriaInfo\x12\x14\n\x0cmulti_select\x18\x03 \x01(\x08\x12\x13\n\x0bcriteria_id\x18\x04 \x01(\r"\x8c\x01\n\x14ClubCriteriaCategory\x12\t\n\x05SKILL\x10\x00\x12\t\n\x05TRAIT\x10\x01\x12\x10\n\x0cRELATIONSHIP\x10\x02\x12\n\n\x06CAREER\x10\x03\x12\x13\n\x0fHOUSEHOLD_VALUE\x10\x04\x12\x07\n\x03AGE\x10\x05\x12\x13\n\x0fCLUB_MEMBERSHIP\x10\x06\x12\r\n\tFAME_RANK\x10\x07"\x89\x02\n\x10ClubCriteriaInfo\x12/\n\x04name\x18\x01 \x01(\x0b2!.EA.Sims4.Network.LocalizedString\x12+\n\x04icon\x18\x02 \x01(\x0b2\x1d.EA.Sims4.Network.ResourceKey\x125\n\x0eresource_value\x18\x03 \x01(\x0b2\x1d.EA.Sims4.Network.ResourceKey\x12\x12\n\nenum_value\x18\x04 \x01(\r\x12\x13\n\x0bresource_id\x18\x05 \x01(\x04\x127\n\x0ctooltip_name\x18\x06 \x01(\x0b2!.EA.Sims4.Network.LocalizedString"\x92\x01\n\x0fClubConductRule\x12\x12\n\nencouraged\x18\x01 \x02(\x08\x128\n\x11interaction_group\x18\x02 \x02(\x0b2\x1d.EA.Sims4.Network.ResourceKey\x121\n\twith_whom\x18\x03 \x01(\x0b2\x1e.EA.Sims4.Network.ClubCriteria"|\n\x10ClubBuildingInfo\x121\n\tcriterias\x18\x01 \x03(\x0b2\x1e.EA.Sims4.Network.ClubCriteria\x125\n\x0eavailable_lots\x18\x02 \x03(\x0b2\x1d.EA.Sims4.Network.LotInfoItem"Ä\x01\n\x19ClubInteractionRuleUpdate\x12Z\n\x0brule_status\x18\x01 \x02(\x0e2E.EA.Sims4.Network.ClubInteractionRuleUpdate.ClubInteractionRuleStatus"K\n\x19ClubInteractionRuleStatus\x12\x0e\n\nENCOURAGED\x10\x00\x12\x0f\n\x0bDISCOURAGED\x10\x01\x12\r\n\tNO_EFFECT\x10\x02"!\n\x0eShowClubInfoUI\x12\x0f\n\x07club_id\x18\x01 \x01(\x04')
_CLUBCRITERIA_CLUBCRITERIACATEGORY = descriptor.EnumDescriptor(name='ClubCriteriaCategory', full_name='EA.Sims4.Network.ClubCriteria.ClubCriteriaCategory', filename=None, file=DESCRIPTOR, values=[descriptor.EnumValueDescriptor(name='SKILL', index=0, number=0, options=None, type=None), descriptor.EnumValueDescriptor(name='TRAIT', index=1, number=1, options=None, type=None), descriptor.EnumValueDescriptor(name='RELATIONSHIP', index=2, number=2, options=None, type=None), descriptor.EnumValueDescriptor(name='CAREER', index=3, number=3, options=None, type=None), descriptor.EnumValueDescriptor(name='HOUSEHOLD_VALUE', index=4, number=4, options=None, type=None), descriptor.EnumValueDescriptor(name='AGE', index=5, number=5, options=None, type=None), descriptor.EnumValueDescriptor(name='CLUB_MEMBERSHIP', index=6, number=6, options=None, type=None), descriptor.EnumValueDescriptor(name='FAME_RANK', index=7, number=7, options=None, type=None)], containing_type=None, options=None, serialized_start=275, serialized_end=415)
_CLUBINTERACTIONRULEUPDATE_CLUBINTERACTIONRULESTATUS = descriptor.EnumDescriptor(name='ClubInteractionRuleStatus', full_name='EA.Sims4.Network.ClubInteractionRuleUpdate.ClubInteractionRuleStatus', filename=None, file=DESCRIPTOR, values=[descriptor.EnumValueDescriptor(name='ENCOURAGED', index=0, number=0, options=None, type=None), descriptor.EnumValueDescriptor(name='DISCOURAGED', index=1, number=1, options=None, type=None), descriptor.EnumValueDescriptor(name='NO_EFFECT', index=2, number=2, options=None, type=None)], containing_type=None, options=None, serialized_start=1082, serialized_end=1157)
_CLUBCRITERIA = descriptor.Descriptor(name='ClubCriteria', full_name='EA.Sims4.Network.ClubCriteria', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='category', full_name='EA.Sims4.Network.ClubCriteria.category', index=0, number=1, type=14, cpp_type=8, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='criteria_infos', full_name='EA.Sims4.Network.ClubCriteria.criteria_infos', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='multi_select', full_name='EA.Sims4.Network.ClubCriteria.multi_select', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='criteria_id', full_name='EA.Sims4.Network.ClubCriteria.criteria_id', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[_CLUBCRITERIA_CLUBCRITERIACATEGORY], options=None, is_extendable=False, extension_ranges=[], serialized_start=84, serialized_end=415)
_CLUBCRITERIAINFO = descriptor.Descriptor(name='ClubCriteriaInfo', full_name='EA.Sims4.Network.ClubCriteriaInfo', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='name', full_name='EA.Sims4.Network.ClubCriteriaInfo.name', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='icon', full_name='EA.Sims4.Network.ClubCriteriaInfo.icon', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='resource_value', full_name='EA.Sims4.Network.ClubCriteriaInfo.resource_value', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='enum_value', full_name='EA.Sims4.Network.ClubCriteriaInfo.enum_value', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='resource_id', full_name='EA.Sims4.Network.ClubCriteriaInfo.resource_id', index=4, number=5, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='tooltip_name', full_name='EA.Sims4.Network.ClubCriteriaInfo.tooltip_name', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=418, serialized_end=683)
_CLUBCONDUCTRULE = descriptor.Descriptor(name='ClubConductRule', full_name='EA.Sims4.Network.ClubConductRule', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='encouraged', full_name='EA.Sims4.Network.ClubConductRule.encouraged', index=0, number=1, type=8, cpp_type=7, label=2, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='interaction_group', full_name='EA.Sims4.Network.ClubConductRule.interaction_group', index=1, number=2, type=11, cpp_type=10, label=2, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='with_whom', full_name='EA.Sims4.Network.ClubConductRule.with_whom', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=686, serialized_end=832)
_CLUBBUILDINGINFO = descriptor.Descriptor(name='ClubBuildingInfo', full_name='EA.Sims4.Network.ClubBuildingInfo', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='criterias', full_name='EA.Sims4.Network.ClubBuildingInfo.criterias', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='available_lots', full_name='EA.Sims4.Network.ClubBuildingInfo.available_lots', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=834, serialized_end=958)
_CLUBINTERACTIONRULEUPDATE = descriptor.Descriptor(name='ClubInteractionRuleUpdate', full_name='EA.Sims4.Network.ClubInteractionRuleUpdate', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='rule_status', full_name='EA.Sims4.Network.ClubInteractionRuleUpdate.rule_status', index=0, number=1, type=14, cpp_type=8, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[_CLUBINTERACTIONRULEUPDATE_CLUBINTERACTIONRULESTATUS], options=None, is_extendable=False, extension_ranges=[], serialized_start=961, serialized_end=1157)
_SHOWCLUBINFOUI = descriptor.Descriptor(name='ShowClubInfoUI', full_name='EA.Sims4.Network.ShowClubInfoUI', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='club_id', full_name='EA.Sims4.Network.ShowClubInfoUI.club_id', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1159, serialized_end=1192)
_CLUBCRITERIA.fields_by_name['category'].enum_type = _CLUBCRITERIA_CLUBCRITERIACATEGORY
_CLUBCRITERIA.fields_by_name['criteria_infos'].message_type = _CLUBCRITERIAINFO
_CLUBCRITERIA_CLUBCRITERIACATEGORY.containing_type = _CLUBCRITERIA
_CLUBCRITERIAINFO.fields_by_name['name'].message_type = Localization_pb2._LOCALIZEDSTRING
_CLUBCRITERIAINFO.fields_by_name['icon'].message_type = ResourceKey_pb2._RESOURCEKEY
_CLUBCRITERIAINFO.fields_by_name['resource_value'].message_type = ResourceKey_pb2._RESOURCEKEY
_CLUBCRITERIAINFO.fields_by_name['tooltip_name'].message_type = Localization_pb2._LOCALIZEDSTRING
_CLUBCONDUCTRULE.fields_by_name['interaction_group'].message_type = ResourceKey_pb2._RESOURCEKEY
_CLUBCONDUCTRULE.fields_by_name['with_whom'].message_type = _CLUBCRITERIA
_CLUBBUILDINGINFO.fields_by_name['criterias'].message_type = _CLUBCRITERIA
_CLUBBUILDINGINFO.fields_by_name['available_lots'].message_type = Lot_pb2._LOTINFOITEM
_CLUBINTERACTIONRULEUPDATE.fields_by_name['rule_status'].enum_type = _CLUBINTERACTIONRULEUPDATE_CLUBINTERACTIONRULESTATUS
_CLUBINTERACTIONRULEUPDATE_CLUBINTERACTIONRULESTATUS.containing_type = _CLUBINTERACTIONRULEUPDATE
DESCRIPTOR.message_types_by_name['ClubCriteria'] = _CLUBCRITERIA
DESCRIPTOR.message_types_by_name['ClubCriteriaInfo'] = _CLUBCRITERIAINFO
DESCRIPTOR.message_types_by_name['ClubConductRule'] = _CLUBCONDUCTRULE
DESCRIPTOR.message_types_by_name['ClubBuildingInfo'] = _CLUBBUILDINGINFO
DESCRIPTOR.message_types_by_name['ClubInteractionRuleUpdate'] = _CLUBINTERACTIONRULEUPDATE
DESCRIPTOR.message_types_by_name['ShowClubInfoUI'] = _SHOWCLUBINFOUI

class ClubCriteria(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CLUBCRITERIA

class ClubCriteriaInfo(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CLUBCRITERIAINFO

class ClubConductRule(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CLUBCONDUCTRULE

class ClubBuildingInfo(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CLUBBUILDINGINFO

class ClubInteractionRuleUpdate(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CLUBINTERACTIONRULEUPDATE

class ShowClubInfoUI(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SHOWCLUBINFOUI
