"""Tasks that collect raw details from the node."""
import logging
import shutil

import task

class LogCollectionTask(task.Task):
    log = logging.getLogger("%s.%s" % (__name__, "LogCollectionTask"))
    
    name = "collect-logs"
    description = "Collect logs"


    def _do_task(self):
        shutil.copytree("/var/logd/cassandra", self.task_dir)

        return 
          