from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target
import sims4

@sims4.commands.Command('notebook.generate_notebook')
def generate_notebook(opt_sim:OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is not None and sim_info.notebook_tracker is not None:
        sim_info.notebook_tracker.generate_notebook_information()
    return True
