from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
import protocolbuffers.SimObjectAttributes_pb2 as SimObjectAttributes_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Venue.proto', package='EA.Sims4.Network', serialized_pb='\n\x0bVenue.proto\x12\x10EA.Sims4.Network\x1a\x19SimObjectAttributes.proto"b\n\x0cCareerOutfit\x12\x17\n\x0coutfit_index\x18\x01 \x02(\r:\x010\x129\n\tmannequin\x18\x02 \x01(\x0b2&.EA.Sims4.Persistence.MannequinSimData"\x88\x01\n\x16VetClinicConfiguration\x12/\n\x07outfits\x18\x01 \x03(\x0b2\x1e.EA.Sims4.Network.CareerOutfit"=\n\x13VetClinicOutfitType\x12\x11\n\rMALE_EMPLOYEE\x10\x00\x12\x13\n\x0fFEMALE_EMPLOYEE\x10\x01')
_VETCLINICCONFIGURATION_VETCLINICOUTFITTYPE = descriptor.EnumDescriptor(name='VetClinicOutfitType', full_name='EA.Sims4.Network.VetClinicConfiguration.VetClinicOutfitType', filename=None, file=DESCRIPTOR, values=[descriptor.EnumValueDescriptor(name='MALE_EMPLOYEE', index=0, number=0, options=None, type=None), descriptor.EnumValueDescriptor(name='FEMALE_EMPLOYEE', index=1, number=1, options=None, type=None)], containing_type=None, options=None, serialized_start=236, serialized_end=297)
_CAREEROUTFIT = descriptor.Descriptor(name='CareerOutfit', full_name='EA.Sims4.Network.CareerOutfit', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='outfit_index', full_name='EA.Sims4.Network.CareerOutfit.outfit_index', index=0, number=1, type=13, cpp_type=3, label=2, has_default_value=True, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='mannequin', full_name='EA.Sims4.Network.CareerOutfit.mannequin', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=60, serialized_end=158)
_VETCLINICCONFIGURATION = descriptor.Descriptor(name='VetClinicConfiguration', full_name='EA.Sims4.Network.VetClinicConfiguration', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='outfits', full_name='EA.Sims4.Network.VetClinicConfiguration.outfits', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[_VETCLINICCONFIGURATION_VETCLINICOUTFITTYPE], options=None, is_extendable=False, extension_ranges=[], serialized_start=161, serialized_end=297)
_CAREEROUTFIT.fields_by_name['mannequin'].message_type = SimObjectAttributes_pb2._MANNEQUINSIMDATA
_VETCLINICCONFIGURATION.fields_by_name['outfits'].message_type = _CAREEROUTFIT
_VETCLINICCONFIGURATION_VETCLINICOUTFITTYPE.containing_type = _VETCLINICCONFIGURATION
DESCRIPTOR.message_types_by_name['CareerOutfit'] = _CAREEROUTFIT
DESCRIPTOR.message_types_by_name['VetClinicConfiguration'] = _VETCLINICCONFIGURATION

class CareerOutfit(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CAREEROUTFIT

class VetClinicConfiguration(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _VETCLINICCONFIGURATION
