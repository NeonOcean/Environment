from event_testing.resolver import InteractionResolver
from event_testing.tests import TunableTestSetWithTooltip
from filters.tunable import TunableSimFilter
from interactions import ParticipantTypeSim
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.localization_tokens import LocalizationTokens
from interactions.utils.loot import LootActions
from interactions.utils.tunable import TunableContinuation
from sims.university.university_scholarship_tuning import ScholarshipMaintenaceType, ScholarshipEvaluationType, MeritEvaluation
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableEnumFlags, TunableList, TunableTuple, TunableReference, Tunable, TunableRange, TunableVariant, OptionalTunable
from sims4.tuning.tunable_base import GroupNames, ExportModes
from sims4.utils import flexmethod
from singletons import DEFAULT
from ui.ui_dialog_picker import TunablePickerDialogVariant, ObjectPickerTuningFlags, BasePickerRow
import enum
import event_testing
import services
import sims4.tuning
logger = sims4.log.Logger('Display Snippet', default_owner='shipark')
SnippetDisplayMixin = get_display_mixin(use_string_tokens=True, has_description=True, has_icon=True, has_tooltip=True, enabled_by_default=True, export_modes=ExportModes.All)

class DisplaySnippet(SnippetDisplayMixin, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    pass

class ScholarshipAmountEnum(enum.Int, export=False):
    FIXED_AMOUNT = 0
    EVALUATION_TYPE = 1

class Scholarship(DisplaySnippet):

    @classmethod
    def _verify_tuning_callback(cls):
        if not cls._display_data.instance_display_name:
            logger.error("Scholarships require a display name, but scholarship ({})'s display name has a None value.", str(cls))
        if not cls._display_data.instance_display_description:
            logger.error("Scholarships require a display description, but scholarship ({})'s display description has a None value.", str(cls))
        if not cls._display_data.instance_display_icon:
            logger.error("Scholarships require a display icon, but scholarship ({})'s display icon has a None value.", str(cls))

    INSTANCE_TUNABLES = {'evaluation_type': ScholarshipEvaluationType.TunableFactory(description='\n            The evaluation type used by this scholarship.\n            '), 'maintenance_type': ScholarshipMaintenaceType.TunableFactory(description='\n            The maintenance requirement of this scholarship.\n            '), 'amount': TunableVariant(description='\n            If fixed_amount, use the tuned value when receiving the scholarship.\n            If evaluation_type, use the evaluation type to determine what the value of \n            the scholarship should be. \n            ', fixed_amount=TunableTuple(amount=TunableRange(description='\n                    The amount of money to award a Sim if they receive this scholarship.\n                    ', tunable_type=int, default=50, minimum=1), locked_args={'amount_enum': ScholarshipAmountEnum.FIXED_AMOUNT}), evaluation_type=TunableTuple(locked_args={'amount_enum': ScholarshipAmountEnum.EVALUATION_TYPE}))}

    @classmethod
    def verify_tuning_callback(cls):
        if cls.amount.amount_enum == ScholarshipAmountEnum.EVALUATION_TYPE and not isinstance(cls.evaluation_type, MeritEvaluation):
            logger.error('Scholarship ({}) specified its value to be determined                    by use-evaluation-type, but evaluation type ({}) does not support                    dynamic value generation.', cls, cls.evaluation_type)

    @classmethod
    def get_value(cls, sim_info):
        if cls.amount.amount_enum == ScholarshipAmountEnum.FIXED_AMOUNT:
            return cls.amount.amount
        else:
            return cls.evaluation_type.get_value(sim_info)

class Organization(DisplaySnippet):
    INSTANCE_TUNABLES = {'progress_statistic': TunableReference(description='\n            The Ranked Statistic represents Organization Progress.\n            ', manager=services.get_instance_manager(sims4.resources.Types.STATISTIC), class_restrictions='RankedStatistic', export_modes=ExportModes.All), 'hidden': Tunable(description='\n            If True, then the organization is hidden from the organization panel.\n            ', tunable_type=bool, default=False, export_modes=ExportModes.All), 'organization_task_data': TunableList(description='\n            List of possible tested organization tasks that can be offered to \n            active organization members.\n            ', tunable=TunableTuple(description='\n                Tuple of test and aspirations that is run on activating\n                organization tasks.\n                ', tests=event_testing.tests.TunableTestSet(description='\n                   Tests run when the task is activated. If tests do not pass,\n                   the tasks are not considered for assignment.\n                   '), organization_task=TunableReference(description='\n                    An aspiration to use for task completion.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.ASPIRATION), class_restrictions='AspirationOrganizationTask'))), 'organization_filter': TunableSimFilter.TunableReference(description="\n            Terms to add a member to the Organization's membership list.\n            "), 'no_events_are_scheduled_string': OptionalTunable(description='\n            If enabled and the organization has no scheduled events, this text\n            will be displayed in the org panel background.\n            ', tunable=TunableLocalizedString(description='\n                The string to show in the organization panel if there are no scheduled\n                events.\n                '))}

class DisplaySnippetPickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'picker_dialog': TunablePickerDialogVariant(description='\n            The item picker dialog.\n            ', available_picker_flags=ObjectPickerTuningFlags.ITEM, tuning_group=GroupNames.PICKERTUNING), 'subject': TunableEnumFlags(description="\n            To whom 'loot on selected' should be applied.\n            ", enum_type=ParticipantTypeSim, default=ParticipantTypeSim.Actor, tuning_group=GroupNames.PICKERTUNING), 'display_snippets': TunableList(description='\n            The list of display snippets available to select and paired loot actions\n            that will run if selected.\n            ', tunable=TunableTuple(display_snippet=TunableReference(description='\n                    A display snippet that holds the display data that will\n                    populate the row in the picker.\n                    ', manager=services.get_instance_manager(sims4.resources.Types.SNIPPET), class_restrictions='DisplaySnippet', allow_none=False), loot_on_selected=TunableList(description='\n                    A list of loot actions that will be applied to the subject Sim.\n                    ', tunable=LootActions.TunableReference(description='\n                        A loot action applied to the subject Sim.\n                        ')), tests=TunableTestSetWithTooltip(description='\n                    Test set that must pass for this snippet to be available.\n                    NOTE: A tooltip test result will take priority over any\n                    instance display tooltip tuned in the display snippet.\n                    ')), tuning_group=GroupNames.PICKERTUNING), 'display_snippet_text_tokens': LocalizationTokens.TunableFactory(description='\n            Localization tokens passed into the display snippet text fields.\n            ', tuning_group=GroupNames.PICKERTUNING), 'continuations': TunableList(description='\n            List of continuations to push when a snippet is selected.\n            ', tunable=TunableContinuation(), tuning_group=GroupNames.PICKERTUNING)}

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        snippet_count = 0
        for _ in cls.picker_rows_gen(target, context, **kwargs):
            snippet_count += 1
            if snippet_count >= cls.picker_dialog.min_selectable:
                return True
        return False

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.sim, target_sim=self.sim)
        return True
        yield

    @classmethod
    def _display_snippet_selection_gen(cls):
        if cls.display_snippets:
            for display_snippet_data in cls.display_snippets:
                yield (display_snippet_data.display_snippet.display_name, display_snippet_data.display_snippet.display_icon, display_snippet_data.display_snippet.display_description, display_snippet_data.display_snippet.display_tooltip, display_snippet_data.loot_on_selected, display_snippet_data.tests)

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        target = target if target is not DEFAULT else inst.target
        context = context if context is not DEFAULT else inst.context
        resolver = InteractionResolver(cls, inst, target=target, context=context)
        tokens = inst_or_cls.display_snippet_text_tokens.get_tokens(resolver)
        for (name, icon, description, display_tooltip, loot, tests) in inst_or_cls._display_snippet_selection_gen():
            test_result = tests.run_tests(resolver, search_for_tooltip=True)
            is_enable = test_result.result
            if is_enable or test_result.tooltip is not None:
                tooltip = None if test_result.tooltip is None else lambda *_, tooltip=test_result.tooltip: tooltip(*tokens)
                tooltip = None if display_tooltip is None else lambda *_, tooltip=display_tooltip: tooltip(*tokens)
                row = BasePickerRow(is_enable=is_enable, name=name(*tokens), icon=icon, tag=loot, row_description=description(*tokens), row_tooltip=tooltip)
                yield row

    def _on_display_snippet_selected(self, picked_choice, **kwargs):
        if picked_choice is None:
            return
        for loot_action in picked_choice[0].loot_actions:
            loot_action.apply_to_resolver(self.get_resolver())

    def on_choice_selected(self, picked_choice, **kwargs):
        self._on_display_snippet_selected(picked_choice, **kwargs)
        for continuation in self.continuations:
            self.push_tunable_continuation(continuation)
