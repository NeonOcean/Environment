from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, Tunable, TunableTuple, TunableVariant

class WindSpeedEffect(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'wind_speed': TunableTuple(spin_speed=TunableVariant(description='\n                The spin speed level to set for the sim.\n                The locked float are fixed enums on the client.\n                ', locked_args={'OFF': 0.0, 'NORMAL': 3.0, 'FAST': 8.0}, default='OFF'), transition_speed=Tunable(description='\n                Set the transition speed of the object.\n                The transition speed defines the speed of the\n                transition between spin speeds.\n                ', tunable_type=float, default=1.0))}
