#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  Make a directory named as .backup in your home folder, and then
#              +  put things or their symbol link that you want to backup into this 
#              +  place.
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  x/10/2006 
#      REVISION:  17/11/2006
#===============================================================================#
BackupDir = '~/.backup'
DestPath = '~/backup'
RemoteServer = '192.168.5.15'
ExcludeFile = '~/.cron/rsync.exclude'
#===============================================================================#
import sys, os
import gnomevfs
import re
from datetime import datetime

class simpleBackup:
    def __init__(self, backupDir, destPath, lockfile = '/var/lock/sbackup.lock', remoteServer = '', excludeFile = ''):
        self.backupDir = backupDir 
        self.destPath = os.path.expanduser( destPath )
        self.remoteServer = remoteServer
        self.excludeFile = os.path.expanduser( excludeFile )
        self.dirPattern = re.compile( '^(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})' )
        self.lockfile = lockfile
        self.archivedFolders = []
        self.purgedFolders = []

    def _folder2time(self, folderName):
        # 2006-10-13-2255.8zZwpJ
        m = self.dirPattern.search( folderName )
        if m:
            atime = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
            return atime
        else:
            return False

    def _logAlgorithmFilter(self):
        odays = {}
        omonths = {}
        oyears = {}
        folder2time = self._folder2time

        for f in self.archivedFolders:
            atime = self._folder2time(f)
            if atime:
                now = datetime.today()
                if (now - atime).days <= 365:
                    # this year
                    if (now - atime).days <= 30:
                        # this month
                        if (now - atime).days <= 7:
                            # this week
                            pass
                        else:
                            # purge the old, and keep the newest of the day
                            if not odays.has_key(atime.day):
                                odays[atime.day] = f
                            elif (odays.has_key(atime.day) and atime > folder2time(odays[atime.day])):
                                self.purgedFolders.append(odays[atime.day])
                                odays[atime.day] = f
                            else:
                                self.purgedFolders.append(f)
                    else:
                        # purge the old, and keep the newest of the month
                        if not omonths.has_key(atime.month):
                            omonths[atime.month] = f
                        elif ( omonths.has_key(atime.month) and atime > folder2time(omonths[atime.month])):
                            self.purgedFolders.append(omonths[atime.month])
                            omonths[atime.month] = f
                        else:
                            self.purgedFolders.append(f)
                else:
                    # purge the old, and keep the newest of the year
                    if not oyears.has_key(atime.year):
                        oyears[atime.year] = f
                    elif (oyears.has_key(atime.year) and atime > folder2time(oyears[atime.year])):
                        self.purgedFolders.append(oyears[atime.year])
                        oyears[atime.year] = f
                    else:
                        self.purgedFolders.append(f)

    def _exitfunc( self ):
        # Remove lockfile
        os.remove(self.lockfile)
        sys.exit(1)
    
    def _joinFolder(self, old, new):
        """\
         update the new with the old. Is this strange? No.
        """

        # I cannot use mv to overwrite same directory, so use cp instead.
        cmd = 'cp -rdpfu %s/* %s/' % (self.destPath + '/' + old, self.destPath + '/' + new)
        if self.remoteServer != '':
            cmd = "ssh %s '%s'" % (self.remoteServer, cmd)

        # do it!
        pipe = os.popen(cmd) 
        if pipe.close():
            return 1
        else:
            return 0 
        
    def _removeDir(self, dest, force = False):
        dest = self.destPath + '/' + dest

        # try to remove the empty directory
        if force:
            cmd = 'rm -rf %s' % ( dest )
        else:
            cmd = 'rmdir %s 2>/dev/null' % ( dest )

        if self.remoteServer != '':
            cmd = 'ssh %s %s' % ( self.remoteServer, cmd )
       
        pipe = os.popen(cmd) 
        if pipe.close():
            return 1
        else:
            return 0 
        
    def doTransfer(self):
        self.inc_dir = datetime.today().strftime('%Y-%m-%d-%H%M.%S')
        if self.remoteServer == '':
            self.rsyncDest = self.destPath + '/' + 'current'
            cmd = "mktemp -d destPath/%s.XXXXXX" % self.inc_dir
        else:
            self.rsyncDest = self.remoteServer + ':' + self.destPath + '/' + 'current'
            cmd = "ssh %s mktemp -d %s/%s.XXXXXX" % (self.remoteServer, self.destPath, self.inc_dir )
        
        pipe = os.popen(cmd)
        self.inc_dir = pipe.read().strip()
        if pipe.close():
            print "E: Can't create temporary incremental backup directory."
            return 1

        if self.excludeFile != '':
            self.rsyncOptions = '--force --ignore-errors --delete-excluded --exclude-from=%s  --delete --backup -l --backup-dir=%s -a' % (self.excludeFile, self.inc_dir)
        else:
            self.rsyncOptions = '--force --ignore-errors --delete --backup -L --backup-dir=%s -a' % (self.excludeFile, self.inc_dir)
        
        cmd = 'rsync %s %s %s' % ( self.rsyncOptions, self.backupDir, self.rsyncDest )
        pipe = os.popen(cmd)
        print pipe.read().strip()
        if pipe.close():
            return 1
        else:
            return 0
    

    def doPurge(self, join = False):
        # try to remove the empty folder 
        self._removeDir(self.inc_dir, force = False)
        
        if self.remoteServer == '':
            destURI = 'file://' + self.destPath
        else:
            destURI = 'ssh://' + self.remoteServer + '/' + self.destPath

        # use gnomevfs to process the local/remote directory. 
        try:
            d = gnomevfs.open_directory( destURI )
            for f in d:
                if f.type == 2 and f.name != "." and f.name != ".." and self.dirPattern.search( f.name ):
                    self.archivedFolders.append( f.name )
        except:
            print "E: Can't use gnomevfs to process the local/remote folders."
            return 1

        self.archivedFolders.sort()
        self.archivedFolders.reverse()
        self._logAlgorithmFilter()
        # print self.archivedFolders
        
        for f in self.purgedFolders:
            print "removing %s" % f
            if join: 
                ji = self.archivedFolders.index(f) -1
                while ji >=0:
                    if self.archivedFolders[ji] in self.purgedFolders:
                        ji -= 1
                    else:
                        break
                if ji >=0:
                    self._joinFolder(old = f, new = self.archivedFolders[ji])
            self._removeDir( f, force = True )

    def doBackup(self):
        """\
        """

        import atexit

        # Create the lockfile so noone disturbs us
        ok = False
        try: 
            fp = open( self.lockfile, "r" )
            pid = fp.readline().strip()
            fp.close()
            if pid != '':
                test = os.popen("/bin/ps h " + pid).read().strip()
                if test == '':
                    ok = True
        except IOError:
            ok = True

        if not ok:
            sys.exit("E: Another Simple Backup daemon already running: exiting")

        try:
            fp = open( self.lockfile, "w" )
            fp.write(str(os.getpid()))
            fp.close()
        except IOError:
            print "E: Can't create a lockfile: ", sys.exc_info()[1]
        atexit.register(self._exitfunc)
        
        if self.doTransfer() == 0:
            self.doPurge(join = True)
            return 0
        else:
            print "E: rsync failed to backup your directories."
            return 1

try:
    RemoteServer = RemoteServer
except NameError:
    RemoteServer = ''

BackupDir = os.path.expanduser(BackupDir)

if not os.path.exists(BackupDir):
    print "E: backup directory %s doesn't exist." % BackupDir
    sys.exit(2)

d = ''
for s in os.listdir(BackupDir):
    if os.path.islink(os.path.join(BackupDir, s)):
        d += os.path.realpath(os.path.join(BackupDir, s)) + ' '
    else:
        d += os.path.join(BackupDir, s)

backup = simpleBackup( backupDir = d, destPath = DestPath, remoteServer = RemoteServer, excludeFile = ExcludeFile )
backup.doBackup()
