from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='SituationPersistence.proto', package='EA.Sims4.Persistence', serialized_pb='\n\x1aSituationPersistence.proto\x12\x14EA.Sims4.Persistence"Ü\x01\n\x11SituationGoalData\x12\x14\n\x0cgoal_type_id\x18\x01 \x02(\x06\x12\x10\n\x08actor_id\x18\x02 \x01(\x06\x12\r\n\x05count\x18\x03 \x01(\r\x12\x11\n\tcompleted\x18\x04 \x01(\x08\x12\x10\n\x08chain_id\x18\x05 \x01(\x06\x12\x13\n\x0bcustom_data\x18\x06 \x01(\x0c\x12\x0e\n\x06locked\x18\x07 \x01(\x08\x12\x16\n\x0ecompleted_time\x18\x08 \x01(\x04\x12\x11\n\ttarget_id\x18\t \x01(\x06\x12\x1b\n\x13secondary_target_id\x18\n \x01(\x06"~\n\x1aCompletedSituationGoalData\x12?\n\x0esituation_goal\x18\x01 \x01(\x0b2\'.EA.Sims4.Persistence.SituationGoalData\x12\x1f\n\x17chosen_goal_set_type_id\x18\x02 \x01(\x06"\x8c\x01\n\x16SituationGoalChainData\x12!\n\x19starting_goal_set_type_id\x18\x01 \x01(\x06\x12\x1f\n\x17chosen_goal_set_type_id\x18\x02 \x01(\x06\x12\x10\n\x08chain_id\x18\x03 \x01(\x06\x12\x1c\n\x10display_position\x18\x04 \x01(\x05:\x02-1"\x8f\x04\n\x18SituationGoalTrackerData\x12\x19\n\x11has_offered_goals\x18\x01 \x01(\x08\x12\x1b\n\x13inherited_target_id\x18\x02 \x01(\x06\x12<\n\x06chains\x18\x03 \x03(\x0b2,.EA.Sims4.Persistence.SituationGoalChainData\x12<\n\x0bminor_goals\x18\x04 \x03(\x0b2\'.EA.Sims4.Persistence.SituationGoalData\x12:\n\tmain_goal\x18\x05 \x01(\x0b2\'.EA.Sims4.Persistence.SituationGoalData\x12I\n\x0fcompleted_goals\x18\x06 \x03(\x0b20.EA.Sims4.Persistence.CompletedSituationGoalData\x12p\n\x11goal_tracker_type\x18\x07 \x01(\x0e2>.EA.Sims4.Persistence.SituationGoalTrackerData.GoalTrackerType:\x15STANDARD_GOAL_TRACKER"F\n\x0fGoalTrackerType\x12\x19\n\x15STANDARD_GOAL_TRACKER\x10\x00\x12\x18\n\x14DYNAMIC_GOAL_TRACKER\x10\x01"¼\x02\n\x17SituationAssignmentData\x12\x0e\n\x06sim_id\x18\x01 \x02(\x06\x12\x13\n\x0bjob_type_id\x18\x02 \x02(\x06\x12\x0f\n\x07purpose\x18\x03 \x01(\r\x12\x1a\n\x12role_state_type_id\x18\x04 \x01(\x06\x12\x17\n\x0fspawning_option\x18\x05 \x01(\r\x12\x18\n\x10request_priority\x18\x06 \x01(\r\x12\x1e\n\x16expectation_preference\x18\x07 \x01(\x08\x12\x1c\n\x14accept_alternate_sim\x18\x08 \x01(\x08\x12#\n\x1bcommon_blacklist_categories\x18\t \x01(\r\x12$\n\x1celevated_importance_override\x18\n \x01(\x08\x12\x13\n\x0breservation\x18\x0b \x01(\x08"P\n\x1bSituationSimpleSeedlingData\x12\x13\n\x0bphase_index\x18\x01 \x01(\r\x12\x1c\n\x14remaining_phase_time\x18\x02 \x01(\x02"X\n\x1cSituationComplexSeedlingData\x12\x1d\n\x15situation_custom_data\x18\x01 \x01(\x0c\x12\x19\n\x11state_custom_data\x18\x02 \x01(\x0c"s\n\x18SituationJobAndRoleState\x12\x13\n\x0bjob_type_id\x18\x01 \x02(\x06\x12\x1a\n\x12role_state_type_id\x18\x02 \x02(\x06\x12&\n\x1eemotional_loot_actions_type_id\x18\x03 \x01(\x06"ö\x05\n\x11SituationSeedData\x12\x19\n\x11situation_type_id\x18\x01 \x02(\x06\x12\x14\n\x0csituation_id\x18\x02 \x02(\x06\x12\x14\n\x0cseed_purpose\x18\x03 \x01(\r\x12\x13\n\x0binvite_only\x18\x04 \x01(\x08\x12\x13\n\x0bhost_sim_id\x18\x05 \x01(\x06\x12B\n\x0bassignments\x18\x06 \x03(\x0b2-.EA.Sims4.Persistence.SituationAssignmentData\x12\x13\n\x0buser_facing\x18\x07 \x01(\x08\x12\x10\n\x08duration\x18\x08 \x01(\x02\x12\x0f\n\x07zone_id\x18\t \x01(\x06\x12L\n\x14jobs_and_role_states\x18\n \x03(\x0b2..EA.Sims4.Persistence.SituationJobAndRoleState\x12\x13\n\x0bcreate_time\x18\x0b \x01(\x04\x12\r\n\x05score\x18\x0c \x01(\x02\x12F\n\x0bsimple_data\x18\r \x01(\x0b21.EA.Sims4.Persistence.SituationSimpleSeedlingData\x12H\n\x0ccomplex_data\x18\x0e \x01(\x0b22.EA.Sims4.Persistence.SituationComplexSeedlingData\x12 \n\x18filter_requesting_sim_id\x18\x0f \x01(\x06\x12I\n\x11goal_tracker_data\x18\x10 \x01(\x0b2..EA.Sims4.Persistence.SituationGoalTrackerData\x12\x12\n\nstart_time\x18\x11 \x01(\x04\x12\x1b\n\x13active_household_id\x18\x12 \x01(\x06\x12\x17\n\x0fscoring_enabled\x18\x13 \x01(\x08\x12"\n\x14main_goal_visibility\x18\x14 \x01(\x08:\x04true\x12\x15\n\rlinked_sim_id\x18\x15 \x01(\x06"6\n\x19SituationBlacklistTagData\x12\x0b\n\x03tag\x18\x01 \x02(\x04\x12\x0c\n\x04time\x18\x02 \x02(\x04"k\n\x16SituationBlacklistData\x12\x0e\n\x06sim_id\x18\x01 \x02(\x06\x12A\n\x08tag_data\x18\x02 \x03(\x0b2/.EA.Sims4.Persistence.SituationBlacklistTagData"Ì\x01\n\x10AllSituationData\x126\n\x05seeds\x18\x01 \x03(\x0b2\'.EA.Sims4.Persistence.SituationSeedData\x12\x1a\n\x12leave_situation_id\x18\x02 \x01(\x06\x12\x1e\n\x16leave_now_situation_id\x18\x03 \x01(\x06\x12D\n\x0eblacklist_data\x18\x04 \x03(\x0b2,.EA.Sims4.Persistence.SituationBlacklistData')
_SITUATIONGOALTRACKERDATA_GOALTRACKERTYPE = descriptor.EnumDescriptor(name='GoalTrackerType', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.GoalTrackerType', filename=None, file=DESCRIPTOR, values=[descriptor.EnumValueDescriptor(name='STANDARD_GOAL_TRACKER', index=0, number=0, options=None, type=None), descriptor.EnumValueDescriptor(name='DYNAMIC_GOAL_TRACKER', index=1, number=1, options=None, type=None)], containing_type=None, options=None, serialized_start=1004, serialized_end=1074)
_SITUATIONGOALDATA = descriptor.Descriptor(name='SituationGoalData', full_name='EA.Sims4.Persistence.SituationGoalData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='goal_type_id', full_name='EA.Sims4.Persistence.SituationGoalData.goal_type_id', index=0, number=1, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='actor_id', full_name='EA.Sims4.Persistence.SituationGoalData.actor_id', index=1, number=2, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='count', full_name='EA.Sims4.Persistence.SituationGoalData.count', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='completed', full_name='EA.Sims4.Persistence.SituationGoalData.completed', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='chain_id', full_name='EA.Sims4.Persistence.SituationGoalData.chain_id', index=4, number=5, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='custom_data', full_name='EA.Sims4.Persistence.SituationGoalData.custom_data', index=5, number=6, type=12, cpp_type=9, label=1, has_default_value=False, default_value=b'', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='locked', full_name='EA.Sims4.Persistence.SituationGoalData.locked', index=6, number=7, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='completed_time', full_name='EA.Sims4.Persistence.SituationGoalData.completed_time', index=7, number=8, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='target_id', full_name='EA.Sims4.Persistence.SituationGoalData.target_id', index=8, number=9, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='secondary_target_id', full_name='EA.Sims4.Persistence.SituationGoalData.secondary_target_id', index=9, number=10, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=53, serialized_end=273)
_COMPLETEDSITUATIONGOALDATA = descriptor.Descriptor(name='CompletedSituationGoalData', full_name='EA.Sims4.Persistence.CompletedSituationGoalData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='situation_goal', full_name='EA.Sims4.Persistence.CompletedSituationGoalData.situation_goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='chosen_goal_set_type_id', full_name='EA.Sims4.Persistence.CompletedSituationGoalData.chosen_goal_set_type_id', index=1, number=2, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=275, serialized_end=401)
_SITUATIONGOALCHAINDATA = descriptor.Descriptor(name='SituationGoalChainData', full_name='EA.Sims4.Persistence.SituationGoalChainData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='starting_goal_set_type_id', full_name='EA.Sims4.Persistence.SituationGoalChainData.starting_goal_set_type_id', index=0, number=1, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='chosen_goal_set_type_id', full_name='EA.Sims4.Persistence.SituationGoalChainData.chosen_goal_set_type_id', index=1, number=2, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='chain_id', full_name='EA.Sims4.Persistence.SituationGoalChainData.chain_id', index=2, number=3, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='display_position', full_name='EA.Sims4.Persistence.SituationGoalChainData.display_position', index=3, number=4, type=5, cpp_type=1, label=1, has_default_value=True, default_value=-1, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=404, serialized_end=544)
_SITUATIONGOALTRACKERDATA = descriptor.Descriptor(name='SituationGoalTrackerData', full_name='EA.Sims4.Persistence.SituationGoalTrackerData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='has_offered_goals', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.has_offered_goals', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='inherited_target_id', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.inherited_target_id', index=1, number=2, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='chains', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.chains', index=2, number=3, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='minor_goals', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.minor_goals', index=3, number=4, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='main_goal', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.main_goal', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='completed_goals', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.completed_goals', index=5, number=6, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='goal_tracker_type', full_name='EA.Sims4.Persistence.SituationGoalTrackerData.goal_tracker_type', index=6, number=7, type=14, cpp_type=8, label=1, has_default_value=True, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[_SITUATIONGOALTRACKERDATA_GOALTRACKERTYPE], options=None, is_extendable=False, extension_ranges=[], serialized_start=547, serialized_end=1074)
_SITUATIONASSIGNMENTDATA = descriptor.Descriptor(name='SituationAssignmentData', full_name='EA.Sims4.Persistence.SituationAssignmentData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='sim_id', full_name='EA.Sims4.Persistence.SituationAssignmentData.sim_id', index=0, number=1, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='job_type_id', full_name='EA.Sims4.Persistence.SituationAssignmentData.job_type_id', index=1, number=2, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='purpose', full_name='EA.Sims4.Persistence.SituationAssignmentData.purpose', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='role_state_type_id', full_name='EA.Sims4.Persistence.SituationAssignmentData.role_state_type_id', index=3, number=4, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='spawning_option', full_name='EA.Sims4.Persistence.SituationAssignmentData.spawning_option', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='request_priority', full_name='EA.Sims4.Persistence.SituationAssignmentData.request_priority', index=5, number=6, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='expectation_preference', full_name='EA.Sims4.Persistence.SituationAssignmentData.expectation_preference', index=6, number=7, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='accept_alternate_sim', full_name='EA.Sims4.Persistence.SituationAssignmentData.accept_alternate_sim', index=7, number=8, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='common_blacklist_categories', full_name='EA.Sims4.Persistence.SituationAssignmentData.common_blacklist_categories', index=8, number=9, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='elevated_importance_override', full_name='EA.Sims4.Persistence.SituationAssignmentData.elevated_importance_override', index=9, number=10, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='reservation', full_name='EA.Sims4.Persistence.SituationAssignmentData.reservation', index=10, number=11, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1077, serialized_end=1393)
_SITUATIONSIMPLESEEDLINGDATA = descriptor.Descriptor(name='SituationSimpleSeedlingData', full_name='EA.Sims4.Persistence.SituationSimpleSeedlingData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='phase_index', full_name='EA.Sims4.Persistence.SituationSimpleSeedlingData.phase_index', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='remaining_phase_time', full_name='EA.Sims4.Persistence.SituationSimpleSeedlingData.remaining_phase_time', index=1, number=2, type=2, cpp_type=6, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1395, serialized_end=1475)
_SITUATIONCOMPLEXSEEDLINGDATA = descriptor.Descriptor(name='SituationComplexSeedlingData', full_name='EA.Sims4.Persistence.SituationComplexSeedlingData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='situation_custom_data', full_name='EA.Sims4.Persistence.SituationComplexSeedlingData.situation_custom_data', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value=b'', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='state_custom_data', full_name='EA.Sims4.Persistence.SituationComplexSeedlingData.state_custom_data', index=1, number=2, type=12, cpp_type=9, label=1, has_default_value=False, default_value=b'', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1477, serialized_end=1565)
_SITUATIONJOBANDROLESTATE = descriptor.Descriptor(name='SituationJobAndRoleState', full_name='EA.Sims4.Persistence.SituationJobAndRoleState', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='job_type_id', full_name='EA.Sims4.Persistence.SituationJobAndRoleState.job_type_id', index=0, number=1, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='role_state_type_id', full_name='EA.Sims4.Persistence.SituationJobAndRoleState.role_state_type_id', index=1, number=2, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='emotional_loot_actions_type_id', full_name='EA.Sims4.Persistence.SituationJobAndRoleState.emotional_loot_actions_type_id', index=2, number=3, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1567, serialized_end=1682)
_SITUATIONSEEDDATA = descriptor.Descriptor(name='SituationSeedData', full_name='EA.Sims4.Persistence.SituationSeedData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='situation_type_id', full_name='EA.Sims4.Persistence.SituationSeedData.situation_type_id', index=0, number=1, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='situation_id', full_name='EA.Sims4.Persistence.SituationSeedData.situation_id', index=1, number=2, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='seed_purpose', full_name='EA.Sims4.Persistence.SituationSeedData.seed_purpose', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='invite_only', full_name='EA.Sims4.Persistence.SituationSeedData.invite_only', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='host_sim_id', full_name='EA.Sims4.Persistence.SituationSeedData.host_sim_id', index=4, number=5, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='assignments', full_name='EA.Sims4.Persistence.SituationSeedData.assignments', index=5, number=6, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='user_facing', full_name='EA.Sims4.Persistence.SituationSeedData.user_facing', index=6, number=7, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='duration', full_name='EA.Sims4.Persistence.SituationSeedData.duration', index=7, number=8, type=2, cpp_type=6, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='zone_id', full_name='EA.Sims4.Persistence.SituationSeedData.zone_id', index=8, number=9, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='jobs_and_role_states', full_name='EA.Sims4.Persistence.SituationSeedData.jobs_and_role_states', index=9, number=10, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='create_time', full_name='EA.Sims4.Persistence.SituationSeedData.create_time', index=10, number=11, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='score', full_name='EA.Sims4.Persistence.SituationSeedData.score', index=11, number=12, type=2, cpp_type=6, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='simple_data', full_name='EA.Sims4.Persistence.SituationSeedData.simple_data', index=12, number=13, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='complex_data', full_name='EA.Sims4.Persistence.SituationSeedData.complex_data', index=13, number=14, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='filter_requesting_sim_id', full_name='EA.Sims4.Persistence.SituationSeedData.filter_requesting_sim_id', index=14, number=15, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='goal_tracker_data', full_name='EA.Sims4.Persistence.SituationSeedData.goal_tracker_data', index=15, number=16, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='start_time', full_name='EA.Sims4.Persistence.SituationSeedData.start_time', index=16, number=17, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='active_household_id', full_name='EA.Sims4.Persistence.SituationSeedData.active_household_id', index=17, number=18, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='scoring_enabled', full_name='EA.Sims4.Persistence.SituationSeedData.scoring_enabled', index=18, number=19, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='main_goal_visibility', full_name='EA.Sims4.Persistence.SituationSeedData.main_goal_visibility', index=19, number=20, type=8, cpp_type=7, label=1, has_default_value=True, default_value=True, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='linked_sim_id', full_name='EA.Sims4.Persistence.SituationSeedData.linked_sim_id', index=20, number=21, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=1685, serialized_end=2443)
_SITUATIONBLACKLISTTAGDATA = descriptor.Descriptor(name='SituationBlacklistTagData', full_name='EA.Sims4.Persistence.SituationBlacklistTagData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='tag', full_name='EA.Sims4.Persistence.SituationBlacklistTagData.tag', index=0, number=1, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='time', full_name='EA.Sims4.Persistence.SituationBlacklistTagData.time', index=1, number=2, type=4, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=2445, serialized_end=2499)
_SITUATIONBLACKLISTDATA = descriptor.Descriptor(name='SituationBlacklistData', full_name='EA.Sims4.Persistence.SituationBlacklistData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='sim_id', full_name='EA.Sims4.Persistence.SituationBlacklistData.sim_id', index=0, number=1, type=6, cpp_type=4, label=2, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='tag_data', full_name='EA.Sims4.Persistence.SituationBlacklistData.tag_data', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=2501, serialized_end=2608)
_ALLSITUATIONDATA = descriptor.Descriptor(name='AllSituationData', full_name='EA.Sims4.Persistence.AllSituationData', filename=None, file=DESCRIPTOR, containing_type=None, fields=[descriptor.FieldDescriptor(name='seeds', full_name='EA.Sims4.Persistence.AllSituationData.seeds', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='leave_situation_id', full_name='EA.Sims4.Persistence.AllSituationData.leave_situation_id', index=1, number=2, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='leave_now_situation_id', full_name='EA.Sims4.Persistence.AllSituationData.leave_now_situation_id', index=2, number=3, type=6, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None), descriptor.FieldDescriptor(name='blacklist_data', full_name='EA.Sims4.Persistence.AllSituationData.blacklist_data', index=3, number=4, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, options=None)], extensions=[], nested_types=[], enum_types=[], options=None, is_extendable=False, extension_ranges=[], serialized_start=2611, serialized_end=2815)
_COMPLETEDSITUATIONGOALDATA.fields_by_name['situation_goal'].message_type = _SITUATIONGOALDATA
_SITUATIONGOALTRACKERDATA.fields_by_name['chains'].message_type = _SITUATIONGOALCHAINDATA
_SITUATIONGOALTRACKERDATA.fields_by_name['minor_goals'].message_type = _SITUATIONGOALDATA
_SITUATIONGOALTRACKERDATA.fields_by_name['main_goal'].message_type = _SITUATIONGOALDATA
_SITUATIONGOALTRACKERDATA.fields_by_name['completed_goals'].message_type = _COMPLETEDSITUATIONGOALDATA
_SITUATIONGOALTRACKERDATA.fields_by_name['goal_tracker_type'].enum_type = _SITUATIONGOALTRACKERDATA_GOALTRACKERTYPE
_SITUATIONGOALTRACKERDATA_GOALTRACKERTYPE.containing_type = _SITUATIONGOALTRACKERDATA
_SITUATIONSEEDDATA.fields_by_name['assignments'].message_type = _SITUATIONASSIGNMENTDATA
_SITUATIONSEEDDATA.fields_by_name['jobs_and_role_states'].message_type = _SITUATIONJOBANDROLESTATE
_SITUATIONSEEDDATA.fields_by_name['simple_data'].message_type = _SITUATIONSIMPLESEEDLINGDATA
_SITUATIONSEEDDATA.fields_by_name['complex_data'].message_type = _SITUATIONCOMPLEXSEEDLINGDATA
_SITUATIONSEEDDATA.fields_by_name['goal_tracker_data'].message_type = _SITUATIONGOALTRACKERDATA
_SITUATIONBLACKLISTDATA.fields_by_name['tag_data'].message_type = _SITUATIONBLACKLISTTAGDATA
_ALLSITUATIONDATA.fields_by_name['seeds'].message_type = _SITUATIONSEEDDATA
_ALLSITUATIONDATA.fields_by_name['blacklist_data'].message_type = _SITUATIONBLACKLISTDATA
DESCRIPTOR.message_types_by_name['SituationGoalData'] = _SITUATIONGOALDATA
DESCRIPTOR.message_types_by_name['CompletedSituationGoalData'] = _COMPLETEDSITUATIONGOALDATA
DESCRIPTOR.message_types_by_name['SituationGoalChainData'] = _SITUATIONGOALCHAINDATA
DESCRIPTOR.message_types_by_name['SituationGoalTrackerData'] = _SITUATIONGOALTRACKERDATA
DESCRIPTOR.message_types_by_name['SituationAssignmentData'] = _SITUATIONASSIGNMENTDATA
DESCRIPTOR.message_types_by_name['SituationSimpleSeedlingData'] = _SITUATIONSIMPLESEEDLINGDATA
DESCRIPTOR.message_types_by_name['SituationComplexSeedlingData'] = _SITUATIONCOMPLEXSEEDLINGDATA
DESCRIPTOR.message_types_by_name['SituationJobAndRoleState'] = _SITUATIONJOBANDROLESTATE
DESCRIPTOR.message_types_by_name['SituationSeedData'] = _SITUATIONSEEDDATA
DESCRIPTOR.message_types_by_name['SituationBlacklistTagData'] = _SITUATIONBLACKLISTTAGDATA
DESCRIPTOR.message_types_by_name['SituationBlacklistData'] = _SITUATIONBLACKLISTDATA
DESCRIPTOR.message_types_by_name['AllSituationData'] = _ALLSITUATIONDATA

class SituationGoalData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONGOALDATA

class CompletedSituationGoalData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _COMPLETEDSITUATIONGOALDATA

class SituationGoalChainData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONGOALCHAINDATA

class SituationGoalTrackerData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONGOALTRACKERDATA

class SituationAssignmentData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONASSIGNMENTDATA

class SituationSimpleSeedlingData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONSIMPLESEEDLINGDATA

class SituationComplexSeedlingData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONCOMPLEXSEEDLINGDATA

class SituationJobAndRoleState(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONJOBANDROLESTATE

class SituationSeedData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONSEEDDATA

class SituationBlacklistTagData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONBLACKLISTTAGDATA

class SituationBlacklistData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _SITUATIONBLACKLISTDATA

class AllSituationData(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _ALLSITUATIONDATA
