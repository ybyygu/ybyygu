#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#===============================================================================#
#
#  answer queries for mutt from kabc file
#
#===============================================================================#
import sys
import os
import re

KDE_ADDRESSBOOK=os.environ['HOME'] + '/.kde/share/apps/kabc/std.vcf'

# String to identify Mail address entrys in vcards
MAIL_INIT_STRING = r'EMAIL[^:]*:'
# String to identify Name entrys in vcards
NAME_INIT_STRING = r'FN:'

class vcard:
    def __init__(self, email, name):
        self.email = str(email)
        self.name = str(name)

def parseFile(file_name):
    if not os.access(file_name, os.F_OK|os.R_OK):
        print 'Cannot open file ' , file_name
        sys.exit(1)
    try:
        cf = open(file_name)
        cards = cf.read()
    finally:
        cf.close()
    re_vcard = re.compile(r'BEGIN:VCARD.*?END:VCARD', re.DOTALL)
    vcards = re_vcard.findall(cards)
    return vcards

def getEmails(vcard_str):
    mail_re = re.compile(r'^' + MAIL_INIT_STRING + r'(.*)$')
    tmp_mails = []
    for line in vcard_str.split('\n'):
        if line[:5] == 'EMAIL':
            tmp_mails.append(mail_re.search(line).group(1).strip())
    return tmp_mails
    
def getMatches(vcards, search_string):
    lines = []
    search_re = re.compile(search_string, re.I)
    name_re = re.compile(r'^' + NAME_INIT_STRING + r'(.*)$', re.MULTILINE)
    for loop_vcard in vcards:
        if search_re.search(loop_vcard):
            tmp_mails = getEmails(loop_vcard)
            if name_re.search(loop_vcard) != None:
                tmp_name = name_re.search(
                    loop_vcard).group(1).replace(';', ' ').strip()
            else:
                tmp_name = 'Noname'
            for mail in tmp_mails:
                my_vcard = vcard(mail, tmp_name)
                lines.append(my_vcard)
    return lines

def safeEncode(string, encode):
    if not encode :
        encode = "GBK"
    try:
        res = unicode(string, encode)
    except UnicodeDecodeError:
        try:
            res = unicode(string, "UTF8")
        except:
            res = "Can't encode string."

    return res 

def parsePipedEmail():
    """\
    return name, mail, nickname 
    """
    import re
    import email.Header
    
    name = ''
    mail = ''

    line = sys.stdin.readline()
    while line.strip():
        if re.compile(r'^From: ').match(line):
            line = line.replace('"', '')
            if line[6:8] == '=?':
                header = email.Header.decode_header(line)
                string = header[1][0]
                subcode = header[1][1]
                name = safeEncode(string, subcode)
                mail = header[2][0]
                mail = mail.lstrip(' <')
                mail = mail.strip('> ')
            elif line.find('<') != -1:
                ne = line[6:].split(' <')
                name = ne[0]
                mail = ne[1].strip('> \n')
            else:
                fm = line.split(': ')
                mail = fm[1].strip()
        line = sys.stdin.readline()
    
    if name == '' and mail:
        name = mail[0:mail.find('@')]
    nickname = mail[0:mail.find('@')]

    return name, mail, nickname

def addContactToKabc(name, mail, nickname):
    if mail == '':
        return 1

    print 'Add this %s <%s> to your addressbook? (Y/n)' % (name, mail),
    fin = open('/dev/tty')
    answer = fin.readline()
    if answer.strip() == '' or answer.strip().lower() == 'y':
        print 'Full Name: [%s]' % name,
        answer = fin.readline()
        if answer.strip():
            name = answer.strip()
        
        print 'Nick Name: [%s]' % nickname,
        answer = fin.readline()
        if answer.strip():
            nickname = answer.strip()
    else:
        return 0
    try:
        name = name.encode('utf-8')
    except:
        pass

    vcard = 'BEGIN:VCARD\nEMAIL:%s\nFN:%s\nNICKNAME:%s\nVERSION:3.0\nEND:VCARD\n' % (mail, name, nickname)
    fout = open(KDE_ADDRESSBOOK, 'a')
    fout.write(vcard)


def usage():
    print '%s:' % sys.argv[0]
    print '-q | --query query_string'
    print '\tdo a mutt query from kabc addressbook'
    print '-e | --edit'
    print '\tedit in kaddressbook'
    print '-a | --add'
    print '\tadd contact from mutt'

#==========================================================================
# MAIN PROGRAM
#==========================================================================
def main (argv=None):
    import getopt

    # Parse the command line arguments
    if argv is None:  argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "hq:ae", ["help", "query=", "add", 'edit'])
    except:
        print "Invalid command-line argument"
        usage()
        return 1

    # Process the switches
    query = None
    add = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            return 0
        elif o in ("-q", "--query"):
            query = a
        elif o in ("-a", "--add"):
            add = True
        elif o in ('-e', '--edit'):
            try:
                os.system('kaddressbook >& /dev/null')
            except:
                pass
        else:
            usage()
            return 1

    if add:
        name, mail, nickname = parsePipedEmail()
        addContactToKabc(name, mail, nickname)
        return 0
    elif query:
        vcards = parseFile(KDE_ADDRESSBOOK)
        lines = getMatches(vcards, query)
        print 'Searched ' + str(vcards.__len__()) + ' vcards, found ' + str(
            lines.__len__())+ ' matches.'
        for line in lines:
            print '%s\t%s\t%s' % (line.email, line.name, 'KAddressbook')

        if lines.__len__() > 0:
            return 0
        else:
            return 1        

if (__name__ == "__main__"):
    main()


