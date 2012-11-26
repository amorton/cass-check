"""Base for Tasks. 

Tasks are the things commands run. They take input from the node or other 
tasks outputs and write output files. For example collecting logs.
"""
import logging
import os.path

import yaml

import file_util

# ============================================================================
# 

class Task(object):
    """Base for tasks."""
    
    name = ""
    """Name of the task. Used to identify it on the command line."""
    
    description = ""
    """Description of the task."""
    
    def __init__(self, args):
        self.args = args
        self.task_dir = os.path.abspath(os.path.join(self.args.check_dir, 
            self.name))

        file_util.ensure_dir(self.task_dir)
        self.log.debug("Using output dir {self.task_dir} for task "\
            "{self.name}".format(self=self))
        self.receipt = TaskReceipt(self.name, self.task_dir)
        
    def __call__(self):
        self._do_task()
        return self.task_dir

    def _do_task(self):
        raise NotImplementedError()
    
# ============================================================================
# 

class TaskReceipt(object):
    """Recipt about a task that was run."""
    log = logging.getLogger("%s.%s" % (__name__, "TaskReceipt"))
    
    def __init__(self, name, task_dir, error=None):
        self.name = name 
        self.error = error
        self.task_dir = task_dir
        
    def write(self):
        """Writes the task receipt to the current task_dir."""
        
        assert os.path.isdir(self.task_dir)
        out_file = os.path.join(self.task_dir, "receipt.yaml")
        self.log.debug("Writing task receipt for {self.name} to "\
            "{out_file}".format(self=self, out_file=out_file))

        with open(out_file, "w") as f:
            yaml.dump(vars(self), stream=f)
        return out_file