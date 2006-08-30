#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  python-eyed3
#         NOTES:  ---
#        AUTHOR:  ybyygu 
#       VERSION:  0.1
#       CREATED:  2006-7-18
#      REVISION:  ---
#===============================================================================#


from eyeD3 import *
import getopt

def usage():
   print """Usage: %s [options] [filename]
Options:
   -h, --help    print this help message
   -d, --dry-run print the converted tags without changing any files
   
id3convert is a simple python script for coverting mp3 id3 tags into Unicode
UTF-8 encoding, you can pass it MP3 files to covert any MP3 files.

NOTE: RUN THIS ON YOUR OWN RISK!""" % sys.argv[:1].pop()
   sys.exit(2)

def convert(dry_run, lists):
    for f in lists:
        tag = eyeD3.Tag()
        try:
            tag.link(f,ID3_V1)
            artist = False
            album = False
            title = False
            artist = tag.getArtist().encode('iso8859-1').decode('gbk')
            album = tag.getAlbum().encode('iso8859-1').decode('gbk')
            title = tag.getTitle().encode('iso8859-1').decode('gbk')
        except:
            print "What? Error?"
            continue

        if artist:
            print "artist: " + artist
            if not dry_run:
                tag.setArtist(artist)
        if album:
            print "album: " + album
            if not dry_run:
                tag.setAlbum(album)
        if title:
            print "title: " + title
            if not dry_run:
                tag.setTitle(title)
        if dry_run:
            continue
        tag.setVersion(ID3_V2_4)
        tag.setTextEncoding(UTF_16_ENCODING)
        tag.update(ID3_V2_4)
        tag.remove(ID3_V1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                 "dh",
                                 ["dry-run", "help"])
    except getopt.GetoptError:
        usage()
    
    dry_run = False
    for opt, arg in opts:
        if opt in ("-d", "--dry-run"):
            dry_run = True
        elif opt in ("-h", "--help"):
            usage()
    if args:
        convert(dry_run, args)
    else:
        print "Please specify at least one MP3 file."

