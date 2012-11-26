"""Utilities for working with files n stuff."""

import errno
import os.path

def ensure_dir(path):
    """Ensure the directories for ``path`` exist. 
    """

    
    try:
        os.makedirs(path)
    except (EnvironmentError) as e:
        if not(e.errno == errno.EEXIST and 
            e.filename == path):
            raise
    return