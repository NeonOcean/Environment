from event_testing.tests_with_data import InteractionTestEvents
from interactions.utils.loot import LootActions
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableSet, TunableList, Tunable, OptionalTunable, TunableReference, TunableVariant
from sims4.tuning.tunable_base import ExportModes, GroupNames
from situations.situation_curve import SituationCurve
from tunable_utils.taggables_tests import SituationIdentityTest
from zone_modifier.zone_modifier_actions import ZoneInteractionTriggers, ZoneModifierWeeklySchedule
import services
import sims4.resources

class ZoneModifier(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ZONE_MODIFIER)):
    INSTANCE_TUNABLES = {'zone_modifier_locked': Tunable(description='\n            Whether this is a locked trait that cannot be assigned/removed\n            through build/buy.\n            ', tunable_type=bool, default=False, export_modes=ExportModes.All, tuning_group=GroupNames.UI), 'enter_lot_loot': TunableSet(description='\n            Loot applied to Sims when they enter or spawn in on the lot while\n            this zone modifier is active.\n            \n            NOTE: The corresponding exit loot is not guaranteed to be given.\n            For example, if the Sim walks onto the lot, player switches to a\n            different zone, then summons that Sim, that Sim will bypass\n            getting the exit loot.\n            ', tunable=LootActions.TunableReference(pack_safe=True)), 'exit_lot_loot': TunableSet(description='\n            Loot applied to Sims when they exit or spawn off of the lot while\n            this zone modifier is active.\n            \n            NOTE: This loot is not guaranteed to be given after the enter loot.\n            For example, if the Sim walks onto the lot, player switches to a\n            different zone, then summons that Sim, that Sim will bypass\n            getting the exit loot.\n            ', tunable=LootActions.TunableReference(pack_safe=True)), 'interaction_triggers': TunableList(description='\n            A mapping of interactions to possible loots that can be applied\n            when an on-lot Sim executes them if this zone modifier is set.\n            ', tunable=ZoneInteractionTriggers.TunableFactory()), 'schedule': ZoneModifierWeeklySchedule.TunableFactory(description='\n            Schedule to be activated for this particular zone modifier.\n            '), 'prohibited_situations': OptionalTunable(description='\n            Optionally define if this zone should prevent certain situations\n            from running or getting scheduled.\n            ', tunable=SituationIdentityTest.TunableFactory(description='\n                Prevent a situation from running if it is one of the specified \n                situations or if it contains one of the specified tags.\n                ')), 'venue_requirements': TunableVariant(description='\n            Whether or not we use a blacklist or white list for the venue\n            requirements on this zone modifier.\n            ', allowed_venue_types=TunableSet(description='\n                A list of venue types that this Zone Modifier can be placed on.\n                All other venue types are not allowed.\n                ', tunable=TunableReference(description='\n                    A venue type that this Zone Modifier can be placed on.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.VENUE), pack_safe=True)), prohibited_venue_types=TunableSet(description='\n                A list of venue types that this Zone Modifier cannot be placed on.\n                ', tunable=TunableReference(description='\n                    A venue type that this Zone Modifier cannot be placed on.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.VENUE), pack_safe=True)), export_modes=ExportModes.All), 'conflicting_zone_modifiers': TunableSet(description='\n            Conflicting zone modifiers for this zone modifier. If the lot has any of the\n            specified zone modifiers, then it is not allowed to be equipped with this\n            one.\n            ', tunable=TunableReference(manager=services.get_instance_manager(sims4.resources.Types.ZONE_MODIFIER), pack_safe=True), export_modes=ExportModes.All), 'additional_situations': SituationCurve.TunableFactory(description="\n            An additional schedule of situations that can be added in addition\n            a situation scheduler's source tuning.\n            ", get_create_params={'user_facing': False})}

    @classmethod
    def handle_event(cls, sim_info, event, resolver):
        if event not in InteractionTestEvents:
            return
        sim = sim_info.get_sim_instance()
        if sim is None or not sim.is_on_active_lot():
            return
        for trigger in cls.interaction_triggers:
            trigger.handle_interaction_event(sim_info, event, resolver)

    @classmethod
    def register_interaction_triggers(cls):
        services.get_event_manager().register_tests(cls, cls._get_trigger_tests())

    @classmethod
    def unregister_interaction_triggers(cls):
        services.get_event_manager().unregister_tests(cls, cls._get_trigger_tests())

    @classmethod
    def _get_trigger_tests(cls):
        tests = list()
        for trigger in cls.interaction_triggers:
            tests.extend(trigger.get_trigger_tests())
        return tests

    @classmethod
    def is_situation_prohibited(cls, situation_type):
        if cls.prohibited_situations is None:
            return False
        return cls.prohibited_situations(situation=situation_type)
