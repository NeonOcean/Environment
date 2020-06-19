import enum
import sims4.reload
with sims4.reload.protected(globals()):
    _log_arb_contents = False
AUTO_EXIT_REF_TAG = 'auto_exit'
MAX_ZERO_LENGTH_ASM_CALLS_FOR_RESET = 50
ASM_TARGET_TRANSLATION = 'TargetTranslation'
ASM_TARGET_ORIENTATION = 'TargetOrientation'
ASM_SCRIPT_EVENT_ID = 'scriptEventID'
ASM_SCRIPT_EVENT_PLACEMENT = 'scriptEventPlacement'
ASM_LANDING_SURFACE = 'LandingSurface'
ASM_THROW_ANGLE = 'ThrowAngle'
ASM_HIT_ANGLE = 'hitAngle'

class ActorType(enum.Int, export=False):
    Sim = int(149264255)
    Object = int(200706046)
    Door = int(2935391323)
    Vehicle = int(1022379774)

class InteractionAsmType(enum.IntFlags, export=False):
    Unknown = 0
    Interaction = 1
    Outcome = 2
    Response = 4
    Reactionlet = 8
    Canonical = 16
