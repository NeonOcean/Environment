from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
import protocolbuffers.S4Common_pb2 as S4Common_pb2
import protocolbuffers.ResourceKey_pb2 as ResourceKey_pb2
import protocolbuffers.Situations_pb2 as Situations_pb2
import protocolbuffers.UI_pb2 as UI_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Loot.proto', package='EA.Sims4.Network', serialized_pb='\n\nLoot.proto\x12\x10EA.Sims4.Network\x1a\x0eS4Common.proto\x1a\x11ResourceKey.proto\x1a\x10Situations.proto\x1a\x08UI.proto"Ú\x01\n\x0eSituationEnded\x12-\n\ticon_info\x18\x01 \x02(\x0b2\x1a.EA.Sims4.Network.IconInfo\x12\x13\n\x0bfinal_score\x18\x03 \x01(\r\x12;\n\x0bfinal_level\x18\x04 \x01(\x0b2&.EA.Sims4.Network.SituationLevelUpdate\x12\x13\n\x07sim_ids\x18\x05 \x03(\x06B\x02\x10\x01\x122\n\x0baudio_sting\x18\x06 \x01(\x0b2\x1d.EA.Sims4.Network.ResourceKey')
_SITUATIONENDED = descriptor.Descriptor(name='SituationEnded', full_name='EA.Sims4.Network.SituationEnded', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='icon_info', full_name='EA.Sims4.Network.SituationEnded.icon_info', index=0, number=1, type=11, cpp_type=10, label=2, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='final_score', full_name='EA.Sims4.Network.SituationEnded.final_score', index=1, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='final_level', full_name='EA.Sims4.Network.SituationEnded.final_level', index=2, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='sim_ids', full_name='EA.Sims4.Network.SituationEnded.sim_ids', index=3, number=5, type=6, cpp_type=4, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')), descriptor.FieldDescriptor(name='audio_sting', full_name='EA.Sims4.Network.SituationEnded.audio_sting', index=4, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=96, serialized_end=314)
_SITUATIONENDED.fields_by_name['icon_info'].message_type = UI_pb2._ICONINFO
_SITUATIONENDED.fields_by_name['final_level'].message_type = Situations_pb2._SITUATIONLEVELUPDATE
_SITUATIONENDED.fields_by_name['audio_sting'].message_type = ResourceKey_pb2._RESOURCEKEY
DESCRIPTOR.message_types_by_name['SituationEnded'] = _SITUATIONENDED

class SituationEnded(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONENDED
