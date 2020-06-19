from singletons import DEFAULT
import _hashutil
hash32 = _hashutil.hash32
hash64 = _hashutil.hash64
try:
    KEYNAMEMAPTYPE_UNUSED = _hashutil.KEYNAMEMAPTYPE_UNUSED
    KEYNAMEMAPTYPE_RESOURCES = _hashutil.KEYNAMEMAPTYPE_RESOURCES
    KEYNAMEMAPTYPE_RESOURCESTRINGS = _hashutil.KEYNAMEMAPTYPE_RESOURCESTRINGS
    KEYNAMEMAPTYPE_OBJECTINSTANCES = _hashutil.KEYNAMEMAPTYPE_OBJECTINSTANCES
    KEYNAMEMAPTYPE_SWARM = _hashutil.KEYNAMEMAPTYPE_SWARM
    KEYNAMEMAPTYPE_STRINGHASHES = _hashutil.KEYNAMEMAPTYPE_STRINGHASHES
    KEYNAMEMAPTYPE_TUNINGINSTANCES = _hashutil.KEYNAMEMAPTYPE_TUNINGINSTANCES
    KEYNAMEMAPTYPE_END = _hashutil.KEYNAMEMAPTYPE_END
except:
    pass

def unhash(value:int, table_type:int=None):
    if value < 0:
        raise ValueError('Negative numbers are not valid hashes.')
    if table_type is None:
        result = _hashutil.unhash64(value)
    else:
        result = _hashutil.unhash64(value, table_type)
    return '#{}#'.format(result)

def unhash_with_fallback(value, fallback_pattern=DEFAULT, table_type:int=None):
    if fallback_pattern is DEFAULT:
        if value < 8589934592:
            fallback_pattern = '{:#010x}'
        else:
            fallback_pattern = '{:#018x}'
    return fallback_pattern.format(value)

def obj_str_hash(obj):
    return hash(str(obj))
