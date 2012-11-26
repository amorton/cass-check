"""Tasks that collect raw details from the node."""
import logging
import os
import shutil

import task

# ============================================================================
# 

class LogCollectionTask(task.Task):
    log = logging.getLogger("%s.%s" % (__name__, "LogCollectionTask"))
    
    name = "collect-logs"
    description = "Collect logs"


    def _do_task(self):
        
        # only copy files that start with this
        matches = ["system.log", "gc-"]
        root, _, files = os.walk("/var/log/cassandra").next()
        
        for f in files:
            for match in matches:
                if f.startswith(match):
                    src = os.path.join(root, f)
                    dest = os.path.join(self.task_dir, f)
                    self.log.debug("Copying {src} to {dest}".format(
                        src=src, dest=dest))
                    shutil.copy2(src, dest)
                    break

        return 

# ============================================================================
# 

class ProxyHistogramsCollectionTask(task.Task):
    log = logging.getLogger("%s.%s" % (__name__, 
        "ProxyHistogramsCollectionTask"))
    
    name = "collect-proxy-histograms"
    description = "Collect proxy histograms"


    def _do_task(self):
        
        cmd = "/Users/aaron/servers/cassandra/apache-cassandra-1.1.6/bin/nodetool -h localhost proxyhistograms"
        self._write_output(self._exec_cmd(cmd))
        return 
