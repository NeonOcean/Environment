from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class RouteEventType(enum.Int, export=False):
    BUFF_REPEAT = 1
    BUFF_SINGLE = 2
    BROADCASTER = 3
    INTERACTION_PRE = 4
    INTERACTION_POST = 5
    FIRST_OUTDOOR = 6
    LAST_OUTDOOR = 7

class RouteEventPriority(DynamicEnum):
    DEFAULT = 0

class RoutingStageEvent(enum.Int, export=False):
    ROUTE_START = 0
    ROUTE_END = 1
