#! /usr/bin/python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION: a command line tool which facilitates uploading and downloading
#                from web share service: (like: http://ultrashare.net)
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       LICENCE:  GPL version 2 or upper
#       VERSION:  0.1
#       CREATED:  2007-06-28
#      REVISION:  2007-07-27 15:25
#===============================================================================#

# importing
import sys
import os, os.path
import urllib2
import cookielib
import re

#===============================================================================#
#
#  Constants definition and gloable behavior
#
#===============================================================================#

# Exit status constants
exit_failure = 1
exit_success = 0

# Global constants
const_1k = 1024
const_block_size = 10 * const_1k

# Create an OpenerDirector with support for Cookies ...
cookieJar = cookielib.CookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
opener = urllib2.build_opener(cookie_handler)
#+ and install it globally so it can be used with urlopen.
# Try to mimic Firefox, at least a little bit
agent = ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.6) Gecko/20060728 Firefox/1.5.0.6')
opener.addheaders = [agent]
urllib2.install_opener(opener)

#===============================================================================#
#
#  Helper functions
#
#===============================================================================#

def to_k(bytes):
    """
    Convert bytes to KiB
    """
    global const_1k
    return bytes / const_1k

#===============================================================================#
#
#  Classes
#
#===============================================================================#

class multipartForm():
    """
    multipart/form-data used to file uploading
    """
    def __init__(self, post_url=None):
        self.postURL = post_url
        self.fields = []
        self.filePath = None
        self.fileField = "" # filed_name used to uploading file
        self.fileName = ""  # file_name used to uploading file
        self.contentLength = 0

    def addFile(self, file_path, file_name, field_name='file'):
        self.filePath = file_path
        self.fileField = field_name
        self.fileName = file_name

    def appendField(self, name, value):
        if name and value:
            self.fields.append((name, value))

    def post(self):
        """
        fill form with multipart/form-data format
        """
        import httplib
        #httplib.HTTPConnection.debuglevel=1

        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'

        start_data = ""
        for (key, value) in self.fields:
            start_data += ('--' + BOUNDARY)
            start_data += CRLF
            start_data += ('Content-Disposition: form-data; name="%s"' % key)
            start_data += CRLF
            start_data += CRLF
            start_data += value
            start_data += CRLF
        
        start_data += ('--' + BOUNDARY)
        start_data += CRLF
        start_data += ('Content-Disposition: form-data; name="%s"; filename="%s"' % (self.fileField, self.fileName))
        start_data += CRLF
        start_data += ('Content-Type: %s' % self._get_content_type())
        start_data += (CRLF)
        start_data += (CRLF)

        end_data = CRLF
        end_data += ('--' + BOUNDARY + '--')
        end_data += CRLF
        
        file_size = os.path.getsize(self.filePath)
        content_length = str(len(start_data) + file_size + len(end_data))
        host = self.postURL[7:].split('/')[0]
        selector = self.postURL[7 + len(host):]

        h = httplib.HTTP(host)
        h.putrequest('POST', selector)
        h.putheader('Host', host)
        h.putheader('Content-Type','multipart/form-data; boundary=%s' % BOUNDARY)
        h.putheader('Content-Length', content_length)
        h.endheaders()
        
        h.send(start_data)
        fp = open(self.filePath)
        try:
            data = fp.read(const_block_size)
            while data:
                h.send(data)
                data = fp.read(const_block_size)
                current = fp.tell()
                percent = current * 100.0 / file_size
                print "\rSending file data... %sK of %sK, %2.0f%%" % (to_k(current), to_k(file_size), percent),
        except KeyboardInterrupt:
            sys.exit("\nUpload operation was cancelled!")
        print 
        fp.close()

        h.send(end_data)
        errcode, errmsg, headers = h.getreply()
        if errcode in(301, 302):
            import urlparse
            url = urlparse.urljoin(self.postURL, headers.getheader('Location'))
            return urllib2.urlopen(url).read()
        else:
            return h.file.read()

    def _get_content_type(self):
        import mimetypes
        return mimetypes.guess_type(self.filePath)[0] or 'application/octet-stream'

class webshareService:
    """
    web service information
    """
    def __init__(self):
        # parameters for uploading
        self.uploadURL = ""
        self.form = multipartForm()
        self.downloadPattern = ""
        self.serverResponse = ""
        self.report = ""

        # parameters for downloading
        self.downloadURL = ""
        self.savedFilename = ""
    
    def postFile(self, file_path, file_name):
        """
        upload a file into server, then return download link
        """
        download_link = ""

        self.parseForm()
        self.form.addFile(file_path, file_name)
        self.fillForm()
        self.report = self.form.post()
        self.getReport()

        re_link = re.compile(self.downloadPattern, re.IGNORECASE)
        #print self.report #debug
        p = re_link.search(self.report)
        if p:
            download_link = p.group(1)
        return download_link

    def postData(self, link, data):
        """
        helper function for posting data
        """
        from urllib import urlencode
        data = urlencode(data)
        return urllib2.urlopen(link, data)

    def parseForm(self):
        """
        visit uploadURL, and parse the post URL from the output
        """
        # return when a static postURL was found
        if self.form.postURL:
            return

        import urlparse

        output = urllib2.urlopen(self.uploadURL).read()
        re_multipart = re.compile(r'<form[^>]+enctype="multipart/form-data"[^>]*>')
        p = re_multipart.search(output)
        if not p:
            sys.exit("parseForm: Cannot collect file post data from given URL.")
        multipart_data = p.group(0)

        # find the path to uploading a file
        re_action = re.compile(r'action="([^"]+)')
        p = re_action.search(multipart_data)
        if not p:
            sys.exit("parseForm: Cannot find the path to uploading a file.")
        action_url = p.group(1)
        if action_url[:4] != "http":
            base_url = "://".join(urlparse.urlsplit(upload_url)[0:2])
            post_url = urlparse.urljoin(base_url, action_url)
        else:
            post_url = action_url
        self.form.postURL = post_url

    def fillForm(self):
        """
        hook for fill special form field
        """
        pass

    def getReport(self):
        """
        hook for getting download link; to modify self.report
        """
        pass

    def getFile(self, link):
        """
        hook for things before downloading
        """
        return urllib2.urlopen(link)

    def downloadFile(self, link):
        """
        default handle for downloading a file
        """
        self.downloadURL = link
        file_data = self.getFile(link)

        ftype = file_data.info()["Content-Type"]
        try:
            txt = file_data.info()["Content-Disposition"]
        except KeyError:
            sys.exit("No attachment found.")

        if self.savedFilename:
            filename = self.savedFilename
        else:
            # figure out saved_name from response-header
            from urllib import unquote
            txt = unquote(txt)
            ind = txt.find('=') + 1
            filename = txt[ind:]
            if filename[0] == '"' and filename[-1] == '"':
                filename = filename.strip('"')
        
        print('File Type: %s\nFile Name: %s' % (ftype, filename))
        
        # give a chance to rename an existent file.
        if os.path.exists(filename):
            ans = raw_input("%s exist. Rename or Overwrite? (R/O) " % filename)
            if ans and ans.upper() != 'O':
                ans = raw_input("Please input a new filename: ")
                filename = ans
        output_file = open(filename, 'wb')
        byte_counter = 0
        file_block = file_data.read(const_block_size)
        file_len_str = '%sK' % to_k(int(file_data.info()['Content-length']))
        try:
            while len(file_block) != 0:
                byte_counter += len(file_block)
                output_file.write(file_block)
                print('\rRetrieving file data... %sK of %s ' % (to_k(byte_counter), file_len_str)),
                file_block = file_data.read(const_block_size)
        except KeyboardInterrupt:
            sys.exit("Downloading operation was cancelled.")
        output_file.close()

class wiiuploadServer(webshareService):
    """
    http://www.wiiupload.net
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = "http://www.wiiupload.net/"
        self.downloadPattern = r'<input type="text" id="link1" value="(http://.*/fl/\w+)"'
    
    def fillForm(self):
        self.form.fileField = 'file'

    def getFile(self, link):
        sid = link.split('/')[-1]
        new_url = 'http://www.wiiupload.net/sf/%s' % sid
        refer_url = 'http://www.wiiupload.net/dl/%s' % sid
        req = urllib2.Request(new_url)
        req.add_header("Referer", refer_url)
        return urllib2.urlopen(req)

class bestsharingServer(webshareService):
    """
    http://bestsharing.com
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = 'http://bestsharing.com/pageup/upload.js'
        self.downloadPattern = r'value="(http://www.bestsharing.com/files/[^"]+)"'

    def fillForm(self):
        self.form.fileField = 'FILENAME'
        self.form.appendField('LANG', 'en')
        self.form.appendField('Upload!', 'Upload!')
    
    def getFile(self, link):
        rex = re.compile(r'<a href="(http://.+/[^"]+)"[^>]+>Download file</a>')
        report = urllib2.urlopen(link).read()
        p = rex.search(report)
        if p:
            link = p.group(1)
        else:
            sys.exit("bestsharingServer: Cannot get the static download URL. May be a server upgrade.")
        return urllib2.urlopen(link)

class filewindServer(webshareService):
    """
    http://www.filewind.com
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = 'http://www.filewind.com'
        self.downloadPattern = r'<a href="(http://.*\.filewind\.com/g\.php\?filepath=[^"]+)"'
        self.delimer = "_=_"

    def fillForm(self):
        # randomise fileName
        import random
        self.form.fileField = "userfile[]"
        self.form.fileName += (self.delimer + "%i" % (random.random()*10**5))
        self.form.appendField("Submit", "Upload File")
    
    def getFile(self, link):
        """
        formalize savedFilename
        """    
        new_url = link.replace("g.php", "file.php")
        refer_url = link
        req = urllib2.Request(new_url)
        req.add_header("Referer", refer_url)
        report = urllib2.urlopen(req)

        # fix filename
        txt = report.info()["Content-Disposition"]
        rex = re.compile(r'attachment; filename="([^"]+)')
        p = rex.search(txt)
        if p:
            filename = p.group(1)
            self.savedFilename = filename.split(self.delimer)[0]
        else:
            sys.exit('Bad thing happened.')
        return report

class fs2youServer(webshareService):
    """
    http://www.fs2you.com
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = 'http://www.fs2you.com'
        self.downloadPattern = r'(http://www.fs2you.com/files/[\w|-]+)'

    def fillForm(self):
        self.form.fileField = "upload0"
        self.form.appendField("upload_count", "1")
        self.form.appendField("email", "foo.foo.foo@eyou.com")
        self.form.appendField("description", "posted by wudloader.py.")

    def getReport(self):
        rex = re.compile(r'<input name="([^"]+)".+ value="([^"]+)".*/>')
        data = rex.findall(self.report)
        if data:
            rex = re.compile(r'action="(http://[^"]+)">')
            p = rex.search(self.report)
            if p:
                post_url = p.group(1)
                data = dict(data)
                self.report = self.postData(post_url, data).read()
            else:
                sys.exit("Failed!")
        else:
            sys.exit("Failed")
    
    def getFile(self, link):
        report = urllib2.urlopen(link).read()
        rex = re.compile(r"preview_url = '(http://.+\.fs2you\.com/[^']+)'")
        p = rex.search(report)
        if p:
            return urllib2.urlopen(p.group(1))
        else:
            sys.exit("Failed!")

class justfreespaceServer(webshareService):
    """
    http://filehost.justfreespace.com/upload.php
    """
    def __init__(self):
        import random
        webshareService.__init__(self)
        self.identifier = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 11))
        self.uploadURL = "http://filehost.justfreespace.com/upload.php"
        self.form.postURL = self.uploadURL
        self.downloadPattern = r'>(http://FileHost.JustFreeSpace.Com/[^<]+)</textarea>'
    
    def fillForm(self):
        self.form.fileField = "upfile"
        self.form.appendField("myemail", "")
        self.form.appendField("descr", "uploaded by wudloader.py")
        self.form.appendField("pprotect", "")

    def getFile(self, link):
        report = urllib2.urlopen(link).read()
        rex = re.compile(r"(http://FileHost.JustFreeSpace.Com/download.*\.php\?[^\\]+)", re.IGNORECASE)
        p = rex.search(report)
        if p:
            link = p.group(1)
            print link
            return urllib2.urlopen(link)
        else:
            sys.exit('Failed!')

class filesendServer(webshareService):
    """
    http://www.filesend.net
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = "http://www.filesend.net"
        self.downloadPattern = r'href="(http://www.filesend.net/download.php\?f=[^"]+)"'

    def fillForm(self):
        self.form.fileField = "upfile_0"
        #self.form.appendField("MAX_FILE_SIZE", "125829120")
        self.form.appendField("confirm", "on")
        self.form.appendField("confirm", "0")
        self.form.appendField("upload_range", "1")

    def getFile(self, link):
        report = urllib2.urlopen(link).read()
        rex = re.compile('action="(http://[^"]+)".*name="sid"\s+value="([^"]+)"', re.IGNORECASE)
        p = rex.search(report)
        if p:
            link = p.group(1)
            data = {
                "sid": p.group(2)
            }
            return self.postData(link, data)
        else:
            sys.exit("Failed!")

class filehostServer(webshareService):
    """
    http://www.filehost.gr/upload.php
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = "http://www.filehost.gr"
        self.form.postURL = "http://www.filehost.gr/upload.php"
        self.downloadPattern = r'href="(http://www.filehost.gr/download[^"]+)">'

    def fillForm(self):
        self.form.fileField = "upfile"
        self.form.appendField("from", "")
        self.form.appendField("operation", "1")
        self.form.appendField("agreecheck", "on")

    def getFile(self, link):
        report = urllib2.urlopen(link).read()
        rex = re.compile(r'href="(http://www.filehost.gr/download[^"]+)"')
        p = rex.search(report)
        if p:
            link = p.group(1)
            return urllib2.urlopen(link)
        else:
            sys.exit("Failed!")

class uploadjarServer(webshareService):
    """
    http://www.uploadjar.com/upload.php
    """
    def __init__(self):
        webshareService.__init__(self)
        self.uploadURL = "http://www.uploadjar.com/"
        self.form.postURL = "http://www.uploadjar.com/upload.php"
        self.downloadPattern = r'value="(http://uploadjar.com/[^"]+)"'

    def fillForm(self):
        self.form.fileField = "upfile"
        self.form.appendField("myemail", "")
        self.form.appendField("descr", "uploaded by wudloader.py")
        self.form.appendField("agreecheck", "")
    
    def getFile(self, link):
        report = urllib2.urlopen(link).read()
        rex = re.compile(r"window.location=\\'(download[^\\]+)", re.IGNORECASE)
        p = rex.search(report)
        if p:
            import urlparse
            link = urlparse.urljoin(link, p.group(1))
            return urllib2.urlopen(link)
        else:
            sys.exit("Failed!")

class webloader:
    """
    Utilities for uploading or downloading powered by free web share service
    """
    def __init__(self):
        # build up servers
        wiiupload = wiiuploadServer()
        filewind = filewindServer()
        fs2you = fs2youServer()
        bestsharing = bestsharingServer()
        justfreespace = justfreespaceServer()
        filesend = filesendServer()
        filehost = filehostServer()
        uploadjar = uploadjarServer()

        # parameters for uploading session
        self.serviceList = [wiiupload, filewind, bestsharing, fs2you, justfreespace, filesend, filehost, uploadjar]
        self.workServer = self.serviceList[0]
        self.uploadFiles = []
        self.compress = False

    def _compress(self, file_path):
        """
        make a bz2 compressed file instead of the original one.
        """
        import bz2
        import tempfile

        bzfile = tempfile.mkstemp('.bz2')[1]
        bzfp = bz2.BZ2File(bzfile, 'wb')
        chunk = 1024**2 # 1MB
        try:
            fp = open(file_path, 'rb')
        except:
            sys.exit('compress: File is not readable.')
        data = fp.read(chunk)
        while data:
            bzfp.write(data)
            data = fp.read(chunk)

        fp.close()
        bzfp.close()
        return bzfile

    def _selectServiceByURL(self, link):
        """
        select the appropriate server by link
        """
        for s in self.serviceList:
            str_url = s.downloadPattern
            start = str_url.find('(') + 1
            end = str_url.find(')')
            re_url = re.compile(str_url[start:end])
            p = re_url.search(url)
            if p:
                self.workServer = s
                return True
        print "WARNING: This server is not currently supported. Use default download method instead."

    def listServices(self):
        for s in self.serviceList:
            print "   %s\t%s" % (self.serviceList.index(s), s.uploadURL)

    def selectService(self, server_index):
        if server_index < 0 or server_index >= len(self.serviceList):
            print "server out of index."
        else:
            self.workServer = self.serviceList[server_index]
        
    def appendUploadFile(self, filename):
        if os.path.exists(filename):
            print 'Append %s into upload Queue.' % filename
            self.uploadFiles.append(filename)
        else:
            print '%s does not exist in your filesystem. Discarded.' % filename

    def upload(self):
        """
        Uploading
        """
        for file_path in self.uploadFiles:
            # if compress...
            file_name = os.path.basename(file_path)
            if self.compress:
                print "Compressing file before sending..."
                file_path = self._compress(file_path)
                file_name += ".bz2"

            print "uploading %s onto %s, please wait..." % (f, self.workServer.uploadURL[7:].split('/')[0])
            link = self.workServer.postFile(file_path, file_name)
            if link:
                print("Uploaded successfully! Please download from below link:")
                print("%s" % link)
            else:
                print "There is a mistake. Cannot find the download Link from output."

    def download(self, link):
        """
        downloading 
        """
        self._selectServiceByURL(link)
        self.workServer.downloadFile(link)

#===============================================================================#
#
#  Main Program
#
#===============================================================================#

import optparse
import glob

# Create the command line options parser and parse command line
cmdl_usage = 'usage: %prog [options] download_url_or_upload_filename'
cmdl_version = '2007.07.08'
cmdl_parser = optparse.OptionParser(usage=cmdl_usage, version=cmdl_version, conflict_handler='resolve')
cmdl_parser.add_option('-h', '--help', action='help', help='print this help text and exit')
cmdl_parser.add_option('-v', '--version', action='version', help='print program version and exit')
cmdl_parser.add_option('-c', '--compress', action='store_true', dest='compress', default=False, help='compress input file before uploading')
cmdl_parser.add_option('-l', '--list', action='store_true', dest='list', default=False, help='list the available share services')
cmdl_parser.add_option('-s', '--select', dest='server_index', default=0, type="int", help='select the service in the list')
(cmdl_opts, cmdl_args) = cmdl_parser.parse_args()

# do things acording to command line options
loader = webloader() 
if cmdl_opts.list:
    print "Currently available serivices:"
    loader.listServices()
    sys.exit(exit_success)
if cmdl_opts.server_index:
    loader.selectService(cmdl_opts.server_index)

# URLs or files
URLs = []
files = []

# Guess the mission type from the argument
#+Maybe files? glob it!
for f in cmdl_args:
    guess = glob.glob(f)
    if guess:
        files += guess
    else:
        if len(f) >= 10 and f[:7] == 'http://':
            URLs.append(f)
        else:
            sys.exit("No files or URLs were given.")

if not URLs and not files:
    cmdl_parser.print_help()
    sys.exit(exit_failure)

if URLs:
    for url in URLs:
        loader.download(url)
if files:
    if cmdl_opts.compress:
        loader.compress = True
    for file in files:
        loader.appendUploadFile(file)
    loader.upload()

