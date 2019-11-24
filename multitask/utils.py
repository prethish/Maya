import os
import sys
try:
    import resource
except ImportError:
    pass

def memory_usage():
    if sys.platform == 'win32':
        return "UNDEF"
    rusage_denom = 1024
    if sys.platform == 'darwin':
        # ... it seems that in OSX the output is different units ...
        rusage_denom = rusage_denom * rusage_denom
    
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
    return mem