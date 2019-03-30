from sims.sim_info_types import Age, Gender, SpeciesExtended
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry

class _AdoptionSimData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'age': TunableEnumEntry(description="\n            The adopted Sim's age.\n            ", tunable_type=Age, default=Age.BABY), 'gender': TunableEnumEntry(description="\n            The adopted Sim's gender.\n            ", tunable_type=Gender, default=Gender.FEMALE), 'species': TunableEnumEntry(description="\n            The adopted Sim's species.\n            ", tunable_type=SpeciesExtended, default=SpeciesExtended.HUMAN)}
