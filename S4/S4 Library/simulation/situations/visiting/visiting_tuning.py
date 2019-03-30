from sims4.tuning.tunable import TunableList, TunableReference
import services

class VisitingTuning:
    ALWAYS_WELCOME_TRAITS = TunableList(description='\n        Traits that will guarantee that after the Sim is welcomed into a \n        household, it will always be automatically welcomed if he/she comes\n        back.\n        i.e. Vampires are always welcomed after being welcomed once.\n        ', tunable=TunableReference(description='\n            Trait reference to make the Sim always be welcomed after they \n            are welcomed once.\n            ', manager=services.trait_manager(), pack_safe=True))
