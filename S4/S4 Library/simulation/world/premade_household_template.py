from filters.household_template import HouseholdTemplate, _get_tunable_household_member_list
from filters.sim_template import SimTemplateType
from sims.sim_spawner import SimSpawner
from sims4.tuning.tunable import OptionalTunable, TunableWorldDescription, Tunable
from sims4.utils import classproperty
import services
import sims4.log
logger = sims4.log.Logger('PremadeHousehold', default_owner='tingyul')

class PremadeHouseholdTemplate(HouseholdTemplate):
    INSTANCE_TUNABLES = {'_household_members': _get_tunable_household_member_list(template_type=SimTemplateType.PREMADE_HOUSEHOLD), '_hidden': Tunable(description='\n            If enabled, the household is hidden from Manage Households,\n            accessible from Managed Worlds.\n            ', tunable_type=bool, default=False), '_townie_street': OptionalTunable(description='\n            If enabled, this household is a townie household and is\n            assigned to a street.\n            ', tunable=TunableWorldDescription())}

    @classmethod
    def _tuning_loaded_callback(cls):
        for household_member_data in cls._household_members:
            sim_template = household_member_data.sim_template
            if sim_template.household_template is not None:
                logger.error('PremadeSimTemplate {} is used by multiple PreamdeHouseholdTemplates {}, {}', sim_template, sim_template.household_template, cls)
            sim_template.household_template = cls

    @classproperty
    def template_type(cls):
        return SimTemplateType.PREMADE_HOUSEHOLD

    @classmethod
    def create_premade_household(cls):
        account = services.account_service().get_account_by_id(SimSpawner.SYSTEM_ACCOUNT_ID)
        household = cls.create_household(None, account, creation_source='premade_household_template')
        if cls._hidden:
            household.set_to_hidden()
        if household is not None:
            household.name = cls.__name__
        return household

    @classmethod
    def apply_fixup_to_household(cls, household):
        if cls._townie_street is not None:
            if household.home_zone_id:
                logger.error('{} has Townie Street is tuned but household {} is not a townie household', cls, household)
            else:
                world_id = services.get_world_id(cls._townie_street)
                if not world_id:
                    logger.error('{} has invalid townie street: {}', cls, cls._townie_street)
                else:
                    household.set_home_world_id(world_id)
