import enum

class SimInfoLODLevel(enum.Int):
    MINIMUM = 1
    BACKGROUND = 10
    BASE = 25
    INTERACTED = 50
    FULL = 100
    ACTIVE = 125
    _prev_lod = {BACKGROUND: MINIMUM, BASE: BACKGROUND, INTERACTED: BASE, FULL: INTERACTED, ACTIVE: FULL}
    _next_lod = {MINIMUM: BACKGROUND, BACKGROUND: BASE, BASE: INTERACTED, INTERACTED: FULL}

    @staticmethod
    def get_previous_lod(from_lod):
        if from_lod in SimInfoLODLevel._prev_lod:
            return SimInfoLODLevel._prev_lod[from_lod]

    @staticmethod
    def get_next_lod(from_lod):
        if from_lod in SimInfoLODLevel._next_lod:
            return SimInfoLODLevel._next_lod[from_lod]
