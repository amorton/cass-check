"""Base for commands"""

import argparse
import copy
import logging
import os.path

import pkg_resources

from mako.template import Template

import file_util, resources, task

# ============================================================================
# 

class SubCommand(object):
    """Base for all SubCommands that can be called on the command line. 

    :cls:`SubCommand` instances are created by the script entry point and 
    their ``__call__`` method called. 
    """

    name = None
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = None
    """Command line help for the Sub Command."""

    description = None
    """Command line description for the Sub Command."""


    @classmethod
    def add_sub_parser(cls, sub_parsers):
        """Called to add a parser to ``sub_parsers`` for this command. 

        Sub classes may override this method but pass the call up to ensure 
        the sub parser is created correctly. 

        A default ``func`` argument is set on the :cls:``ArgumentParser`` to 
        point to the constructor for the SubCommand class.

        Returns the :cls:`argparser.ArgumentParser`.
        """
        
        assert cls.name, "command_name must be set."

        parser = sub_parsers.add_parser(cls.name,
            help=cls.help or "No help", 
            description=cls.description or "No help", 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.set_defaults(func=cls)
        return parser
    
    def __call__(self):
        """Called to execute the SubCommand.
        
        Must return a tuple of (rv, msg). Rv is returned as the script exit 
        and msg is the std out message.
        
        Must be implemented by sub classes.
        """
        raise NotImplementedError()

# ============================================================================
# 

class NoopCommand(SubCommand):
    """Testing no op."""

    name = "noop"
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = "some help"
    """Command line help for the Sub Command."""

    description = "some desc"
    """Command line description for the Sub Command."""


    def __init__(self, args):
        pass
        
    def __call__(self):
        """Just return a no op message."""
        return (0, "no op")

# ============================================================================
# 

class CheckCommand(SubCommand):
    """Command that runs all the parts of the checkup."""

    name = "check"
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = "Runs a full checkup."
    """Command line help for the Sub Command."""

    description = "Runs a full checkup."
    """Command line description for the Sub Command."""


    def __init__(self, args):
        self.log = logging.getLogger("%s.%s" % (__name__, "CheckCommand"))
        self.args = args
        
    def __call__(self):
        """Runs the command."""
        
        # commands to run and the order to run them in. 
        ep_names = ["collect"]
        cmds = []
        for ep_name in ep_names:
            eps = pkg_resources.iter_entry_points(resources.COMMAND_EP_GROUP,
                name=name)
            if not eps or len(eps) > 1:
                return RuntimeError("Found {len} end points for group "\
                    "{group} and name {name}".format(len=len(ep), 
                    group=resources.COMMAND_EP_GROUP, name=ep_name))
            cmds.append(eps[0].load(copy.copy(args)))
        self.log.info("Running commands {cmds}".format(cmds=cmds))
        
        out = []
        for cmd in cmds:
            self.log.debug("Starting command {cmd}".format(cmd=cmd))
            out.append(cmd())
        
        return (0, "\n".join(out))

# ============================================================================
# 

class ReportCommand(SubCommand):
    """Build a report on the output from tasks."""

    name = "report"
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = "Reports on the task output."
    """Command line help for the Sub Command."""

    description = "Reports on the task output."
    """Command line description for the Sub Command."""


    def __init__(self, args):
        self.log = logging.getLogger("%s.%s" % (__name__, "ReportCommand"))
        self.args = args

        self.report_dir = os.path.join(self.args.check_dir, self.name)
        file_util.ensure_dir(self.report_dir)

    def __call__(self):
        """Runs the command."""
        
        # Collect all of the task receipts that need to be reported on.
        # args.check_dir will be the top level dir 
        receipts = []
        for root, dirs, files in os.walk(self.args.check_dir):
            paths = (
                os.path.join(root, f)
                for f in files
            )
            for path in paths:
                receipt = task.TaskReceipt.maybe_load(path)
                if receipt and receipt.report_on:
                    receipts.append(receipt)
        self.log.debug("Reporting on receipts {receipts}".format(
            receipts=receipts))
        
        # Build a list of all the files we want to copy and associate 
        # this with the receipt. 
        receipt_files = {}
        for receipt in receipts:            
            root, _, files in os.walk(receipt.task_dir).next()
            paths = (
                os.path.join(root, f)
                for f in files
            )
            
            # Exclude the receipt files. 
            copy_files = [
                path
                for path in paths
                if not task.TaskReceipt.is_receipt_file(path)
            ]
            self.log.debug("For task {receipt.task_name} has files "\
                "{files}".format(receipt=receipt, files=files))
            receipt_files[receipt] = files
        
        self.log.info("Building report in {self.report_dir}".format(
            self=self))
        report_file = self._write_report(receipt_files)
        
        out = [
            "Wrote report to {report_file}".format(report_file=report_file)
        ]
        return (0, "\n".join(out))
    
    def _write_report(self, receipt_files):
        """Writes the report to disk for the ``receipt_files`` map of 
        :class:`task.TastReceipt` to list of file paths. 
        """
        
        # Render the report
        
        template = Template(text=pkg_resources.resource_string(
            "cass_check", "templates/report.mako"))
        index_path = os.path.join(self.report_dir, "index.html")
        self.log.info("Writing report index to {index_path}".format(
            index_path=index_path))
        with open(index_path, "w") as f:
            f.write(template.render(receipt_files=receipt_files))
            
        # copy assets
        for asset_name in pkg_resources.resource_listdir("cass_check", 
            "assets/"):
            
            res_name = "assets/{asset_name}".format(asset_name=asset_name)
            dest = os.path.join(self.report_dir, res_name)
            self.log.info("Copying report asset {asset_name} to "\
                "{dest}".format(asset_name=asset_name, dest=dest))
                
            with pkg_resources.resource_stream("cass_check", res_name) as src:
                file_util.ensure_dir(os.path.dirname(dest))
                with open(dest, "w") as f:
                    f.write(src.read())
        
        return index_path
        

# ============================================================================
# 

class TaskRunningCommand(SubCommand):
    """A base for commands that run tasks, like collection."""

    name = ""
    """Command line name for the Sub Command.

    Must be specified by sub classes.
    """

    help = ""
    """Command line help for the Sub Command."""

    description = ""
    """Command line description for the Sub Command."""
    
    entry_point_group = ""
    """Advertised entry point group to get tasks from for this command."""

    def __init__(self, args):
        self.args = args
        
    def __call__(self):
        """"""
        
        # Update things before creating all the tasks
        self._on_before_tasks()
        
        # create all the tasks
        tasks = []
        self.log.debug("Loading entry points from group {group}".format(
            group=self.entry_point_group))
        for ep in pkg_resources.iter_entry_points(self.entry_point_group):
            # Tasks share the same args instance the command has.
            tasks.append(ep.load()(self.args))
        self.log.info("Running tasks {tasks}".format(tasks=tasks))
        
        # Run each task
        for task in tasks:
            self.log.debug("Running task {task.name}".format(task=task))
            task_dir = None
            try:
                task_dir = task()
            except (Exception) as e:
                if self.args.fail_fast:
                    raise
                self.log.warn("Error from task {task.name}".format(task=task),
                    exc_info=True)
                task.receipt.error = e
            
            task.receipt.write()
            self.log.info("Task {task.name} generated output in "\
                "{task_dir}".format(task=task, task_dir=task_dir))
        
        return (0, self._describe_receipts(tasks))
        
    def _on_before_tasks(self):
        """Called before the tasks are created for the command. 
        
        Changes to the args should be made here. For example setting the 
        output dir for this command.
        """
        
        # update the output dir 
        orig_check_dir = self.args.check_dir
        self.args.check_dir = os.path.abspath(os.path.join(
            self.args.check_dir, self.name))
        file_util.ensure_dir(self.args.check_dir)
        
        self.log.debug("For command {command.name} set check_dir to "\
            "{command.args.check_dir}".format(command=self))
        return
    
    def _describe_receipts(self, tasks):
        """Build a string to describe all the ``tasks`` that ran.
        
        Uses the task receipt.
        """
        
        builder = []
        append = builder.append
        
        append("Tasks run by command {s.name}:".format(s=self))
        for task in tasks:
            result = "Error" if task.receipt.error else task.receipt.task_dir
            append("\t{receipt.name:<30} {result}".format(receipt=task.receipt, 
                result=result))
        return "\n".join(builder)
# ============================================================================
# 

class CollectCommand(TaskRunningCommand):
    """Run tasks categorised as collect tasks."""
    log = logging.getLogger("%s.%s" % (__name__, "CollectCommand"))
        
    name = "collect"
    """Command line name for the Sub Command.
    """

    help = "Collect raw details from the node."
    """Command line help for the Sub Command."""

    description = ""
    """Command line description for the Sub Command."""

    entry_point_group = "cass_check.tasks.collection"

        
