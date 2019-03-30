import collections
from distributor.shared_messages import IconInfoData
from interactions import ParticipantTypeObject
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.loot_basic_op import BaseLootOperation
from interactions.utils.tunable_icon import TunableIcon
from sims4.localization import TunableLocalizedString, LocalizationHelperTuning
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableEnumEntry, OptionalTunable, TunableTuple, TunableList, Tunable, TunableReference, HasTunableReference, TunableVariant, HasTunableSingletonFactory, TunablePackSafeReference
from ui.notebook_tuning import NotebookCategories, NotebookSubCategories
import services
import sims4
logger = sims4.log.Logger('Notebook', default_owner='camilogarcia')

class NotebookEntry(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)):
    INSTANCE_TUNABLES = {'category_id': TunableEnumEntry(description='\n            Category type which will define the format the UI will use\n            to display the information.\n            ', tunable_type=NotebookCategories, default=NotebookCategories.INVALID), 'subcategory_id': TunableEnumEntry(description='\n            Subcategory type which will define the format the UI will use\n            to display the information.\n            ', tunable_type=NotebookSubCategories, default=NotebookSubCategories.INVALID), 'entry_text': TunableLocalizedString(description='\n            Text to be displayed on the notebook entry.        \n            '), 'entry_icon': OptionalTunable(TunableIcon(description='\n            Optional icon to be displayed with the entry text.\n            ')), 'entry_tooltip': OptionalTunable(TunableLocalizedString(description='\n            Text to be displayed when the player hovers this entry.        \n            ')), 'entry_sublist': OptionalTunable(TunableList(description='\n            List of objects linked to a notebook entry.\n            i.e. Ingredient objects attached to a serum or to a recipe.\n            ', tunable=TunableTuple(description='\n                Pair of object definitions and amount of objects needed\n                to \n                ', object_definition=TunableReference(services.definition_manager(), description='Reference to ingredient object.'), num_objects_required=Tunable(description='\n                    Number of objects required on this field.  This will be\n                    displayed next to the current value of objects found in the \n                    inventory.\n                    Example: Serums will displayed \n                             <current_objects_held / num_objects_required>\n                    ', tunable_type=int, default=0))))}

    def __init__(self, recipe_object_definition_id=None, entry_object_definition_ids=None, new_entry=True):
        self.new_entry = new_entry
        self.recipe_object_definition_id = recipe_object_definition_id
        if entry_object_definition_ids is not None:
            self.entry_object_definition_ids = set(entry_object_definition_ids)
        else:
            self.entry_object_definition_ids = set()

    def has_identical_entries(self, entries):
        for entry in entries:
            if self.__class__ == entry.__class__:
                return True
        return False

    def is_definition_based(self):
        return False

    @property
    def entry_icon_info_data(self):
        if self.entry_icon is not None:
            return IconInfoData(icon_resource=self.entry_icon)

EntryData = collections.namedtuple('EntryData', ('entry_text', 'entry_icon_info_data', 'entry_tooltip', 'entry_sublist'))
SubListData = collections.namedtuple('SubListData', ('object_definition', 'item_count', 'num_objects_required', 'is_ingredient', 'object_display_name'))

class NotebookEntryBait(NotebookEntry):
    REMOVE_INSTANCE_TUNABLES = ('entry_text', 'entry_icon', 'entry_tooltip', 'entry_sublist')

    def add_entry_definition_id(self, definition_id):
        self.entry_object_definition_ids.add(definition_id)

    def is_definition_based(self):
        return self.recipe_object_definition_id is not None

    def get_definition_notebook_data(self, ingredient_cache=[]):
        definition_manager = services.definition_manager()
        recipe_definition = definition_manager.get(self.recipe_object_definition_id)
        sublist = set()
        for entry_definition_id in self.entry_object_definition_ids:
            entry_definition = definition_manager.get(entry_definition_id)
            if recipe_definition is None or entry_definition is None:
                return
            sublist.add(SubListData(entry_definition, 0, 1, False, None))
        return EntryData(LocalizationHelperTuning.get_object_name(recipe_definition), IconInfoData(obj_def_id=recipe_definition.id), None, sublist)

    def has_identical_entries(self, entries):
        for entry in entries:
            if entry.recipe_object_definition_id != self.recipe_object_definition_id:
                pass
            else:
                for entry_id in self.entry_object_definition_ids:
                    if entry_id not in entry.entry_object_definition_ids:
                        entry.add_entry_definition_id(entry_id)
                return True
        return False

class NotebookEntryRecipe(NotebookEntry):
    REMOVE_INSTANCE_TUNABLES = ('entry_text', 'entry_icon', 'entry_tooltip', 'entry_sublist')

    @property
    def entry_object_definition_id(self):
        if self.entry_object_definition_ids:
            return next(iter(self.entry_object_definition_ids))
        return 0

    def is_definition_based(self):
        return True

    def get_definition_notebook_data(self, ingredient_cache=[]):
        ingredients_used = {}
        manager = services.get_instance_manager(sims4.resources.Types.RECIPE)
        recipe_definition = manager.get(self.entry_object_definition_id)
        if recipe_definition is None:
            return
        final_product = recipe_definition.final_product_definition
        ingredient_display = []
        if recipe_definition.use_ingredients is not None:
            for tuned_ingredient_factory in recipe_definition.sorted_ingredient_requirements:
                ingredients_found_count = 0
                ingredients_needed_count = 0
                ingredient_requirement = tuned_ingredient_factory()
                ingredient_requirement.attempt_satisfy_ingredients(ingredient_cache, ingredients_used)
                ingredients_found_count += ingredient_requirement.count_satisfied
                ingredients_needed_count += ingredient_requirement.count_required
                ingredient_display.append(SubListData(None, ingredients_found_count, ingredients_needed_count, True, ingredient_requirement.get_diplay_name()))
        return EntryData(LocalizationHelperTuning.get_object_name(final_product), IconInfoData(obj_def_id=final_product.id), None, ingredient_display)

    def has_identical_entries(self, entries):
        if all(entry.entry_object_definition_id != self.entry_object_definition_id for entry in entries):
            return False
        return super().has_identical_entries(entries)

class NotebookEntryLootOp(BaseLootOperation):

    class _NotebookEntryFromParticipant(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reference_notebook_entry': TunableReference(description='\n                Reference to a notebook entry where we will get the core notebook\n                data (category, subcategory) but we will use the the object \n                reference to populate the rest of the data. \n                ', manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY), pack_safe=True), 'participant': TunableEnumEntry(description='\n                Participant on which we will get the noteboook entry information \n                from.\n                ', tunable_type=ParticipantTypeObject, default=ParticipantTypeObject.Object)}

        def get_entries(self, resolver):
            entry_target = resolver.get_participant(self.participant)
            if entry_target is None:
                logger.error('Notebook entry {} for participant {} is None, participant type is probably invalid for this loot.', self, self.participant)
                return
            return entry_target.get_notebook_information(self.reference_notebook_entry)

    class _NotebookEntryFromReference(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'notebook_entry': TunableReference(description='\n                Create a new entry filling up all the fields for an entry.\n                ', manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY), pack_safe=True)}

        def get_entries(self, resolver):
            return (self.notebook_entry(),)

    class _NotebookEntryFromRecipe(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reference_notebook_entry': TunablePackSafeReference(description='\n                Reference to a notebook entry where we will get the core notebook\n                data (category, subcategory).   \n                ', manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)), 'recipe': TunablePackSafeReference(description='\n                The recipe to use to create the notebook entry.  This recipe\n                should have the use_ingredients tunable set so the notebook\n                system has data to populate the entry.\n                ', manager=services.recipe_manager())}

        def get_entries(self, resolver):
            if self.recipe is None or self.reference_notebook_entry is None:
                return
            return (self.reference_notebook_entry(None, (self.recipe.guid64,)),)

    FACTORY_TUNABLES = {'notebook_entry': TunableVariant(description='\n            Type of unlock for notebook entries.\n            ', create_new_entry=_NotebookEntryFromReference.TunableFactory(), create_entry_from_participant=_NotebookEntryFromParticipant.TunableFactory(), create_entry_from_recipe=_NotebookEntryFromRecipe.TunableFactory())}

    def __init__(self, *args, notebook_entry, **kwargs):
        super().__init__(*args, **kwargs)
        self.notebook_entry = notebook_entry

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            return False
        if subject.notebook_tracker is None:
            logger.warn('Trying to unlock a notebook entry on {}, but the notebook tracker is None. LOD issue?', subject)
            return False
        unlocked_entries = self.notebook_entry.get_entries(resolver)
        if not unlocked_entries:
            return False
        for unlocked_entry in unlocked_entries:
            subject.notebook_tracker.unlock_entry(unlocked_entry)

class NotebookDisplayElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):

    def _do_behavior(self):
        if self.interaction.sim.sim_info.notebook_tracker is None:
            logger.error("Trying to display a notebook on {} but that Sim doesn't have a notebook tracker. LOD issue?", self.interaction.sim)
            return False
        self.interaction.sim.sim_info.notebook_tracker.generate_notebook_information()
        return True
