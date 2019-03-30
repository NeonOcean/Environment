from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='BillingClient.proto', package='EA.Sims4.Network', serialized_pb='\n\x13BillingClient.proto\x12\x10EA.Sims4.Network")\n\x14BillingClientRequest\x12\x11\n\titem_guid\x18\x01 \x03(\t"[\n\x15BillingClientResponse\x12B\n\rresponse_code\x18\x01 \x01(\x0e2+.EA.Sims4.Network.BillingClientResponseType*=\n\x19BillingClientResponseType\x12\x0f\n\x0bBCR_SUCCESS\x10\x00\x12\x0f\n\x0bBCR_FAILURE\x10\x01')
_BILLINGCLIENTRESPONSETYPE = descriptor.EnumDescriptor(name='BillingClientResponseType', full_name='EA.Sims4.Network.BillingClientResponseType', filename=None, file=DESCRIPTOR, values=[descriptor.EnumValueDescriptor(name='BCR_SUCCESS', index=0, number=0, options=None, type=None), descriptor.EnumValueDescriptor(name='BCR_FAILURE', index=1, number=1, options=None, type=None)], containing_type=None, options=None, serialized_start=177, serialized_end=238)
BCR_SUCCESS = 0
BCR_FAILURE = 1
_BILLINGCLIENTREQUEST = descriptor.Descriptor(name='BillingClientRequest', full_name='EA.Sims4.Network.BillingClientRequest', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='item_guid', full_name='EA.Sims4.Network.BillingClientRequest.item_guid', index=0, number=1, type=9, cpp_type=9, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=41, serialized_end=82)
_BILLINGCLIENTRESPONSE = descriptor.Descriptor(name='BillingClientResponse', full_name='EA.Sims4.Network.BillingClientResponse', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='response_code', full_name='EA.Sims4.Network.BillingClientResponse.response_code', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=84, serialized_end=175)
_BILLINGCLIENTRESPONSE.fields_by_name['response_code'].enum_type = _BILLINGCLIENTRESPONSETYPE
DESCRIPTOR.message_types_by_name['BillingClientRequest'] = _BILLINGCLIENTREQUEST
DESCRIPTOR.message_types_by_name['BillingClientResponse'] = _BILLINGCLIENTRESPONSE

class BillingClientRequest(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _BILLINGCLIENTREQUEST

class BillingClientResponse(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _BILLINGCLIENTRESPONSE
