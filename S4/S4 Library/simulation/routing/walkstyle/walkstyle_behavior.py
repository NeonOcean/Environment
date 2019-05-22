import itertools
import operator
from primitives.routing_utils import get_block_id_for_node
from routing.walkstyle.walkstyle_enums import WalkStyleRunAllowedFlags
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableRange, TunableMapping, TunableList, TunableTuple, TunableEnumFlags, OptionalTunable, TunableReference
import services
import sims4.math
logger = sims4.log.Logger('WalkstyleBehavior')

class WalksStyleBehavior(HasTunableSingletonFactory, AutoFactoryInit):
    SWIMMING_WALKSTYLES = TunableList(description='\n        The exhaustive list of walkstyles allowed while Sims are swimming. If a\n        Sim has a request for a walkstyle that is not supported, the first\n        element is used as a replacement.\n        ', tunable=TunableWalkstyle())
    WALKSTYLE_COST = TunableMapping(description='\n        Associate a specific walkstyle to a statistic cost before the walkstyle\n        can be activated.\n        ', key_type=TunableWalkstyle(description='\n            The walkstyle that should have a specified cost when triggered.\n            ', pack_safe=True), value_type=TunableTuple(description='\n            Cost data of the specified walkstyle.\n            ', walkstyle_cost_statistic=TunableReference(description='\n                The statistic we are operating on when the walkstyle is\n                triggered.\n                ', manager=services.get_instance_manager(sims4.resources.Types.STATISTIC), pack_safe=True), cost=TunableRange(description='\n                When the walkstyle is triggered during a route, this is the\n                cost that will be substracted from the specified statistic. \n                ', tunable_type=int, default=1, minimum=0)))
    WALKSTYLES_OVERRIDE_TELEPORT = TunableList(description='\n        Any walkstyles found here will be able to override the teleport styles\n        if they are specified.\n        ', tunable=TunableWalkstyle(pack_safe=True))
    FACTORY_TUNABLES = {'carry_walkstyle_behavior': OptionalTunable(description='\n            Define the walkstyle the Sim plays whenever they are being carried\n            by another Sim.\n            \n            If this is set to "no behavior", the Sim will not react to the\n            parent\'s walkstyle at all. They will play no walkstyle, and rely on\n            posture idles to animate.\n            \n            If this is set, Sims have the ability to modify their walkstyle\n            whenever their parent is routing.\n            ', tunable=TunableTuple(description='\n                Specify how this Sim behaves when being carried by another Sim.\n                ', default_carry_walkstyle=TunableWalkstyle(description='\n                    Unless an override is specified, this is the walkstyle\n                    applied to the Sim whenever they are being carried.\n                    '), carry_walkstyle_overrides=TunableMapping(description='\n                    Define carry walkstyle overrides. For instance, we might\n                    want to specify a different carry walkstyle if the parent is\n                    frantically running, for example.\n                    ', key_type=TunableWalkstyle(description='\n                        The walkstyle that this carry walkstyle override applies to.\n                        ', pack_safe=True), value_type=TunableWalkstyle(description='\n                        The carry walkstyle override.\n                        ', pack_safe=True))), enabled_name='Apply_Carry_Walkstyle', disabled_name='No_Behavior'), 'combo_walkstyle_replacements': TunableList(description='\n            The prioritized list of the combo walkstyle replacement rules. We\n            use this list to decide if a Sim should use a combo walk style based\n            on the the highest priority walkstyle request, and other walkstyles\n            that might affect the replacement based on the key combo rules.\n            ', tunable=TunableTuple(description='\n                The n->1 mapping of walkstyle replacement. \n                ', key_combo_list=TunableList(description='\n                    The list of the walkstyles used as key combos. If the\n                    current highest priority walkstyle exists in this list, and\n                    the Sim has every other walkstyle in the key list, then we\n                    replace this with the result walkstyle tuned in the tuple.\n                    ', tunable=TunableWalkstyle(pack_safe=True)), result=TunableWalkstyle(description='\n                    The mapped combo walkstyle.\n                    ', pack_safe=True))), 'default_walkstyle': TunableWalkstyle(description='\n            The underlying walkstyle for this Sim. This is most likely going to\n            be overridden by the CAS walkstyle, emotional walkstyles, buff\n            walkstyles, etc...\n            '), 'run_allowed_flags': TunableEnumFlags(description="\n            Define where the Sim is allowed to run. Certain buffs might suppress\n            a Sim's ability to run.\n            ", enum_type=WalkStyleRunAllowedFlags, default=WalkStyleRunAllowedFlags.RUN_ALLOWED_OUTDOORS, allow_no_flags=True), 'run_disallowed_walkstyles': TunableList(description="\n            A set of walkstyles that would never allow a Sim to run, i.e., if\n            the Sim's requested walkstyle is in this set, they will not run,\n            even to cover great distances.\n            ", tunable=TunableWalkstyle(pack_safe=True)), 'run_required_total_distance': TunableRange(description='\n            For an entire route, the minimum distance required for Sim to run.\n            ', tunable_type=float, minimum=0, default=20), 'run_required_segment_distance': TunableRange(description='\n            For a specific route segment, the minimum distance required for the\n            Sim to run.\n            ', tunable_type=float, minimum=0, default=10), 'run_walkstyle': TunableWalkstyle(description='\n            The walkstyle to use when this Sim is supposed to be running.\n            '), 'short_walkstyle': TunableWalkstyle(description='\n            The walkstyle to use when Sims are routing over a distance shorter\n            than the one defined in "Short Walkstyle Distance" or any of the\n            overrides.\n            \n            This value is used if no override is tuned in "Short Walkstyle Map".\n            '), 'short_walkstyle_distance': TunableRange(description="\n            Any route whose distance is less than this value will request the\n            short version of the Sim's current walkstyle.\n            ", tunable_type=float, minimum=0, default=7), 'short_walkstyle_distance_override_map': TunableMapping(description="\n            If a Sim's current walkstyle is any of the ones specified in here,\n            use the associated value to determine if the short version of the\n            walkstyle is to be requested.\n            ", key_type=TunableWalkstyle(description='\n                The walkstyle that this distance override applies to.\n                ', pack_safe=True), value_type=TunableRange(description="\n                Any route whose distance is less than this value will request\n                the short version of the Sim's current walkstyle, provided the\n                Sim's current walkstyle is the associated walkstyle.\n                ", tunable_type=float, minimum=0, default=7)), 'short_walkstyle_map': TunableMapping(description='\n            Associate a specific short version of a walkstyle to walkstyles.\n            ', key_type=TunableWalkstyle(description='\n                The walkstyle that this short walkstyle mapping applies to.\n                ', pack_safe=True), value_type=TunableWalkstyle(description='\n                The short version of the associated walkstyle.\n                ', pack_safe=True))}

    def _get_walkstyle_overrides(self, actor):
        if actor.is_sim:
            return tuple(buff.walkstyle_behavior_override for buff in actor.get_active_buff_types() if buff.walkstyle_behavior_override is not None)
        return ()

    def apply_walkstyle_to_path(self, actor, path, time_offset=None):
        walkstyle = self.get_walkstyle_for_path(actor, path)
        path_nodes = list(path.nodes)
        for path_node in path_nodes:
            if not time_offset is None:
                if path_node.time >= time_offset:
                    path_node.walkstyle = walkstyle
            path_node.walkstyle = walkstyle
        if walkstyle in self.run_disallowed_walkstyles:
            return walkstyle
        walkstyle_overrides = self._get_walkstyle_overrides(actor)
        run_required_total_distance = sims4.math.safe_max((override for override in walkstyle_overrides if override.run_required_total_distance is not None), key=operator.attrgetter('walkstyle_behavior_priority'), default=self).run_required_total_distance
        if path.length() < run_required_total_distance:
            return walkstyle
        run_allowed_flags = self.run_allowed_flags
        for walkstyle_override in walkstyle_overrides:
            run_allowed_flags |= walkstyle_override.additional_run_flags
        for walkstyle_override in walkstyle_overrides:
            run_allowed_flags &= ~walkstyle_override.removed_run_flags
        if not run_allowed_flags:
            return walkstyle
        run_required_segment_distance = sims4.math.safe_max((override for override in walkstyle_overrides if override.run_required_segment_distance is not None), key=operator.attrgetter('walkstyle_behavior_priority'), default=self).run_required_segment_distance
        all_path_node_data = []
        for (start_node, end_node) in zip(path_nodes, path_nodes[1:]):
            switch_routing_surface = start_node.routing_surface_id != end_node.routing_surface_id
            is_outside = start_node.portal_id == 0 and get_block_id_for_node(start_node) == 0
            route_key = (switch_routing_surface, is_outside)
            all_path_node_data.append((route_key, start_node, end_node))
        for ((_, is_outside), path_node_data) in itertools.groupby(all_path_node_data, key=operator.itemgetter(0)):
            if is_outside and not run_allowed_flags & WalkStyleRunAllowedFlags.RUN_ALLOWED_OUTDOORS:
                continue
            if not is_outside and not run_allowed_flags & WalkStyleRunAllowedFlags.RUN_ALLOWED_INDOORS:
                continue
            path_node_data = list(path_node_data)
            segment_length = sum((sims4.math.Vector3(*start_node.position) - sims4.math.Vector3(*end_node.position)).magnitude_2d() for (_, start_node, end_node) in path_node_data)
            if segment_length < run_required_segment_distance:
                continue
            for (_, path_node, _) in path_node_data:
                if not time_offset is None:
                    if path_node.time >= time_offset:
                        path_node.walkstyle = self.get_run_walkstyle(actor)
                path_node.walkstyle = self.get_run_walkstyle(actor)
        return walkstyle

    def get_combo_replacement(self, highest_priority_walkstyle, walkstyle_list):
        for combo_tuple in self.combo_walkstyle_replacements:
            key_combo_list = combo_tuple.key_combo_list
            if highest_priority_walkstyle in key_combo_list:
                if all(ws in walkstyle_list for ws in key_combo_list):
                    return combo_tuple

    def get_combo_replaced_walkstyle(self, highest_priority_walkstyle, walkstyle_list):
        combo_tuple = self.get_combo_replacement(highest_priority_walkstyle, walkstyle_list)
        if combo_tuple is not None:
            return combo_tuple.result

    def get_default_walkstyle(self, actor):
        walkstyle = actor.get_cost_valid_walkstyle(WalksStyleBehavior.WALKSTYLE_COST)
        walkstyle_list = actor.get_walkstyle_list()
        replaced_walkstyle = self.get_combo_replaced_walkstyle(walkstyle, walkstyle_list)
        if replaced_walkstyle is not None:
            walkstyle = replaced_walkstyle
        return walkstyle

    def get_short_walkstyle(self, walkstyle, actor):
        short_walkstyle = self._get_property_override(actor, 'short_walkstyle')
        return self.short_walkstyle_map.get(walkstyle, short_walkstyle)

    def get_run_walkstyle(self, actor):
        run_walkstyle = self._get_property_override(actor, 'run_walkstyle')
        return run_walkstyle

    def _get_property_override(self, actor, property_name):
        overrides = self._get_walkstyle_overrides(actor)
        override = sims4.math.safe_max((override for override in overrides if getattr(override, property_name) is not None), key=operator.attrgetter('walkstyle_behavior_priority'), default=self)
        property_value = getattr(override, property_name)
        return property_value

    def _apply_walkstyle_cost(self, actor, walkstyle):
        walkstyle_cost = WalksStyleBehavior.WALKSTYLE_COST.get(walkstyle, None)
        if walkstyle_cost is not None:
            stat_instance = actor.get_stat_instance(walkstyle_cost.walkstyle_cost_statistic)
            if stat_instance is None:
                logger.error('Statistic {}, not found on Sim {} for walkstyle cost', walkstyle_cost.walkstyle_cost_statistic, actor, owner='camilogarcia')
                return
            stat_instance.add_value(-walkstyle_cost.cost)

    def get_walkstyle_for_path(self, actor, path):
        walkstyle = self.get_default_walkstyle(actor)
        short_walk_distance = self.short_walkstyle_distance_override_map.get(walkstyle, self.short_walkstyle_distance)
        if path.length() < short_walk_distance:
            walkstyle = self.get_short_walkstyle(walkstyle, actor)
        if actor.is_sim:
            if actor.in_pool and walkstyle not in self.SWIMMING_WALKSTYLES:
                return self.SWIMMING_WALKSTYLES[0]
            else:
                posture = actor.posture
                if posture.mobile and posture.compatible_walkstyles and walkstyle not in posture.compatible_walkstyles:
                    return posture.compatible_walkstyles[0]
        return walkstyle
