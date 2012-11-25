"""Utilities for working with files n stuff."""

import errno
import os.path

def ensure_dir(path):
    """Ensure the directories for ``path`` exist. 

    ``path`` may be a file path or directory path. 
    """

    
    try:
        os.makedirs(os.path.dirname(path))
    except (EnvironmentError) as e:
        if not(e.errno == errno.EEXIST and 
            e.filename == os.path.dirname(path)):
            raise
    return