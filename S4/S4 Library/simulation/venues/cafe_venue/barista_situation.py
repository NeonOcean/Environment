from sims4.tuning.instances import lock_instance_tunables
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.complex.staff_member_situation import StaffMemberSituation
from situations.situation import Situation
from situations.situation_types import SituationCreationUIOption

class BaristaSituation(StaffMemberSituation):
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

lock_instance_tunables(BaristaSituation, exclusivity=BouncerExclusivityCategory.VENUE_EMPLOYEE, creation_ui_option=SituationCreationUIOption.NOT_AVAILABLE, duration=0, _implies_greeted_status=False)