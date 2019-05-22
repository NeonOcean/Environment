from collections import Counter
from protocolbuffers import Consts_pb2
from scheduler import WeeklySchedule
from sims4.localization import LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableEnumEntry, TunableVariant, TunableTuple, TunablePercent, TunableSet
from ui.ui_dialog_notification import UiDialogNotification
import services
import sims4.commands
import sims4.resources
import tag

class RebateManager:
    TRAIT_REBATE_MAP = TunableMapping(description='\n        A mapping of traits and the tags of objects which provide a rebate for\n        the given trait.\n        ', key_type=TunableReference(description='\n            If the Sim has this trait, any objects purchased with the given\n            tag(s) below will provide a rebate.\n            ', manager=services.get_instance_manager(sims4.resources.Types.TRAIT), pack_safe=True), value_type=TunableTuple(description='\n            The information about the rebates the player should get for having\n            the mapped trait.\n            ', valid_objects=TunableVariant(description='\n                The items to which the rebate will be applied.\n                ', by_tag=TunableSet(description='\n                    The rebate will only be applied to objects purchased with the\n                    tags in this list.\n                    ', tunable=TunableEnumEntry(tunable_type=tag.Tag, default=tag.Tag.INVALID, invalid_enums=(tag.Tag.INVALID,))), locked_args={'all_purchases': None}, default='all_purchases'), rebate_percentage=TunablePercent(description='\n                The percentage of the catalog price that the player will get\n                back in the rebate.\n                ', default=10), notification_text=TunableLocalizedStringFactory(description='\n                A string representing the line item on the notification\n                explaining why Sims with this trait received a rebate.\n                \n                This string is provided one token: the percentage discount\n                obtained due to having this trait.\n                \n                e.g.:\n                 {0.Number}% off for purchasing Art and leveraging Critical\n                 Connections.\n                ')))
    REBATE_PAYMENT_SCHEDULE = WeeklySchedule.TunableFactory(description='\n        The schedule when accrued rebates will be paid out.\n        ')
    REBATE_NOTIFICATION = UiDialogNotification.TunableFactory(description="\n        The notification that will show when the player receives their rebate\n        money.\n        \n        The notification's text is provided two tokens:\n         0 - An integer representing the total rebate amount \n         \n         1 - A string. The contents of the string are a bulleted list of the\n         entries specified for each of the traits.\n         \n        e.g.:\n         A rebate check of {0.Money} has been received! Sims in the household\n         were able to save on their recent purchases:\n{1.String}\n        ")

    def __init__(self, household):
        self._household = household
        self._rebates = Counter()
        self._schedule = None

    def add_rebate_for_object(self, obj):
        for (trait, rebate_info) in self.TRAIT_REBATE_MAP.items():
            rebate_percentage = rebate_info.rebate_percentage
            valid_objects = rebate_info.valid_objects
            if self._sim_in_household_has_trait(trait):
                if not valid_objects is None:
                    if obj.has_any_tag(valid_objects):
                        self._rebates[trait] += obj.catalog_value*rebate_percentage
                self._rebates[trait] += obj.catalog_value*rebate_percentage
        if self._rebates:
            self.start_rebate_schedule()

    def _sim_in_household_has_trait(self, trait):
        return any(s.trait_tracker.has_trait(trait) for s in self._household.sim_info_gen())

    def clear_rebates(self):
        self._rebates.clear()

    def start_rebate_schedule(self):
        if self._schedule is None:
            self._schedule = self.REBATE_PAYMENT_SCHEDULE(start_callback=self.payout_rebates, schedule_immediate=False)

    def payout_rebates(self, *_):
        if not self._rebates:
            return
        rebate_reasons_string = LocalizationHelperTuning.get_bulleted_list(None, *(self.TRAIT_REBATE_MAP[t].notification_text(self.TRAIT_REBATE_MAP[t].rebate_percentage*100) for t in self._rebates))
        rebate_amount = sum(self._rebates.values())
        active_sim_info = services.active_sim_info()
        dialog = self.REBATE_NOTIFICATION(active_sim_info)
        dialog.show_dialog(additional_tokens=(rebate_amount, rebate_reasons_string))
        total_rebate_amount = sum(self._rebates.values())
        self._household.funds.add(total_rebate_amount, reason=Consts_pb2.TELEMETRY_MONEY_ASPIRATION_REWARD, sim=active_sim_info)
        self.clear_rebates()

@sims4.commands.Command('households.rebates.payout')
def payout_rebates(household_id:int=None, _connection=None):
    if household_id is None:
        household = services.active_household()
    else:
        household_manager = services.household_manager()
        household = household_manager.get(household_id)
    if household is None:
        return False
    rebate_manager = household.rebate_manager
    if rebate_manager is None:
        return False
    rebate_manager.payout_rebates()
    return True
