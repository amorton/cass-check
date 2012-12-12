"""Base for Tasks. 

Tasks are the things commands run. They take input from the node or other 
tasks outputs and write output files. For example collecting logs.
"""
import logging
import os.path
import shlex
import subprocess

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
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # virtual and abstract 
    
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

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Utilities. 

    def _exec_cmd(self, cmd_line):
        """Executes the ``cmd_line``. 
        
        """

        split_line = shlex.split(str(cmd_line))
        self.log.debug("Executing command {split_line}".format(
            split_line=split_line))
        
        process = subprocess.Popen(split_line, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = process.communicate()
        if std_err:
            raise RuntimeError("Error running command {cmd_line}: "\
                "{error}".format(cmd_line=cmd_line, error=error))
                
        return std_out

    def _write_output(self, content):
        """Write the output for the task. 
        """
        
        path = os.path.join(self.task_dir, self.name)
        self.log.debug("Writing output from task {self.name} to "\
            "{path}".format(self=self, path=path))
        
        with open(path, "w") as f:
            f.write(content)
        return path
        
# ============================================================================
# 

class TaskReceipt(object):
    """Recipt about a task that was run."""
    log = logging.getLogger("%s.%s" % (__name__, "TaskReceipt"))
    
    def __init__(self, name, task_dir, error=None):
        self.name = name 
        self.error = error
        self.task_dir = task_dir
        self.report_on = False
    
    @classmethod
    def is_receipt_file(cls, path):
        _, file_name = os.path.split(path)
        return file_name == "receipt.yaml"

    @classmethod
    def maybe_load(cls, path):
        """Loads the receipt at ``path`` if it is a recipt file.
        
        Returns None or the :class:`TaskReceipt`.
        """
        
        if not cls.is_receipt_file(path):
            return None
            
        cls.log.debug("Reading TaskReceipt {path}".format(path=path))
        with open(path, "r") as f:
            data = yaml.load(f)
        
        receipt = TaskReceipt(data["name"], data["task_dir"])
        for k, v in data.iteritems():
            if hasattr(receipt, k):
                setattr(receipt, k, v)
            else:
                cls.log.debug("Unkown property {k} in receipt file "\
                    "{path}".format(k=k, path=path))
        return receipt
        
    def write(self):
        """Writes the task receipt to the current task_dir."""
        
        assert os.path.isdir(self.task_dir)
        out_file = os.path.join(self.task_dir, "receipt.yaml")
        self.log.debug("Writing task receipt for {self.name} to "\
            "{out_file}".format(self=self, out_file=out_file))

        with open(out_file, "w") as f:
            yaml.dump(vars(self), stream=f, default_flow_style=False)
        return out_file