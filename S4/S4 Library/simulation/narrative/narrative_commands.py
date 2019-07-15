from narrative.narrative_enums import NarrativeEvent
from server_commands.argument_helpers import TunableInstanceParam, get_tunable_instance
import services
import sims4.commands
from sims4.common import Pack

@sims4.commands.Command('narrative.trigger_event', command_type=sims4.commands.CommandType.Automation)
def trigger_narrative_event(event:NarrativeEvent, _connection=None):
    services.narrative_service().handle_narrative_event(event)

@sims4.commands.Command('narrative.start_narrative', command_type=sims4.commands.CommandType.Automation)
def start_narrative(narrative:TunableInstanceParam(sims4.resources.Types.NARRATIVE), _connection=None):
    services.narrative_service().start_narrative(narrative)

@sims4.commands.Command('narrative.end_narrative', command_type=sims4.commands.CommandType.Automation)
def end_narrative(narrative:TunableInstanceParam(sims4.resources.Types.NARRATIVE), _connection=None):
    services.narrative_service().end_narrative(narrative)

@sims4.commands.Command('narrative.reset_completion', command_type=sims4.commands.CommandType.Automation)
def reset_narrative_completion(narrative:TunableInstanceParam(sims4.resources.Types.NARRATIVE), _connection=None):
    services.narrative_service().reset_completion(narrative)

@sims4.commands.Command('narrative.get_active_narratives', command_type=sims4.commands.CommandType.DebugOnly)
def get_active_narratives(_connection=None):
    for active_narrative in services.narrative_service().active_narratives:
        sims4.commands.cheat_output('{}'.format(active_narrative.guid64), _connection)
    return True

@sims4.commands.Command('narrative.has_narrative', command_type=sims4.commands.CommandType.Automation)
def has_narrative(narrative_id:int, _connection=None):
    found_narrative = False
    for active_narrative in services.narrative_service().active_narratives:
        if active_narrative.guid64 == narrative_id:
            found_narrative = True
            break
    sims4.commands.automation_output('NarrativeInfo; NarrativeIsActive:{}'.format(found_narrative), _connection)
    return True

@sims4.commands.Command('narrative.restart_conservation_narrative', command_type=sims4.commands.CommandType.Cheat, pack=Pack.EP07)
def restart_conservation_narrative(_connection=None):
    narrative = get_tunable_instance(sims4.resources.Types.NARRATIVE, 'narrative_IslandConservation_Stage_Starting')
    if narrative is None:
        return
    services.narrative_service().start_narrative(narrative)
