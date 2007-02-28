#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  28-9-2006
#      REVISION:  ---
#===============================================================================#
import sys
import cmd
import os
from os.path import expanduser, join, basename, exists, isdir, isfile
import glob
import threading

class submitThread(threading.Thread):
    """\
    """

    remoteQueueServer = ''
    remoteArchiveServer = ''

    def __init__(self, cmd, name = 'SubmitThread'):
        self.cmd = cmd
        threading.Thread.__init__(self, name = name)
        self.setDaemon(True)
        self.start()

    def run(self):
        print self.cmd

    def queue(self, dryrun = False):
        """\
        get queued gjf file from queue spool
        """
        if remoteQueueServer == '':
        # get from local queue directory
            
    
    def archive(self):
        """\
        archive log files.
        """

    def submit(self):
        """\
        """
         

class Interpreter(cmd.Cmd):
    """
    interactive control gaussian job queues
    """

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "qsg>> "
        self.intro = """\
***********************************************
This is gaussian job queues Processor; type 
  <ctrl>-d (UNIX-only) or 'quit' to quit, 
  <TAB> (UNIX-only)for command or argument 
  completion, '?' or 'help' for help.
***********************************************"""
        self.queue_dir = "~/gjf/queue"
        self.work_dir = "~/gjf/work"
        self.error_dir = "~/gjf/error_done"
        self.norm_dir = "~/gjf/norm_done"
        self.servers = {}
    
    def do_add_server(self, server):
        """add a server into server list"""
        self.servers.append(server)
   
    def status(self):
        """ show status"""
        for f in servers.keys():
             print "%s:\t%s" %(f, servers[f])
         
    def do_queue(self, arg):
        """list queues"""
        queues = glob.glob(join(expanduser(self.queue_dir), "*.gjf"))
        if queues:
            for f in queues:
                print basename(f)
        else:
            print "No queued jobs"

    def do_summary(self, server):
        """summary current running job"""
        print "summary:"

    def do_start(self, server):
        """start gaussian queues on remote server"""
        cmd = "ssh %s screen -S qsg  -d -m sleep 80" % server
        thread = SubmitThread(cmd)

    def do_stop(self, server):
        """stop gaussian queues"""
        cmd = "ssh server screen -S qsg  -X quit"
        res = os.popen(cmd).read().strip()
        self.servers[server] = 'idle'

    def do_kill(self, server):
        """kill current job running on server"""
        cmd = "ssh server pkill -f l*.exe"
        res = os.popen(cmd).read().strip()

    def do_quit(self, arg):
        """to quit, type quit"""
        return True

    def do_EOF(self, arg):
        return True
    do_q = do_exit = do_quit


def main(argv = None):
    """
    """
    if argv == None: argv = sys.argv


    submit=submitThread('test')
    submit.run()
    qsg = Interpreter()
    qsg.cmdloop()
#------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv)
