import services
from seasons.seasons_enums import SeasonLength, SeasonType
from sims4.resources import Types
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry, TunableMapping, TunableReference, TunableTuple
from sims4.tuning.tunable_base import EnumBinaryExportType, ExportModes
from tunable_time import Days, TunableTimeOfWeek, TunableTimeSpan

class StartingSeason(HasTunableSingletonFactory, AutoFactoryInit):
	FACTORY_TUNABLES = {
		'default_season': TunableEnumEntry(description = '\n            First season player starts the game as, unless the condition in\n            alternate season threshold is met.\n            ', tunable_type = SeasonType, default = SeasonType.FALL),
		'alternate_season': TunableTuple(description = '\n            First season the player starts with upon introduction to Seasons,\n            if the current time is past the threshold specified.\n            ', season = TunableEnumEntry(tunable_type = SeasonType, default = SeasonType.SUMMER), threshold = TunableTimeOfWeek(description = '\n                If, upon first introduction to Seasons gameplay, the player is past\n                this time of the week, we will use the alternate season specified\n                ', default_day = Days.WEDNESDAY))
	}

class SeasonsTuning:
	STARTING_SEASON = StartingSeason.TunableFactory()
	SEASON_LENGTH_OPTIONS = TunableMapping(description = '\n        A mapping of individual season length options to the length of time\n        they are set to.\n        ', key_type = TunableEnumEntry(tunable_type = SeasonLength, default = SeasonLength.NORMAL, binary_type = EnumBinaryExportType.EnumUint32), value_type = TunableTimeSpan(description = '\n            Length of this season option, in days.\n            ', default_days = 7, locked_args = {
		'hours': 0,
		'minutes': 0
	}, export_modes = ExportModes.All), tuple_name = 'SeasonLengthOptions', export_modes = ExportModes.All)
	SEASON_TYPE_MAPPING = TunableMapping(description = '\n        A mapping of the season type to the season resource it will use.\n        ', key_type = TunableEnumEntry(description = '\n            The season.\n            ', tunable_type = SeasonType, default = SeasonType.SUMMER), value_type = TunableReference(description = '\n            Season resource that will be mapped to this season.\n            ', manager = services.get_instance_manager(Types.SEASON), pack_safe = True))
