import enum

class VehicleTransitionState(enum.Int):
    NO_STATE = 1
    DEPLOYING = ...
    MOUNTING = ...

class VehicleControlType(enum.Int, export=False):
    UNKNOWN = 0
    WHEEL = 1
