from filters.household_template import HouseholdTemplate, _get_tunable_household_member_list
from filters.sim_template import SimTemplateType
from sims.sim_spawner import SimSpawner
from sims4.utils import classproperty
import services

class PremadeHouseholdTemplate(HouseholdTemplate):
    INSTANCE_TUNABLES = {'_household_members': _get_tunable_household_member_list(template_type=SimTemplateType.PREMADE_HOUSEHOLD)}

    @classproperty
    def template_type(cls):
        return SimTemplateType.PREMADE_HOUSEHOLD

    @classmethod
    def create_premade_household(cls):
        account = services.account_service().get_account_by_id(SimSpawner.SYSTEM_ACCOUNT_ID)
        household = cls.create_household(None, account, creation_source='premade_household_template')
        if household is not None:
            household.name = cls.__name__
        return household
