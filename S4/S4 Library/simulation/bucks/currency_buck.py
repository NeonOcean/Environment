from bucks.bucks_enums import BucksType
from display_snippet_tuning import DisplaySnippet
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableEnumEntry, Tunable
import sims4.log
from sims4.tuning.tunable_base import ExportModes, EnumBinaryExportType, GroupNames
logger = sims4.log.Logger('CurrencyBuck', default_owner='rrodgers')

class CurrencyBuck(DisplaySnippet):
    INSTANCE_TUNABLES = {'buck_type': TunableEnumEntry(description='\n            The buck type for this currency.\n            ', tunable_type=BucksType, default=BucksType.INVALID, export_modes=ExportModes.ClientBinary, binary_type=EnumBinaryExportType.EnumUint32), 'value_string': TunableLocalizedString(description='\n            A string like "{0.Money}" that will be used in UI to display a\n            value of this currency.\n            ', export_modes=ExportModes.All, tuning_group=GroupNames.UI), 'gain_string': TunableLocalizedString(description='\n            A string like "++{0.Money}" that will be used in UI to display an\n            increase in this currency.\n            ', export_modes=ExportModes.All, tuning_group=GroupNames.UI), 'lose_string': TunableLocalizedString(description='\n            A string like "--{0.Money}" that will be used in UI to display a\n            decrease in this currency.\n            ', export_modes=ExportModes.All, tuning_group=GroupNames.UI), 'flyaway_gain_audio': Tunable(description='\n            Audio to use for the flyaway for this currency if currency is \n            gained.\n            ', tunable_type=str, default='', allow_empty=True, tuning_group=GroupNames.UI, export_modes=ExportModes.ClientBinary), 'flyaway_loss_audio': Tunable(description='\n            Audio to use for the flyaway for this currency if currency is \n            lost.\n            ', tunable_type=str, default='', allow_empty=True, tuning_group=GroupNames.UI, export_modes=ExportModes.ClientBinary)}
