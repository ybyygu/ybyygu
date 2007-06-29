#! /usr/bin/python
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
#       CREATED:  2007-6-28
#      REVISION:  ---
#===============================================================================#
import sys
import os, os.path
import time
import getopt
import string
import urllib
import urllib2
import socket
import re
import mimetypes
import mimetools

# Exit status constants
exit_failure = 1
exit_success = 0

# Global constants
const_1k = 1024
const_block_size = 10 * const_1k


###
# tools funciton
#

# Wrapper to create custom requests with typical headers
def request_create(url, data=None):
	retval = urllib2.Request(url)
	if not data is None:
		retval.add_data(data)
	# Try to mimic Firefox, at least a little bit
	retval.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.6) Gecko/20060728 Firefox/1.5.0.6')
	retval.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	retval.add_header('Accept', 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5')
	retval.add_header('Accept-Language', 'en-us,en;q=0.5')
	return retval

# Perform a request, process headers and return response
def perform_request(url, data=None):
	request = request_create(url, data)
	response = urllib2.urlopen(request)
	return response


# Convert bytes to KiB
def to_k(bytes):
	global const_1k
	return bytes / const_1k

###
# How to upload a file into www.divshare.com
#
import threading
import time
class progresser(threading.Thread):
    def __init__(self, sid):
        self.url = "http://www.divshare.com/scripts/ajax/progress.php"
        self.data = "sid=" + "%s" % sid + "&_="
        threading.Thread.__init__(self, name = "progresser")
        self.closed = False
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self.closed: 
            time.sleep(1)
            status_data = perform_request(self.url, self.data).read()
            status_data = status_data.split(' '*10)[-1].strip().split(';')
            percent = status_data[0]
            current = status_data[1]
            total = status_data[2]
            unit = status_data[3]
            speed = status_data[4]
            remain_time = status_data[5]
            print "\ruploading: %s%%, %s of %s%s" % (percent, current, total, unit) ,
            print "; speed: %s KB/s" % speed ,
            print "; remain: %s" % remain_time
    def close(self):
        self.closed = True
        

def uploader(host, upload_file):
    # Create an OpenerDirector with support for Cookies ...
    cookie_handler = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookie_handler)
    # ..and install it globally so it can be used with urlopen.
    urllib2.install_opener(opener)
    
    txt = urllib2.urlopen("http://%s" % host).read()
    re_uri = re.compile(r'/cgi-bin/upload.cgi\?sid=([^"])+')
    p = re_uri.search(txt)
    if p:
        uri = p.group()
        sid = uri[24:] 
    else:
        print "Cannot find the correct uri."
        return 1
    url = "http://" + host + uri
    
    fields = []
    files = [("file[0]", upload_file)]
    content_type, body = encode_multipart_formdata(fields, files)
    headers = {'Content-Type': content_type,
               'Content-Length': str(len(body))}
    req = urllib2.Request(url, body, headers)

    try:
        # make some feedback to user
        feedback = progresser(sid)
        # uploading ...
        report = urllib2.urlopen(req)
        feedback.close()

        # try to get the download url
        url = "http://www.divshare.com/upload"
        data = "upload_method=progress&data_form_sid=%s&terms=on" % sid
        req = urllib2.Request(url, data)
        txt = urllib2.urlopen(req).read()
        re_link = re.compile(r'href="http://www.divshare.com/download/[^"]+"')
        p = re_link.search(txt)
        if p:
            download_link = p.group()[6:-1]
            print("Uploaded successfully!")
            print("Please download from below link:")
            print("%s" % download_link)
    except urllib2.URLError, msg:
        print "uploader: Urllib2 error (%s)" % msg
        return False
    except socket.error, (errno, strerror):
        print "uploader: Socket error (%s) for host %s (%s)" % (errno, host, strerror)
        return False
    return True

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, file_name) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []

    # Add the metadata about the upload first
    if fields:
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
    # Now add the file itself

    for (key, file_name) in files:
        base_name = os.path.basename(file_name)
        f = open(file_name)
        file_content = f.read()
        f.close()
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, base_name))
        L.append('Content-Type: %s' % get_content_type(file_name))
        L.append('')
        L.append(file_content)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


###
# How to get it from divshare server
#


def downloader(url):
    # Install cookie handler
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor()))
    file_data = perform_request(url)
    print('File data found at %s' % file_data.geturl())
    ftype = file_data.info()["Content-Type"]
    if ftype[:len("text/html")] == "text/html":
        txt = file_data.read()
        re_meta_refresh_url = re.compile(r'<meta http-equiv="refresh"[^>]+')
        p = re_meta_refresh_url.search(txt)
        if p:
           meta_refresh_url = p.group()
        else:
            print "No meta refresh url found."
            return 1
        re_url = re.compile(r'url=(http://[^"]+)')
        p = re_url.search(meta_refresh_url)
        if not p:
            print "Cannot collect the correct url."
        refresh_url = p.group(1)
    else:
        print "Unexpected situation."
        return 1
    
    print('Redirect to %s' % refresh_url)
    file_data = perform_request(refresh_url)
    ftype = file_data.info()["Content-Type"]
    try:
        file_len_str = '%sk' % to_k(int(file_data.info()['Content-length']))
    except KeyError:
        file_len_str = '(unknown)'
    
    try:
        txt = file_data.info()["Content-Disposition"]
        re_filename = re.compile(r'attachment; filename="([^"]+)')
        p = re_filename.search(txt)
        if p:
            filename = p.group(1)
        else:
            filename = "unknown.file"
            print "Filename unknown."
    except:
        print("Some terrrible thing happen.") 
        return 1
    
    print('File Type: %s\nFile Name: %s' % (ftype, filename))
    output_file = open(filename, 'wb')
    byte_counter = 0
    file_block = file_data.read(const_block_size)
    while len(file_block) != 0:
        byte_counter += len(file_block)
        output_file.write(file_block)
        print('\rRetrieving file data... %sk of %s ' % (to_k(byte_counter), file_len_str)),
        file_block = file_data.read(const_block_size)
    output_file.close()


#===============================================================================#
#
#  Main Program
#
#===============================================================================#

import optparse

# Create the command line options parser and parse command line
cmdl_usage = 'usage: %prog [options] download_url_or_upload_filename'
cmdl_version = '2007.06.29'
cmdl_parser = optparse.OptionParser(usage=cmdl_usage, version=cmdl_version, conflict_handler='resolve')
cmdl_parser.add_option('-h', '--help', action='help', help='print this help text and exit')
cmdl_parser.add_option('-v', '--version', action='version', help='print program version and exit')
cmdl_parser.add_option('-d', '--down', dest='downurl', help='download from www.divshare.com')
cmdl_parser.add_option('-u', '--upload', dest='uploadfile', metavar='FILE', help='upload file to www.divshare.com')
cmdl_parser.add_option('-q', '--quiet', action='store_true', dest='quiet', help='activates quiet mode')
(cmdl_opts, cmdl_args) = cmdl_parser.parse_args()

down_url = None
upload_file = None
# Get the file or url if specified
if cmdl_opts.uploadfile:
    upload_file = cmdl_opts.uploadfile
elif cmdl_opts.downurl:
    down_url = cmdl_opts.downurl

# Guess the mission type from the argument if without option
if down_url is None and upload_file is None and len(cmdl_args) == 1:
    file_or_url = cmdl_args[0]
    # Verify download URL format
    re_down_url = re.compile(r'http://www.divshare.com/download/[\w|-]+')
    p = re_down_url.match(file_or_url)
    if p:
        down_url = file_or_url
    else:
        # Maybe a file?
        if os.path.exists(file_or_url):
            upload_file = file_or_url
        else:
            sys.exit('Error: URL does not seem to be a divshare download URL or file doesnot exist. \n')
elif len(cmdl_args) > 1 or (down_url is None and upload_file is None):
    cmdl_parser.print_help()
    sys.exit(exit_failure)

if down_url:
    downloader(down_url)
elif upload_file:
    host = "www.divshare.com"
    print("Uploading %s to %s, Please wait ..." % (os.path.basename(upload_file), host))
    uploader(host, upload_file)
