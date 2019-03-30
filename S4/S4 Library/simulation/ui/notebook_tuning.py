from event_testing.resolver import SingleSimResolver
from interactions.utils.tunable_icon import TunableIconAllPacks
from sims4.localization import TunableLocalizedString
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableTuple, OptionalTunable, Tunable, TunableReference
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import enum
import services
import sims4.resources
logger = sims4.log.Logger('Notebook', default_owner='camilogarcia')

class NotebookCategories(DynamicEnum, partitioned=True):
    INVALID = 1

class NotebookSubCategories(DynamicEnum, partitioned=True):
    INVALID = 1

class NotebookEntryType(enum.Int):
    EXPANDABLE_DATA = 0
    NUMBERED_DATA = 1
    ICON_DESCRIPTION_DATA = 2
    EXPANDABLE_SINGLE = 3

class NotebookTuning:
    NOTEBOOK_CATEGORY_MAPPING = TunableMapping(description='\n        A mapping from a notebook category ID to its shared category tuning \n        data.\n        ', key_type=TunableEnumEntry(description='\n            Category type.\n            ', tunable_type=NotebookCategories, default=NotebookCategories.INVALID, pack_safe=True), value_type=TunableTuple(description='\n            Global data associated to a notebook category.\n            ', category_name=TunableLocalizedString(description='\n                Name corresponding a the notebook category.\n                '), category_icon=TunableIconAllPacks(description='\n                Icon to display on the notebook UI corresponding to a category.\n                ', allow_none=True), subcategories=TunableMapping(description='\n                A mapping from a notebook category ID to its global tuning data.\n                ', key_type=TunableEnumEntry(description='\n                    Subcategory type.\n                    ', tunable_type=NotebookSubCategories, default=NotebookSubCategories.INVALID, pack_safe=True), value_type=TunableTuple(description='\n                    Mapping of subcategory ID to the shared subcategory data.\n                    ', subcategory_name=TunableLocalizedString(description='\n                        Name corresponding to a notebook subcategory.\n                        '), subcategory_icon=TunableIconAllPacks(description='\n                        Icon to display on the notebook UI corresponding to a \n                        subcategory.\n                        ', allow_none=True), subcategory_tooltip=TunableLocalizedString(description='\n                        Tooltip to be displayed when a player mouses over a\n                        subcategory icon.\n                        ', allow_none=True), format_type=TunableEnumEntry(description='\n                        Type of entry this notification will look like no the UI.\n                        - Expandable data corresponds to rows of data that expands into\n                          subitems.  For example: Scientist serums will have an expandable\n                          option to display the ingredients for the serums.\n                        - Numbered data corresponds to a list of items to be numbered\n                          as they become available.  For example: Detective notes get \n                          displayed a a numbered list.\n                        - Icon description data corresponds at an entry of an icon with\n                          some text describing it.  For example detective evidence.\n                        ', tunable_type=NotebookEntryType, default=NotebookEntryType.EXPANDABLE_DATA), show_max_entries=OptionalTunable(Tunable(description='\n                        If this is tuned, UI will use this value to display\n                        the amount of missing entries for a subcategory.\n                        For example if we tune this value to 3 and we \n                        unlock a notebook entry UI will display the data\n                        for the one entry that was unlocked but will display\n                        an empty UI field showing the player its missing \n                        two more.\n                        ', tunable_type=int, default=1)), entry_unlocked_notification=OptionalTunable(description='\n                        If enabled, a notification will be shown when a new\n                        notebook entry is unlocked.\n                        ', tunable=TunableUiDialogNotificationSnippet())))))

    @classmethod
    def get_category_id(cls, subcategory_id):
        for (key, value) in cls.NOTEBOOK_CATEGORY_MAPPING.items():
            for subcat_id in value.subcategories:
                if subcat_id == subcategory_id:
                    return key

    @classmethod
    def show_entry_unlocked_notification(cls, category_id, subcategory_id, owner_sim):
        category_data = cls.NOTEBOOK_CATEGORY_MAPPING.get(category_id)
        if category_data is None:
            logger.error('Notebook notification {} category id not found', category_id)
            return
        subcategory_data = category_data.subcategories.get(subcategory_id)
        if subcategory_data is None:
            logger.error('Notebook notification {} subcategory id not found', subcategory_id)
            return
        if subcategory_data.entry_unlocked_notification is not None:
            dialog = subcategory_data.entry_unlocked_notification(owner_sim, SingleSimResolver(owner_sim))
            dialog.show_dialog()

class NotebookCustomTypeTuning:
    BAIT_NOTEBOOK_ENTRY = TunableReference(description='\n        Reference to the notebook entry tuning which will correspond to the \n        fishing bait notebook entry where we will get all the shared \n        tunables.\n        ', manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY), class_restrictions='NotebookEntryBait')
