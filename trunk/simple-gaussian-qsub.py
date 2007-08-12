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
#       VERSION:  0.1
#       CREATED:  2007-07-28
#       UPDATED:  2007-08-12 18:24
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

__version__ = "0.2"
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

        # regvar
        if not self.groot:
            self.groot = "/export/home/gaussian"
        else:
            self.groot = self._expandPath(self.groot)
        if not self.gcmd:
            self.gcmd = "g03"
        if not self.gscratch:
            self.gscratch = "/tmp"
        else:
            self.gscratch = self._expandPath(self.gscratch)

        if not self.sgqRootDir:
            self.sgqRootDir = os.path.join(os.environ["HOME"], "sgq%s" % self._code)
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
            self.sgqArchiveDir = os.path.join(self.sgqRootDir, "archive")
        else:
            self.sgqArchiveDir = self._expandPath(self.sgqArchiveDir)
        if not self.sessionID:
            hostname = socket.gethostname()
            user = os.getenv('USER')
            self.sessionID = "%s@%s%s" % (user, hostname, self._code)

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
        ans = raw_input(leader + "Where is your g03/g98's root directory? (%s)" % groot)
        if ans.strip():
            groot = ans
        # question 1: where is your gaussian scratch directory?
        gscratch = self.gscratch
        if os.environ.has_key("GAUSS_SCRDIR"):
            gscratch = os.environ["GAUSS_SCRDIR"]
        elif os.path.exists(os.path.join(groot, "scratch")): # /groot/scratch
            gscratch = os.path.join(groot, "scratch")

        ans = raw_input(leader + "Where is your gaussian scratch diretory? (%s)" % gscratch)
        if ans.strip():
            gscratch =ans
        test_dir = os.path.join(gscratch, "test_test")

        try:
            os.makedirs(test_dir)
            os.rmdir(test_dir)
        except OSError:
            print "scratch directory is not writeable. You need correct this error."
        # final test
        if not self.validateConf():
            print leader + "WARNING! It seems your setting does not work. I cannot find gaussian profile." 
            print cont + "Did your gaussian package install correctly?"

        # remote server
        remote_server = ""
        ans = raw_input(leader + "Do you want to use a remote queue/archive server? (N/y)")
        if ans.strip().lower() == "y":
            print leader + "IN ORDER TO USE THIS, YOU NEED A PASSWORDLESS SSH CONNECTION TO THE REMOTE SERVER."
            print cont + "For details, please google \"passwordless ssh\", and follow the instructions."
            ans = raw_input(leader + "Now, please input your remote queue server's IP address or name. ")
            if ans.strip():
                remote_server = ans

        self.groot = groot
        self.gcmd = gcmd
        self.gscratch = gscratch
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

        # parse gjf file, fill content and checkFile
        self._parse()
    
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
            print "sgqJob: %s" % errstr.strip()
            return ""
        self.content = o.read()
        rex = re.compile(r'%chk=(.$)')
        p = rex.search(self.content)
        if p:
            self.checkFile = p.group(1).strip()

    def sign(self):
        """
        """
        self.signature = code

class sgqQueue:
    """
    job queue
    """
    def __init__(self):
        self.localQueue = []
        self.remoteQueue = []
        self.signedLocalQueue = []
        self.signedRemoteQueue = []
        self.queue = []
        self.signature = socket.gethostname()

    def _parseDirectory(self, path, host=""):
        """
        path should be a directory, remote or local: host:path/
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
            if out:
                lst = out.split("\n")
            else:
                return
            for l in lst:
                if host: path = host + ":" + path
                path = os.path.join(path, l)
                queue.append(sgqJob(path))
        return queue

    def updateLocal(self):
        """
        update queue from files in queueDir
        """
        if not os.path.exists(conf.sgqQueueDir):
            log.warning("Queue directory does not exist. make it.")
            os.makedirs(conf.sgqQueueDir)
            self.localQueue = []
            return 

        self.localQueue = self._parseDirectory(conf.sgqQueueDir)

        # look into local path signed for this node
        path = os.path.join(conf.sgqQueueDir, self.signature)
        if not os.path.isdir(path):
            log.debug("No signed job for %s" % (self.signature))
            return
        queue = self._parseDirectory(path)
        log.debug("get signed job from %s for %s" % (path, self.signature))
        # remove empty directy
        if not queue:
            log.debug("empty signed queue for %s, remove it." % self.signature)
            try:
                os.rmdir(path)
            except:
                log.warning("failed to remove signed directory.")

        self.signedLocalQueue = queue
    
    def updateRemote(self):
        """
        update queue from remote host
        """
        if not conf.remoteQueueDir:
            return
        host, path = conf.remoteQueueDir.split(":", 1)
        self.remoteQueue = self._parseDirectory(path, host)
        # look into path signed for this node
        path = os.path.join(path, self.signature)
        self.signedRemoteQueue = self._parseDirectory(path, host)

    def update(self):
        """
        update both
        """
        self.updateLocal()
        self.updateRemote()
        self.queue = self.signedLocalQueue + self.signedRemoteQueue + self.localQueue + self.remoteQueue

    def pop(self):
        """
        pop up a file from job queue, return file content and file name
        """
        self.update()
        if self.queue:
            job = self.queue.pop(0)
            # destroy queued file, use job.content to get file content
            # TODO: fix
            #job.remove()
        else:
            return None
        return job

    def currentJob(self):
        """
        get current job information
        """
        self.update()
        if not self.isEmpty():
            return self.queue[0]
        else:
            log.warning("invoke empty currentJob.")

    def isEmpty(self):
        self.update()
        if not self.queue:
            return True
        else:
            return False

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
        lst = glob.glob(os.path.join(self.workDir, "*.log"))
        if lst:
            name = lst.sort()[-1][:-4]
        else:
            log.warning("No log file found in work directory.")
            return

        # check gaussian log status
        glog = name[:-4] + ".log"
        path = os.path.join(self.workDir, glog)
        fp = open(path, "rb")
        fp.seek(-500, 2)
        res = fp.read().find("Normal termination")
        fp.close()
        if res >=0:
            status = "normal_done"
        else:
            status = "error_done"

        # generate archive directory name
        import time
        import random
        uid = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 6))
        dir = time.strftime("%Y-%m%d-%H%M") + "@%s@" % uid + name[:-4]

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
            place_to = host + ":" + path
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
            print "%s does not exists." % profile
            sys.exit("Did your gaussian package setup correctly?")

        script = os.path.join(conf.sgqWorkDir, "run")
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
        log = job.name[:-4] + ".log"
        fp.write("exec sed -e 's/\r$//; $G' %s | %s > %s 2> debug\n" % (job.name, conf.gcmd, log))
        fp.close()

        # restore gjf file from content
        fp = open(os.path.join(conf.sgqWorkDir, job.name), "wb")
        fp.write(job.content)
        fp.close()

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
            log.info("submit job with name: %s" % job.name)
            self.submitGaussian(job)
            self.jobArchive.archive()
            job = self.jobQueue.pop() 
        log.info("No more queued job. exit...")
        commander.over()

class sgqCommander:
    """
    commander send command
    """
    def __init__(self):
        self.jobQueue = sgqQueue()
        self.status = statusConf()

    def pause(self):
        """
        pause queue and running job
        """
        if self.status.activePID:
            pid = int(self.status.activePID)
            self._signalAll(pid, signal.SIGSTOP)
            self.status.paused = "yes"
            print "Job was paused. Enter resume to continue."
        else:
            print "No active queue found."
    
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
            if __DEBUG__: print "sgqCommander: %s" % errstr
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

    def resume(self):
        """
        resume a job
        """
        if self.status.activePID:
            pid = self.status.activePID
            self._signalAll(pid, signal.SIGCONT)
            self.status.paused = ""
            print "Job was resumed."
        else:
            print "No active queue found."

    def start(self, arg=None):
        """
        start job queue
        """
        if self.isActive():
            print "daemon queue is still running."
            return

        # try to start q new queue
        if arg:
            ans = raw_input("submit with %s now? (Y/n)" % arg)
            if ans and ans.lower() != "y":
                return
        else:
            job = self.jobQueue.currentJob()
            if not job:
                print "Queue is empty. Please put jobs into queue, and try again."
                return
            ans = raw_input("submit %s now? (Y/n)" % job.name)
            if ans.strip() and ans.lower() != "y":
                return
        print "queue is activated as a daemon."
        submitter = sgqSubmit(self.jobQueue, arg)
        pid = daemonize(submitter.loop)
        self.status.activePID = pid
    
    def stop(self):
        """
        stop queue
        """
        self.status.shouldStop = "now"

    def showStatus(self):
        """
        show queue status
        """
        if self.status.shouldStop == "now":
            print "Queue will be stopped after current job."
            return
        if self.status.activePID:
            if self.status.paused:
                print "Job was paused."
                return
            print "Daemon queue is running."
            return

        print "No active daemon queue found."

    def restart(self):
        """
        restart current job
        """
        print "not implemented"
        return
        self.terminate()
        self.start(new_gjf)
   
    def kill(self):
        """
        kill sub processes
        """
        pid = self.status.activePID
        pids = self._subPIDS(pid)
        for p in pids:
            log.debug("kill sub processes group %s" % p)
            self._signalAll(p, signal.SIGKILL)

    def isShouldStop(self):
        if self.status.shouldStop == "now":
            return True
        return False

    def terminate(self):
        if not self.isActive():
            print "daemon queue is not running."
            return

        ans = raw_input("terminate daemon queue and kill current job? (N/y)")
        if not ans.strip() or ans.lower() != "y":
            return
        self.stop()
        self.kill()
        self.over()

        print "queue is over. use 'start' to build a new one."

    def isActive(self):
        if self.status.activePID:
            if os.path.exists("/proc/%s" % self.status.activePID):
                return True
            print "queue status is stale. Remove it..."
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
        self.intro = """This is job queue Processor; type 'q' to quit; '?' for help."""

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
        os.system(line)

    def do_summary(self, server):
        """summary current running job"""
        print "summary:"

    def do_status(self, arg):
        """check current status"""
        commander.showStatus()

    def do_cdw(self, arg):
        """change to work directory"""
        os.chdir(conf.sgqWorkDir)
    
    def do_pwd(self, arg):
        """pwd like in shell"""
        print os.path.abspath(".")

    def do_cdq(self, arg):
        """change to queue directory"""
        os.chdir(conf.sgqQueueDir)

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
        print "\n".join(os.listdir("."))

    def do_resume(self, arg):
        """resume gaussian queue"""
        commander.resume()

    def do_pause(self, arg):
        """pause gaussian queues"""
        commander.pause()

    def do_kill(self, server):
        """kill current job running on server"""
        commander.kill()

    def do_stop(self, arg):
        """turn off job queue, but current job will be still running."""
        commander.stop()
        print "queue will be stopped after current job."
   
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
                print "\n".join(lst)
                return
        commander.start(warmup_job)

    def do_terminate(self, arg):
        """stop job queue, and kill current job."""
        commander.terminate()

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
    if cmdl_opts.file:
        commander.start(cmdl_opts.file)
    else:
        commander.start()
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
