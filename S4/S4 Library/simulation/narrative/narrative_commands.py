from narrative.narrative_enums import NarrativeEvent
from server_commands.argument_helpers import TunableInstanceParam
import services
import sims4.commands

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
