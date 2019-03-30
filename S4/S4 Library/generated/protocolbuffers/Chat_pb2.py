from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Chat.proto', package='EA.Sims4.Chat', serialized_pb='\n\nChat.proto\x12\rEA.Sims4.Chat"å\x01\n\x0fChatPersistancy\x128\n\x06groups\x18\x01 \x03(\x0b2(.EA.Sims4.Chat.ChatPersistancy.ChatGroup\x1a\x97\x01\n\tChatGroup\x12\x11\n\tgroupName\x18\x01 \x02(\t\x12E\n\x05users\x18\x02 \x03(\x0b26.EA.Sims4.Chat.ChatPersistancy.ChatGroup.ChatGroupUser\x1a0\n\rChatGroupUser\x12\x11\n\tnucleusId\x18\x01 \x02(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t')
_CHATPERSISTANCY_CHATGROUP_CHATGROUPUSER = descriptor.Descriptor(name='ChatGroupUser', full_name='EA.Sims4.Chat.ChatPersistancy.ChatGroup.ChatGroupUser', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='nucleusId', full_name='EA.Sims4.Chat.ChatPersistancy.ChatGroup.ChatGroupUser.nucleusId', index=0, number=1, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='name', full_name='EA.Sims4.Chat.ChatPersistancy.ChatGroup.ChatGroupUser.name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=b''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=211, serialized_end=259)
_CHATPERSISTANCY_CHATGROUP = descriptor.Descriptor(name='ChatGroup', full_name='EA.Sims4.Chat.ChatPersistancy.ChatGroup', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='groupName', full_name='EA.Sims4.Chat.ChatPersistancy.ChatGroup.groupName', index=0, number=1, type=9, cpp_type=9, label=2, has_default_value=False, default_value=b''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='users', full_name='EA.Sims4.Chat.ChatPersistancy.ChatGroup.users', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[_CHATPERSISTANCY_CHATGROUP_CHATGROUPUSER], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=108, serialized_end=259)
_CHATPERSISTANCY = descriptor.Descriptor(name='ChatPersistancy', full_name='EA.Sims4.Chat.ChatPersistancy', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='groups', full_name='EA.Sims4.Chat.ChatPersistancy.groups', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[_CHATPERSISTANCY_CHATGROUP], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=30, serialized_end=259)
_CHATPERSISTANCY_CHATGROUP_CHATGROUPUSER.containing_type = _CHATPERSISTANCY_CHATGROUP
_CHATPERSISTANCY_CHATGROUP.fields_by_name['users'].message_type = _CHATPERSISTANCY_CHATGROUP_CHATGROUPUSER
_CHATPERSISTANCY_CHATGROUP.containing_type = _CHATPERSISTANCY
_CHATPERSISTANCY.fields_by_name['groups'].message_type = _CHATPERSISTANCY_CHATGROUP
DESCRIPTOR.message_types_by_name['ChatPersistancy'] = _CHATPERSISTANCY

class ChatPersistancy(message.Message, metaclass=reflection.GeneratedProtocolMessageType):

    class ChatGroup(message.Message, metaclass=reflection.GeneratedProtocolMessageType):

        class ChatGroupUser(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
            DESCRIPTOR = _CHATPERSISTANCY_CHATGROUP_CHATGROUPUSER

        DESCRIPTOR = _CHATPERSISTANCY_CHATGROUP

    DESCRIPTOR = _CHATPERSISTANCY
