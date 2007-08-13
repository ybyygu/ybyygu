#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  simple-gaussian-qsub.py (sgq.py)
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo (ybyygu) 
#         EMAIL:  win.png@gmail.com
#       LICENCE:  GPL version 2 or upper
#       CREATED:  2007-07-28
#       UPDATED:  2007-08-13 20:45
#===============================================================================#
import sys
import cmd
import os
from os.path import expanduser, join, basename, exists, isdir, isfile
import re
import glob
import socket
import signal
import logging

#===============================================================================#
#
#  Constants and global behaviors
#
#===============================================================================#

__version__ = "0.3"
cmd_pgrep = "/usr/bin/pgrep"
cmd_ps = "/bin/ps"

#===============================================================================#
#
#  Functions
#
#===============================================================================#

def detect_working_directory():
    """
    figure out the most possible working directory of gaussian program
    """
    # select processes of g03 or g98 owned by current user
    out = os.popen('%s -u $USER "g03|g98"' % cmd_pgrep).read().strip()
    if not out:
        return None
    # maybe more than one, so splitted into dict
    pids = out.split()
    for pid in pids:
        fenv = "/proc/" + pid + "/environ"
        txt = open(fenv).read()
        p = re.compile('\x00PWD=([^\x00]+)').search(txt)
        if p:
            return p.group(1)
        else:
            return None

def detect_log_files(directory):
    """
    figure out possible gaussian log files from directory
    """
    return glob.glob(join(directory, "*.log")) + glob.glob(join(directory, "*.out"))

def sort_log_files(files):
    """
    sort log files by modify time
    """
    def log_cmp(x, y):
        x = os.stat(x)[ST_MTIME]
        y = os.stat(y)[ST_MTIME]
        return cmp(x,y)

    files.sort(log_cmp)

def summary_log(path):
    """
    summary one gausian log file
    """
    pass

def summary_gaussian(where=None):
    """
    Make a summary of the gaussian log file
    """
    files = []
    ###
    # if where is None, try to figure out one
    #
    if where == None:
        dir = detect_working_directory()
        if not dir:
            print "No working gaussian log file found."
            return
        else:
            files = detect_log_files(dir)
            if not files:
                print "No log files found in your working directory."
                return
            else:
                sort_log_files(files)
                for f in files:
                    summary_log(f)

#===============================================================================#
#
#  Classes
#
#===============================================================================#

###
# log-restart
#
class vector:
    """
    Class that represents a atom space vector.
    """    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        """
        return the length of vector
        """
        return sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def distance(self, avector):
        """
        return the distance of the two vectors
        """
        return sqrt((self.x - avector.x)**2 + (self.y - avector.y)**2 + (self.z - avector.z)**2)

    def dot(self, avector):
        """
        dot product
        """
        return self.x * avector.x + self.y * avector.y + self.z * avector.z

    def cross(self, avector):
        """
        cross product
        """
        nx = self.y * avector.z - self.z * avector.y
        ny = self.z * avector.x - self.x * avector.z
        nz = self.x * avector.y - self.y * avector.x
        return vector(nx, ny, nz)

    def __sub__(self, avector):
        x = self.x - avector.x
        y = self.y - avector.y
        z = self.z - avector.z
        return vector(x, y, z)

    def angle(self, vb, vc):
        """
        return the angle between the tree vector points: va(self), vb, vc
        """
        vba = self - vb
        vbc = vc - vb
        arg = acos(vba.dot(vbc)/vba.length()/vbc.length()) * 180.0 / 3.1415926
        return arg

    def torsion(self, vb, vc, vd):
        """
        return the torsion angle between the four vector points: va, vb, vc, vd
        """
        vba = self - vb
        vbc = vc - vb
        vcb = vb - vc
        vcd = vd - vc
        vbaxbc = vba.cross(vbc)
        vcbxcd = vcb.cross(vcd)
        arg = acos(vbaxbc.dot(vcbxcd) / vbaxbc.length() / vcbxcd.length()) * 180.0 /3.1415926
        
        if vba.cross(vbc).dot(vcd) > 0:
            sign = -1
        else:
            sign = 1
        return arg * sign

class atoms:
    def __init__(self):
        self.atoms = []

    def addAtom(self, x, y, z):
        atom = vector(x, y, z)
        self.atoms.append(atom)
    
    def bond(self, id1, id2):
        """
        return the length of the bond specified by the two atom index numbers
        """
        return self.atoms[id1].distance(self.atoms[id2])

    def angle(self, id1, id2, id3):
        """
        return the angel of the tree atoms specified by atoms index
        """
        return self.atoms[id1].angle(self.atoms[id2], self.atoms[id3])

    def torsion(self, id1, id2, id3, id4):
        """
        return the torsion angle of for atoms specified by atoms index
        """
        return self.atoms[id1].torsion(self.atoms[id2], self.atoms[id3], self.atoms[id4])

class gaussianLogParser:
    """
    things related to gaussian log file
    """
    def __init__(self, filename):
        try:
            self.fp = open(filename)
        except IOError:
            print "Cannot open %s" % filename
            raise

        self.cur_pos = 0
        self.cur_step = 0
        self.start_pos = 0
        self.start_step = 0
        self.end_pos = 0
        self.end_step = 0

        fp.seek(0,2)
        self._fp_size = fp.tell()

    def getxyz_str(self, opt_step = -1):
        pass

    def getxyz(self, opt_step = -1):
        xyz = self.getxyz_str(opt_step)

    def move2opt_step(self, opt_step = -1, strollsize = 10000):
        """
        search and locate the opt_step position
        """

        if opt_step == 0:
            fp.seek(0, 0)
            return True

        rex = re.compile(r'^ Step number\s+(\d+)\s+out of')
        key = ' Step number '

        if self.start_step == 0:
            self.fp.seek(0,0)
            if self._move_forward(key):
                line = self.fp.readline().strip()
                if line and rex.match(line):
                    self.start_step = int(rex.search(line).group(1))
                    self.start_pos = self.fp.tell()
                else:
                    raise
            else:
                raise
            if opt_step == 1:
                self.fp.seek(self.cur_pos, 0)
                return True

        if self.end_step == 0:
            self.fp.seek(0, 2)
            if self._move_backward(key):
                line = self.fp.readline().strip()
                if line and rex.match(line):
                    self.end_step = int(rex.search(line).group(1))
                    self.end_pos = self.fp.tell()
                else:
                    raise
            else:
                raise
            if opt_step == -1:
                self.fp.seek(self.cur_pos, 0)
                return True

        # minus step number mean step backwardly from the end
        if opt_step < 0:
            opt_step = opt_step + self.end_step -1
        
        if opt_step >0 and opt_step < self.end_step:
            pos = float(self.opt_step - self.start_step) / (self.end_step - self.start_step) \
                  * (self.end_pos - self.start_pos) + self.start_pos
            pos = int(pos - 2)
            self.fp.seek(pos, 1)

            if self._move_forward(key):
                line = self.fp.readline().strip()
                if line and rex.match(line):
                    self.cur_step = int(rex.search(line).group(1))
                    if self.cur_step == opt_step:
                        self.cur_pos = self.fp.tell()
                        return True
                    else:
                        self.move2opt_step(opt_step)
            # TODO
        else:
            print "The step number is invalid."
            return 1
            
    def _move_backward(self, search_key, strollsize = 10000):
        """\
        move backwardly by search_key, return true if successful, else return false
        """
        # search_key sould be less than 100 bytes 
        while self.fp.tell() >= 0:
            fp.seek(-strollsize, 1)
            pos = fp.tell()
            # we have to read a bit more 
            buffer = fp.read(strollsize + 100)
            # restore position
            fp.seek(pos, 0)
             
            pos_key = buffer.find(key)
            if pos_key >=0:
                self.cur_pos = pos + pos_key -1
                fp.seek(self.cur_pos)
                return True
        return False

    def _move_forward(self, search_key, strollsize = 10000):
        """\
        move forwardly by search_key, return true if successful, else return false
        """
        # search_key sould be less than 100 bytes
        # strollsize should be more than 100 bytes
        while self.fp.tell() <= self._fp_size:
            pos = self.fp.tell()
            # we have to read a bit more 
            buffer = fp.read(strollsize + 100)
            # restore position
            self.fp.seek(-100, 1)
            
            pos_key = buffer.find(key)
            if pos_key >=0:
                self.cur_pos = pos + pos_key -1
                self.fp.seek(self.cur_pos, 0)
                return True
        return False

###
# simple-gaussian-qsub
#
class simpleConf(object):
    """
    simple config file
    """
    def __init__(self, path):
        self._path = path
        self._keys = []
        self._data = {}
        self._read()

    def __getattr__(self, attr):
        """
        """
        if not attr.startswith("_"):
            if attr in self.__dict__["_keys"]:
                return self.__dict__["_data"][attr]
            else:
                try:
                    return self.__dict__[attr]
                except:
                    return ""
        else:
            try:
                return self.__dict__[attr]
            except:
                return ""

    def __setattr__(self, name, value):
        """
        """
        if not name.startswith("_"):
            if not self.__dict__["_data"].has_key(name):
                log.debug("set new attr %s with data %s" % (name, value))
                if value:
                    self.__dict__["_keys"].append(name)
                    self.__dict__["_data"][name] = str(value)
                    self._write()
            elif self.__dict__["_data"][name] !=value:
                log.debug("set attr %s with data %s" % (name, value))
                if not value:
                    log.debug("remove empty attr %s" % name)
                    del self.__dict__["_data"][name]
                    self.__dict__["_keys"].remove(name)
                else:
                    self.__dict__["_data"][name] = str(value)
                self._write()
        else:
            object.__setattr__(self, name, value)

    def _read(self):
        """
        read data from disk file
        """
        lines = ""
        try:
            lines = open(self._path, "rb").readlines()
        except IOError, x:
            log.warning("%s: %s" % (self._path, x.strerror))
            return False
 
        self.__dict__["_keys"] = []
        self.__dict__["_data"] = {}
        for line in lines:
            line = line.strip()
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key[0] == '#':
                continue
            self.__dict__["_keys"].append(key)
            self.__dict__["_data"][key] = value
            #log.debug("read attr %s with data %s from %s" % (key, value, self._path))

    def _write(self):
        """
        write to disk file
        """
        try:
            # mkdir if necessary
            dirname = os.path.dirname(self._path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fp = open(self._path, "w")
        except IOError, x:
            sys.exit("write %s: %s" % (self._path, x.strerror))

        for key in self._keys:
            value = self._data[key]
            fp.write("%s=%s\n" % (key, value))
        fp.close()

    def refresh(self):
        """
        refresh data from disk
        """
        if os.path.exists(self._path):
            self._read()

class sgqConf(simpleConf):
    """
    configuration based on .sgq-[code].conf
    """
    def __init__(self, code=""):
        if code:
            code = "-" + code
        self._code = code

        path = os.path.join(os.environ["HOME"], ".regvar%s" % self._code)
        simpleConf.__init__(self, path)

        if not self.sgqRootDir:
            self.sgqRootDir = os.path.join(os.environ["HOME"], "gjf%s" % self._code)
        else:
            self.sgqRootDir = self._expandPath(self.sgqRootDir)
        if not self.sgqQueueDir:
            self.sgqQueueDir = os.path.join(self.sgqRootDir, "queue")
        else:
            self.sgqQueueDir = self._expandPath(self.sgqQueueDir)
        if not self.sgqWorkDir:
            self.sgqWorkDir = os.path.join(self.sgqRootDir, "work")
        else:
            self.sgqWorkDir = self._expandPath(self.sgqWorkDir)
        if not self.sgqArchiveDir:
            self.sgqArchiveDir = os.path.join(self.sgqRootDir, "ARCHIVE")
        else:
            self.sgqArchiveDir = self._expandPath(self.sgqArchiveDir)
        if not self.sessionID:
            hostname = socket.gethostname()
            user = os.getenv('USER')
            self.sessionID = "%s@%s%s" % (user, hostname, self._code)

        # regvar
        if not self.groot or not self.gcmd or not self.gscratch:
            self.configure()
            return
        self.groot = self._expandPath(self.groot)
        self.gscratch = self._expandPath(self.gscratch)

    def _expandPath(self, path):
        path = os.path.expanduser(path)
        return os.path.expandvars(path)

    def validateConf(self):
        """
        validate conf settings; return True if success.
        """
        profile = os.path.join(self.groot, self.gcmd, "bsd/%s.profile" % self.gcmd)
        if os.path.exists(profile):
            return True
        return False

    def dump(self):
        """
        dump the content of the conf file
        """
        print open(self._path).read().strip()
    
    def configure(self):
        """
        generate .regvar configuration file by answer some simple questions
        """

        leader = "configure: "
        cont = " " * len(leader)
        # question 0: where is your gaussian root directory?
        groot = self.groot
        gcmd = self.gcmd

        if os.environ.has_key("g03root"):
            groot = os.environ["g03root"]
            gcmd = "g03"
        elif os.environ.has_key("g98root"):
            groot = os.environ["g98root"]
            gcmd = "g98"
        else:
            groot = "/export/home/gauss"
            gcmd = "g03"
        ans = raw_input(leader + "Where is your g03/g98's root directory? (%s)" % groot)
        if ans.strip():
            groot = ans
        # question 1: where is your gaussian scratch directory?
        gscratch = "/tmp"
        if os.environ.has_key("GAUSS_SCRDIR"):
            gscratch = os.environ["GAUSS_SCRDIR"]
        elif os.path.exists(os.path.join(groot, "scratch")): # /groot/scratch
            gscratch = os.path.join(groot, "scratch")

        ans = raw_input(leader + "Where is your gaussian scratch diretory? (%s)" % gscratch)
        if ans.strip():
            gscratch = ans
        test_dir = os.path.join(gscratch, "test_test")

        try:
            os.makedirs(test_dir)
            os.rmdir(test_dir)
        except OSError:
            print "scratch directory is not writeable. You need correct this error."
        # final test
        self.groot = groot
        self.gcmd = gcmd
        self.gscratch = gscratch
        if not self.validateConf():
            print leader + "WARNING! It seems your setting does not work. I cannot find gaussian profile." 
            print cont + "Did your gaussian package install correctly?"
            # remove unacceptable settings
            self.groot = ""
            self.gcmd = ""
            self.gscratch = ""
            sys.exit(1)

        # remote server
        remote_server = ""
        ans = raw_input(leader + "Do you want to use a remote queue/archive server? (N/y)")
        if ans.strip().lower() == "y":
            print leader + "IN ORDER TO USE THIS, YOU NEED A PASSWORDLESS SSH CONNECTION TO THE REMOTE SERVER."
            print cont + "For details, please google \"passwordless ssh\", and follow the instructions."
            ans = raw_input(leader + "Now, please input your remote queue server's IP address or name. ")
            if ans.strip():
                remote_server = ans

        if remote_server:
            self.remoteQueueDir = remote_server + ":" + self.sgqQueueDir
            self.remoteArchiveDir = remote_server + ":" + self.sgqArchiveDir
        print leader + "Please make sure below lines exactly match your need."
        print cont + "Or you can directly edit [ %s ]." % self._path
        print "[ Conf-Begin ]".center(72, '-')
        # write into regvar file
        self.dump()
        print "[ Conf-End ]".center(72, '-')

        print leader + "Configuration finished."

class sgqJob:
    """
    wrapper for gaussian job file (remote or local)   
    """
    def __init__(self, path, host=""):
        """
        @path: path to a gjf file
        @host: could be a remote host
        """
        self.path = path
        self.host = host
        self.name = os.path.basename(path)
        self.content = ""
        self.description = "Unknown"

        # parse gjf file, fill content and description
        self._parse()
    
    def _parse(self):
        """
        parse the content of gjf file
        """
        if self.host:
            cmd = "ssh %s 'cat %s'" % (self.host, self.path)
        else:
            cmd = "cat %s" % self.path
    
        i, o, e = os.popen3(cmd)
        errstr = e.read()
        if errstr:
            log.error("%s: %s" % (cmd, errstr.strip()))
            return

        self.content = o.read()
        rex = re.compile(r'%chk=(.$)')

        # human readable job description
        if self.host:
            self.description = "%s from %s" % (self.name, self.host)
        else:
            self.description = "%s from local" % self.name

    def remove(self):
        """
        remove self from disk
        """
        if self.host:
            cmd = "ssh %s 'rm -f %s'" % (self.host, self.path)
        else:
            cmd = "rm -f %s" % (self.path)

        i, o, e = os.popen3(cmd)
        errstr = e.read()
        if errstr:
            log.error("Failed to remove job: %s" % errstr.strip())

    def sign(self):
        """
        """
        self.signature = code

class sgqQueue:
    """
    job queue
    """
    def __init__(self):
        # directories
        self.localQueueDir = conf.sgqQueueDir
        if conf.remoteQueueDir:
            host, path = conf.remoteQueueDir.split(":", 1)
            self.remoteHost = host
            self.remoteQueueDir = path

        # queues
        self.localQueue = []
        self.remoteQueue = []
        self.signedLocalQueue = []
        self.signedRemoteQueue = []

        self.queuedJob = None
        self.signature = socket.gethostname()

        self._update()

    def _parseDirectory(self, path, host=""):
        """
        path should be a directory, remote or local
        """
        queue = []

        # local or remote
        if host:
            cmd = "ssh %s 'cd %s && /bin/ls *.gjf *.com 2>/dev/null'" % (host, path)
        else:
            cmd = "cd %s && /bin/ls *.gjf *.com 2>/dev/null" % path

        i, o, e = os.popen3(cmd)
        errstr = e.read()
        if errstr:
            log.warning("cmd [%s] failed: %s" % (cmd, errstr.strip()))
        else:
            out = o.read().strip()
            if not out:
                return []
            lst = out.split("\n")
            for l in lst:
                log.debug("found job %s from %s" % (l, path))
                new_path = os.path.join(path, l)
                queue.append(sgqJob(new_path, host))
        return queue

    def _updateLocal(self):
        """
        update queue from files in queueDir
        """
        if not os.path.exists(self.localQueueDir):
            log.warning("Queue directory does not exist. make it.")
            os.makedirs(self.queueDir)
            self.localQueue = []
            return 

        log.debug("parse local queue jobs.")
        self.localQueue = self._parseDirectory(self.localQueueDir)
        log.debug("get %s jobs from local queue" % len(self.localQueue))

        # look into local path signed for this node
        log.debug("parse signed local queue jobs.")
        path = os.path.join(self.localQueueDir, self.signature)
        if not os.path.isdir(path):
            log.debug("No signed job for %s." % (self.signature))
            return
        queue = self._parseDirectory(path)

        # remove empty directy
        if not queue:
            log.debug("remove empty signed queue for %s." % self.signature)
            try:
                os.rmdir(path)
            except:
                log.warning("failed to remove signed directory.")
        self.signedLocalQueue = queue
        log.debug("get %s signed job for %s" % (len(self.signedLocalQueue), self.signature))
    
    def _updateRemote(self):
        """
        update queue from remote host
        """
        if not self.remoteQueueDir:
            log.debug("No remote queue defined.")
            self.remoteQueue = []
            return

        log.debug("parse remote host %s" % self.remoteHost)
        self.remoteQueue = self._parseDirectory(self.remoteQueueDir, self.remoteHost)
        log.debug("get %s jobs from remote queue %s" % (len(self.remoteQueue), self.remoteHost))

        # look into path signed for this node
        path = os.path.join(self.remoteQueueDir, self.signature)
        log.debug("parse signed remote queue for %s" % self.signature)
        self.signedRemoteQueue = self._parseDirectory(path, self.remoteHost)
        log.debug("get %s jobs from signed remote queue %s" % (len(self.signedRemoteQueue), self.remoteHost))

    def _update(self):
        """
        update queue directories, return when one queue is not empty.
        """
        self._updateLocal()

        if self.signedLocalQueue:
            self.queuedJob = self.signedLocalQueue.pop(0)
            return
        if self.localQueue:
            self.queuedJob = self.localQueue.pop(0)
            return

        self._updateRemote()
        if self.signedRemoteQueue:
            self.queuedJob = self.signedRemoteQueue.pop(0)
            return
        if self.remoteQueue:
            self.queuedJob = self.remoteQueue.pop(0)
            return
        # finally nothing got
        self.queuedJob = None
    
    def _listLocal(self):
        """
        list local queue
        """
        self._updateLocal()
        if self.signedLocalQueue:
            print (" signed local queue for %s" % self.signature).center(72, "-")
            print "\n".join([" " + q.name for q in self.signedLocalQueue])
        if self.localQueue:
            print " local queue ".center(72, "-")
            print "\n".join([" " + q.name for q in self.localQueue])


    def _listRemote(self):
        """
        list remote queue
        """
        self._updateRemote()
        if self.signedRemoteQueue:
            print (" signed remote queue for %s" % self.signature).center(72, "-")
            print "\n".join([" " + q.name for q in self.signedRemoteQueue])
        if self.remoteQueue:
            print " remote queue ".center(72, "-")
            print "\n".join([" " + q.name for q in self.remoteQueue])

    def list(self):
        """
        list queued jobs; for interactive use
        """
        self._listLocal()
        self._listRemote()

    def pop(self, dry=False):
        """
        pop up a file from job queue, return file content and file name
        """
        self._update()
        if self.queuedJob:
            # destroy queued file, use job.content to get file content
            if not dry:
                self.queuedJob.remove()
            return self.queuedJob
        return None

    def isEmpty(self):
        self._update()
        if self.queuedJob:
            return False
        else:
            return True

class sgqArchive:
    """
    archive finished jobs
    """
    def __init__(self, work_dir, dest_dir, host=""):
        """
        """
        self.workDir = work_dir
        self.archiveDir = dest_dir
        self.host = host

    def archive(self):
        """
        """
        # figure out a name based the .log file under workDir
        os.chdir(self.workDir)
        lst = glob.glob("*.log")
        if lst:
            lst.sort()
        else:
            log.warning("No log file found in work directory.")
            return

        # check gaussian log status
        glog = lst[-1]
        path = os.path.join(self.workDir, glog)
        try:
            fp = open(path, "rb")
            fp.seek(-500, 2)
            res = fp.read().find("Normal termination")
            fp.close()
        except IOError, x:
            log.error("Failed to parse gaussian log: %s" % x.strerror.strip())

        if res >=0:
            status = "norm_done"
        else:
            status = "error_done"

        # generate archive directory name
        import time
        import random
        uid = ''.join(random.sample('0123456789', 8))
        dir = time.strftime("%Y-%m%d-%H%M") + "@%s@" % uid + glog[:-4]

        # make necessary directories
        path = os.path.join(self.archiveDir, status, dir)
        if self.host:
            cmd = "ssh %s 'mkdir -p %s'" % (self.host, path)
        else:
            cmd = "mkdir -p %s" % path
        print path
        i, o, e = os.popen3(cmd)
        errstr = e.read()
        if errstr:
            log.warning("%s: %s" % (cmd, errstr.strip()))
            return False

        # rsync is a great tool, so use rsync to do the real work
        # make sure place_from end with "/"
        place_from = os.path.join(self.workDir, "")
        if self.host:
            place_to = self.host + ":" + path
        else:
            place_to = path
        cmd = "cd %s && rsync -e ssh --quiet --dirs --times --compress ./ %s && rm -f ./*" % (place_from, place_to) 
        i, o, e = os.popen3(cmd)
        errstr = e.read()
        if errstr:
            log.warning("%s: sgqArchive: %s" % (cmd, errstr.strip()))

class statusConf(simpleConf):
    """
    wrapper for queue status 
    """
    def __init__(self, code=""):
        if code:
            code = ".status.sgq:%s" % code
        else:
            code = ".status.sgq"
        path = os.path.join(os.path.expandvars("$HOME"), code)
        simpleConf.__init__(self, path)

    def clear(self):
        """
        """
        self.shouldStop = ""
        self.activePID = ""
        self.paused = ""

class sgqSubmit:
    """
    submit jobs, enter into submit loop
    """
    def __init__(self, jobQueue, warmup_job_path=None):
        if conf.remoteArchiveDir:
            host, dir = conf.remoteArchiveDir.split(":", 1)
        else:
            host = ""
            dir = conf.sgqArchiveDir
        self.jobArchive = sgqArchive(conf.sgqWorkDir, dir, host)
        self.jobQueue = jobQueue
        self.warmup_job_path = warmup_job_path
    
    def submitGaussian(self, job):
        """
        build runnable script and then submit it
        """
        scratch_dir = os.path.join(conf.gscratch, conf.sessionID)
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)
        profile = os.path.join(conf.groot, conf.gcmd, "bsd/%s.profile" % conf.gcmd)
        if not os.path.exists(profile):
            log.error("%s does not exists." % profile)
            log.error("Did your gaussian package setup correctly?")

        script = os.path.join(conf.sgqWorkDir, "run")
        log.debug("build runable gaussian script.")
        try:
            fp = open(script, "wb")
            fp.write("#! /bin/sh\n")
            fp.write("export g03root=%s\n" % conf.groot)
            fp.write("export GAUSS_SCRDIR=%s\n" % scratch_dir)
            fp.write("source %s\n" % profile)
            fp.write("mkdir -p %s && cd %s\n" % (conf.sgqWorkDir, conf.sgqWorkDir))
            #  convert DOS newlines to unix format, and then submit it
            #  Sometimes, gaussian will fail to parse the gjf file when there is no  
            #+ blank line in the end of the file, so I append one.
            ## TODO:
            gauss_log = job.name[:-4] + ".log"
            fp.write("exec sed -e 's/\r$//; $G' %s | %s > %s 2> debug\n" % (job.name, conf.gcmd, gauss_log))
            fp.close()
        except IOError, x:
            log.error("%s" % x.strerror)

        # restore gjf file from content
        log.debug("restore content from job.content")
        try:
            fp = open(os.path.join(conf.sgqWorkDir, job.name), "wb")
            fp.write(job.content)
            fp.close()
        except IOError, x:
            log.error("%s" % x.strerror)

        #os.chmod(script, 0755)
        os.system("/bin/sh %s" % script)

    def loop(self):
        """
        enter submit loop
        """
        if self.warmup_job_path and os.path.isfile(self.warmup_job_path):
            job = sgqJob(self.warmup_job_path)
            log.info("get warmup_job_path with: %s" % self.warmup_job_path)
        else:
            job = self.jobQueue.pop() 
            log.info("get job from queue: %s" % job.name)
        while not commander.isShouldStop() and job.content:
            log.info("submit job: %s" % job.name)
            self.submitGaussian(job)
            log.info("archive job: %s" % job.name)
            self.jobArchive.archive()
            # next
            job = self.jobQueue.pop() 
        log.info("No more queued job. exit...")
        commander.over()

class sgqCommander:
    """
    commander send command
    """
    def __init__(self, interactive=True):
        self.jobQueue = sgqQueue()
        self.status = statusConf()
        self.interactive = interactive

    def _print(self, string):
        """
        condition print
        """
        if self.interactive:
            print string

    def pause(self):
        """
        pause queue and running job
        """
        if self.status.activePID:
            pid = int(self.status.activePID)
            self._signalAll(pid, signal.SIGSTOP)
            self.status.paused = "yes"
            return "Job was paused. Enter resume to continue."
        else:
            return "No active queue found."
    
    def isPaused(self):
        """
        check if queue is paused
        """
        if self.status.paused:
            return True
        else:
            return False

    def _subPIDS(self, pid):
        """
        return a sub processes list of pid
        """
        cmd = "/usr/bin/pgrep -P %s" % pid
        i, o, e = os.popen3(cmd)
        errstr = e.read()
        if errstr:
            log.error("failed to get sub process: %s" % errstr)
            return []
        pids = o.read().strip().split()
        return pids

    def _signalAll(self, pid, signal):
        """
        send signal to pid recursively
        """
        if not pid:
            return 
        pids = self._subPIDS(pid)
        if not pids: # if no sub processes just kill it
            try:
                log.debug("kill pid %s with signal %s" % (pid, signal))
                os.kill(int(pid), signal)
            except OSError, x:
                log.error("%s" % x.strerror)
        else: # kill sub processes recursively
            for p in pids:
                self._signalAll(p, signal)

    def _fixLostPID(self):
        """
        find out daemon process ID if PID status lost.
        """
        prog = os.path.basename(sys.argv[0])
        cmd = "%s -f python.*%s" % (cmd_pgrep, prog)
        i, o, e = os.popen3(cmd)
        err = e.read().strip()
        if err:
            log.warning("find lost PID failed: %s" % err)
            return

        out = o.read().strip()
        if out:
            pids = out.split("\n")
            me = os.getpid()
            for p in pids:
                if p != str(me):
                    self.status.activePID = p
            else:
                log.error("Cannot find lost daemon pid.")
        else:
            log.error("No output produced. No lost daemon pid found.")

    def rebuildStatus(self):
        """
        rebuild status if status missing
        """
        self._fixLostPID()

    def resume(self):
        """
        resume a job
        """
        if self.status.activePID:
            pid = self.status.activePID
            self._signalAll(pid, signal.SIGCONT)
            self.status.paused = ""
            return "Job was resumed."
        else:
            return "No active queue found."

    def start(self, arg=None, ask=False):
        """
        start job queue
        """
        if self.isActive():
            return "daemon queue is still running."

        # try to start q new queue
        job = self.jobQueue.pop(dry=True)
        if not job:
            return "Queue is empty. Please put jobs into queue, and try again."

        if ask:
            if arg:
                question = "submit %s with %s now? (Y/n)" % (job.description, arg)
            else:
                question = "submit %s now? (Y/n)" % (job.description)
            ans = raw_input(question)
            if ans and ans.lower() != "y":
                return

        submitter = sgqSubmit(self.jobQueue, arg)
        #pid = submitter.loop()
        pid = daemonize(submitter.loop)
        self.status.activePID = pid
        return "queue is activated as a daemon."

    def listQueue(self):
        """
        list queued jobs
        """
        self.jobQueue.list()

    def stop(self):
        """
        stop queue
        """
        self.status.shouldStop = "now"

    def showStatus(self):
        """
        show queue status
        """
        log.debug("query queue status")
        if self.status.shouldStop == "now":
            return "Queue will be stopped after current job."
        if self.status.activePID:
            if self.status.paused:
                return "Job was paused."
            return "Daemon queue is running."

        return "No active daemon queue found."

    def restart(self):
        """
        restart current job
        """
        return "not implemented"
        self.terminate()
        self.start(new_gjf)
   
    def kill(self, ask=False):
        """
        kill sub processes
        """
        if not self.isActive():
            return "No active queue found."

        if ask:
            question = "kill running job now? queued job will be continued. (Y/n)"
            ans = raw_input(question)
            if ans.strip() and ans.lower() != "y":
                return

        pid = self.status.activePID
        pids = self._subPIDS(pid)
        for p in pids:
            log.debug("kill sub processes group %s" % p)
            self._signalAll(p, signal.SIGKILL)

    def isShouldStop(self):
        self.status.refresh()
        if self.status.shouldStop == "now":
            return True
        return False

    def terminate(self, ask=False):
        """
        stop queue and kill running jobs
        """
        if not self.isActive():
            return "daemon queue is not running."

        if ask:
            ans = raw_input("terminate daemon queue and kill current job? (y/N)")
            if not ans.strip() or ans.lower() != "y":
                return
        self.stop()
        self.kill()

        return "queue is over. use 'start' to build a new one."

    def isActive(self):
        if self.status.activePID:
            if os.path.exists("/proc/%s" % self.status.activePID):
                return True
            log.info("queue status is stale. Remove it...")
            self.status.clear()
        return False
    
    def over(self):
        self.status.clear()

class Interpreter(cmd.Cmd):
    """
    interactive control gaussian job queue
    """
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "sgq> "
        self.intro = """Hi, this is job queue Processor; type 'q' to quit; '?' for help. enter start to submit job."""
        resp = commander.showStatus()
        if resp:
            self.intro += "\nTIP: %s" % resp

    def _print(self, string):
        """
        pp print
        """
        if string:
            lst = string.split("\n")
            for l in lst:
                print l

    def completedefault(self, *ignored):
        try:
            if ignored[1][:5] == "start":
                if not ignored[0]:
                    return glob.glob("*.gjf") + glob.glob("*.com")
                else:
                    #print ignored
                    lst = glob.glob("%s*.gjf" % ignored[0]) + glob.glob("%s*.com" % ignored[0])
                    #print lst
                    return lst
        except:
            return os.listdir(".")
    
    def emptyline(self):
        """
        Method to process empty lines.
        """
        pass
    
    def default(self, line):
        """
        default handler for command
        """
        self._print("Not implemented. Try shell command:")
        self._print("="*72)
        try:
            os.system(line)
            #i, o, e = os.popen3(line)
            #err = e.read()
            #out = o.read()
        except KeyboardInterrupt:
            return

        #if err:
        #    self._print("%s" % err.strip())
        #else:
        #    self._print("%s" % out)

    def do_summary(self, server):
        """summary current running job"""
        self._print("summary:")

    def do_fixstatus(self, arg):
        """fix status if status spoiled"""
        commander.rebuildStatus()
        self._print("job finished. type 'status' to verify.")

    def do_status(self, arg=None):
        """check current status"""
        resp = commander.showStatus()
        self._print(resp)

    def do_pwd(self, arg):
        """pwd like in shell"""
        self._print("you are here: " + os.path.abspath("."))

    def do_cdw(self, arg):
        """change to work directory"""
        try:
            os.chdir(conf.sgqWorkDir)
        except OSError, x:
            print x.strerror.strip()

    def do_cdq(self, arg):
        """change to queue directory"""
        try:
            os.chdir(conf.sgqQueueDir)
        except OSError, x:
            print x.strerror.strip()

    def do_cde(self, arg):
        """change to error_done directory"""
        dir = os.path.join(conf.sgqArchiveDir, "error_done")
        try:
            os.chdir(dir)
        except OSError, x:
            print x.strerror.strip()

    def do_cdn(self, arg):
        """chanage to norm_done directory"""
        dir = os.path.join(conf.sgqArchiveDir, "norm_done")
        try:
            os.chdir(dir)
        except OSError, x:
            print x.strerror.strip()

    def do_clear(self, arg):
        """clear like in shell"""
        os.system("clear")

    def do_top(self, arg):
        """top like in shell"""
        os.system("top")
    
    def do_cd(self, arg):
        """cd like in shell"""
        if arg:
            dir = arg
        else:
            dir = conf.sgqRootDir
        try:
            os.chdir(dir)
        except OSError, x:
            print "%s" % x.strerror
    
    def do_ls(self, arg):
        """ls like in shell"""
        self._print("\n".join(os.listdir(".")))

    def do_lsq(self, arg):
        """list queued job"""
        commander.listQueue()

    def do_resume(self, arg):
        """resume gaussian queue"""
        resp = commander.resume()
        self._print(resp)

    def do_pause(self, arg):
        """pause gaussian queues"""
        resp = commander.pause()
        self._print(resp)

    def do_kill(self, server):
        """kill current job running on server"""
        commander.kill(ask=True)

    def do_stop(self, arg):
        """turn off job queue, but current job will be still running."""
        commander.stop()
        self._print("queue will be stopped after current job.")
   
    def help_start(self):
        print "start [warm-up-job]"
        print "warmup-job could be an arbitrary gjf file which will be submitted before queue loop start."

    def do_start(self, warmup_job=""):
        """turn on job queue. """
        if warmup_job:
            lst = glob.glob(warmup_job)
            if len(lst) == 1:
                warmup_job = lst[0]
            else:
                self._print("\n".join(lst))
                return
        resp = commander.start(warmup_job, ask=True)
        self._print(resp)

    def do_terminate(self, arg):
        """stop job queue, and kill current job."""
        resp = commander.terminate(ask=True)
        self._print(resp)

    def do_EOF(self, arg):
        """exit Interpreter, but queue will be still running backgroundly."""
        return True

    do_q = do_exit = do_quit = do_EOF
    do_l = do_ls
    do_c = do_clear

# stolen from here: http://www.noah.org/wiki/index.php/Daemonize_Python
def daemonize (func, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''
    This forks the current process into a daemon.
    The stdin, stdout, and stderr arguments are file names that
    will be opened and be used to replace the standard file descriptors
    in sys.stdin, sys.stdout, and sys.stderr.
    These arguments are optional and default to /dev/null.
    Note that stderr is opened unbuffered, so
    if it shares a file with stdout then interleaved output
    may not appear in the order that you expect.
    '''
    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            return pid
    except OSError, e: 
	return (e.errno, e.strerror) # Fork failed.

    # Decouple from parent environment.
    os.setsid() 
    
    # refer: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
    # When the first child terminates, all processes in the second child
    # are sent a SIGHUP. This causes it to be ignored.
    # signal.signal(signal.SIGHUP, signal.SIG_IGN)

    # Do second fork.
    #try: 
    #    pid = os.fork() 
    #    if pid > 0:
    #        os._exit(0)   # Exit second parent.
    #except OSError, e: 
    #    sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
    #    os._exit(1)

    # Now I am a daemon!
    
    #os.chdir("/") # don't hold open any directories
    os.umask(0) 

    # Close open files. Try the system configuration variable, SC_OPEN_MAX,
    # for the maximum number of open files to close. If it doesn't exist, use 1024.
    #try:
    #    maxfd = os.sysconf("SC_OPEN_MAX")
    #except (AttributeError, ValueError):
    #    maxfd = 1024
    #for fd in range(3, maxfd):
    #    try:
    #        os.close(fd)
    #    except OSError:   # ERROR (ignore)
    #        pass

    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    #record process ID
    #control.status.activePID = os.getpid()
    func()
    sys._exit(0)

def main(argv=None):
    """
    main section
    """
    import optparse

    if argv == None: argv = sys.argv

    cmdl_usage = 'usage: %prog [options]...[queue_id]'
    cmdl_version = "%prog " + __version__
    cmdl_parser = optparse.OptionParser(usage=cmdl_usage, version=cmdl_version, conflict_handler='resolve')
    cmdl_parser.add_option('-h', '--help', action='help',
                            help='print this help text and exit')
    cmdl_parser.add_option('-v', '--version', action='version', 
                            help='print program version and exit')
    cmdl_parser.add_option('-f', '--file', dest='file', 
                            help='start from this gjf file')
    cmdl_parser.add_option('-c', '--configure', dest='configure',
                            action="store_true", default=False, 
                            help='configure the environment.')
    cmdl_parser.add_option('-p', '--pause', dest='pause',
                            action="store_true", default=False, 
                            help='pause running job.')
    cmdl_parser.add_option('-r', '--resume', dest='resume',
                            action="store_true", default=False, 
                            help='resume paused job.')
    (cmdl_opts, cmdl_args) = cmdl_parser.parse_args()

    # do things acording to command line options
    if cmdl_args:
        qid = cmdl_args[0]
    else:
        qid = ""
    global conf
    conf = sgqConf(qid)
    
    # configure environment and exit
    if cmdl_opts.configure:
        conf.configure()
        return

    global commander
    commander = sgqCommander()
    
    # pause job and exit
    if cmdl_opts.pause:
        commander.pause()
        return
    # resume job and exit 
    if cmdl_opts.resume:
        commander.resume()
        return
    
    # submit job
    #if cmdl_opts.file:
    #    commander.start(cmdl_opts.file)
    #else:
    #    commander.start(ask=True)
    qsg = Interpreter()
    qsg.cmdloop()

if __name__ == "__main__":
    import logging

    global log
    log = logging.getLogger()
    hldr = logging.FileHandler('/tmp/simple-gaussian-qsub.log', mode="w")
    format = logging.Formatter("%(asctime)s +%(lineno)04d %(levelname)-7s %(message)s")
    hldr.setFormatter(format)
    log.addHandler(hldr)
    log.setLevel(logging.DEBUG)
    log.info("start of logging".center(72, "="))

    main()
