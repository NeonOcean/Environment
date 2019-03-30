import services
import sims4
logger = sims4.log.Logger('Teleport', default_owner='camilogarcia')

class TeleportHelper:

    @classmethod
    def generate_teleport_sequence(cls, teleporting_sim, teleport_data, final_path_node, cost=None):

        def _start_vfx(_):
            if teleport_data.fade_out_effect is not None:
                fade_out_vfx = teleport_data.fade_out_effect(teleporting_sim, store_target_position=True)
                fade_out_vfx.start_one_shot()

        def _fade_sim(_):
            teleporting_sim.fade_out(fade_duration=teleport_data.fade_duration)

        def _teleport_sim(_):
            final_position = sims4.math.Vector3(*final_path_node.position)
            final_orientation = sims4.math.Quaternion(*final_path_node.orientation)
            routing_surface = final_path_node.routing_surface_id
            final_position.y = services.terrain_service.terrain_object().get_routing_surface_height_at(final_position.x, final_position.z, routing_surface)
            teleporting_sim.move_to(translation=final_position, orientation=final_orientation, routing_surface=routing_surface)
            if teleport_data.teleport_effect is not None:
                fade_in_vfx = teleport_data.teleport_effect(teleporting_sim)
                fade_in_vfx.start_one_shot()
            teleporting_sim.fade_in(fade_duration=teleport_data.fade_duration)
            if cost is not None:
                stat_instance = teleporting_sim.get_stat_instance(teleport_data.teleport_cost.teleport_statistic)
                if stat_instance is None:
                    logger.error('Statistic {}, not found on Sim {} for teleport action', teleport_data.teleport_statistic, teleporting_sim)
                    return
                stat_instance.add_value(-cost)

        animation_interaction = teleporting_sim.create_animation_interaction()
        sequence = teleport_data.animation(animation_interaction, sequence=())
        animation_interaction.store_event_handler(_start_vfx, handler_id=teleport_data.start_teleport_vfx_xevt)
        animation_interaction.store_event_handler(_fade_sim, handler_id=teleport_data.start_teleport_fade_sim_xevt)
        animation_interaction.store_event_handler(_teleport_sim, handler_id=teleport_data.teleport_xevt)
        return (sequence, animation_interaction)
