import services
import sims4.tuning.tunable
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory

class AllCompletionType(HasTunableSingletonFactory, AutoFactoryInit):
	FACTORY_TUNABLES = {
		'description': '\n            Choosing this will require all objectives to be completed.\n            '
	}

	def completion_requirement (self, milestone):
		return len(milestone.objectives)

class SubsetCompletionType(HasTunableSingletonFactory, AutoFactoryInit):
	FACTORY_TUNABLES = {
		'description': '\n            Choosing this will require a tuned subset of objectives to be completed.\n            ',
		'number_required': sims4.tuning.tunable.Tunable(description = '\n            The number of objectives required for this aspiration to complete.\n            ', tunable_type = int, default = 1)
	}

	def completion_requirement (self, _):
		return self.number_required

class Milestone:
	INSTANCE_TUNABLES = {
		'objectives': sims4.tuning.tunable.TunableList(description = '\n            A Set of objectives for completing this milestone.\n            ', tunable = sims4.tuning.tunable.TunableReference(description = '\n                An Objective that needs to be completed for this Milestone.\n                ', manager = services.get_instance_manager(sims4.resources.Types.OBJECTIVE), pack_safe = True), export_modes = sims4.tuning.tunable_base.ExportModes.All),
		'objective_completion_type': sims4.tuning.tunable.TunableVariant(description = '\n            A requirement of what objectives need to be completed.                          \n            ', complete_all = AllCompletionType.TunableFactory(), complete_subset = SubsetCompletionType.TunableFactory(), default = 'complete_all')
	}

	@classmethod
	def objective_completion_count (cls):
		return cls.objective_completion_type.completion_requirement(cls)
