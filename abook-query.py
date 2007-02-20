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
#       CREATED:  
#      REVISION:  ---
#===============================================================================#
import os
import sys
from sys import stderr, stdout
import base64
import sqlite
import re
import getopt

class TSectionFields:
    def __init__(self):
        self.__data = []
        self.__tags = ('Email', 'IM', 'Phone', 'Mobile', 'Pager', 'Fax', 'Company', 'Title', 'Other')

    def add(self, tag, value):
        if tag in self.__tags and value != '':
            self.__data.append((tag, value))
    
    def __getitem__(self, index):
        return self.__data[index]

    def __len__(self):
        return len(self.__data)

class TContactSection:
    def __init__(self, sectionName = ''):
        self.__fs = '\1'
        self.Fields = TSectionFields()
        self.Address = ''
        self.SectionName = sectionName

    def addField(self, tag, value):
        if tag in self.__tags and value != '':
            self.Fields.add(tag, value)

class TContact:
    def __init__(self):
        self.__data = {}
        self.__tags = ('FullName', 'NickName', 'PrimEmail', 'Notes')
        for t in self.__tags:
            self.__data[t] = ''

    def getFullName(self):
        return self.__data['FullName']
    def setFullName(self, fullname):
        if fullname != '':
            self.__data['FullName'] = fullname
    FullName = property(getFullName, setFullName, None, None)

    def getNickName(self):
        return self.__data['NickName']
    def setNickName(self, nickname):
        if nickname != '':
            self.__data['NickName'] = nickname
    NickName = property(getNickName, setNickName, None, None)

    def getPrimEmail(self):
        return self.__data['PrimEmail']
    def setPrimEmail(self, email):
        if email != '':
            self.__data['PrimEmail'] = email
    PrimEmail = property(getPrimEmail, setPrimEmail, None, None)
       
    def getNotes(self):
        return self.__data['Notes']
    def setNotes(self, notes):
        if notes != '':
            self.__data['Notes'] = notes
    Notes = property(getNotes, setNotes, None, None)


contact = TContact()
contact.FullName = 'Good'
contact.Notes = 'notes'
sys.exit(0)

class contactSection:
    def __init__(self, sectionName = ''):
        self.SectionName = sectionName
        self.FS = '\1'
        self.Fields = []

        self.TagItems = ('Name', 'Email', 'NickName', 'Notes', 'IM', 'Fax', 'Mobile', 'Phone', 'Pager', 'Title', 'Company', 'Address')

    def addField(self, tag, value):
        if tag in self.TagItems: 
            self.Fields.append((tag, value))
        else:
            pass

    def getField(self, tag):
        r = []
        if tag in self.TagItems:
            for t,v in self.Fields:
                if t == tag:
                    r.append(v)
        return r

    def removeField(self, index):
        del self.Fields[index]

    def dump(self):
        print "[ %s ]" % self.SectionName
        for t,v in self.Fields:
            if v != '':
                print '%s= %s' % (t, v)

    def adaptSection(self):
        """\
        convert section to string representation
        """
        str = self.SectionName
        for t,v in self.Fields:
           str += "%s%s: %s" % (self.FS, t, v)
        return str

    def convertSection(self, sectionString):
        self.Fields = []
        s = sectionString.split(self.FS)
        self.SectionName = s[0]
        for tv in s[1:]:
            t,v = re.split(': ', tv , 1)
            self.addField(t, v)

    def isEmpty(self):
        for t,v in self.Fields:
            if v != '':
                return False
        return True

class contact:
    def __init__(self, name = '', email = '', notes = ''):
        self.Sections = {}
        self.FS = '\2'
        section = contactSection()
        section.addField('Name', name)
        section.addField('Email', email)
        section.addField('Notes', notes)
        section.SectionName = 'Default'
        self.addSection(section)

    def isEmpty(self):
        for t in self.TagItems:
            if self.PrimInfo[t] != '':
                return False
        for s in self.Sections.keys():
            if not self.Sections[s].isEmpty():
                return False
        return True

    def addSection(self, section):
        if not section.isEmpty():
            self.Sections[section.SectionName] = section

    def removeSection(self, sectionName):
        if self.Sections.has_key(sectionName):
            del self.Sections[sectionName]
    
    def dump(self):
        print '='*70
        for s in self.Sections.keys():
            self.Sections[s].dump()
            print '-'*70

    def adaptContact(self):
        """\
        convert contact to string representation
        """
        str = ''
        for k in self.Sections.keys():
            str += "%s%s" % (self.Sections[k].adaptSection(), self.FS)
        return str.strip(self.FS)

    def convertContact(self, contactString):
        """\
        convert from string to contact
        """
        slist = contactString.split(self.FS)
        for s in slist:
            section = contactSection()
            section.convertSection(s)
            self.addSection(section)
    
class addressBook:
    def __init__(self, database):
        self.ContactList = []
        self.Database = database
        self.con = sqlite.connect(self.Database)
        self.cur = self.con.cursor()

    def addContact(self, contact):
        self.ContactList.append(contact)
    
    def removeContact(self, contact):
        if contact in self.ContactList:
            del self.ContactList[self.ContactList.index(contact)]

    def dump(self):
        for contact in self.ContactList:
            contact.dump()
    
    def adaptAddress(self):
        for contact in self.ContactList:
            print contact.adaptContact()
    
    def writeDatabase(self):
        self.cur.execute('create table addressbook (id integer primary key, contact varchar)')
        for c in self.ContactList:
            self.cur.execute("insert into addressbook (id, contact) values(NULL, %s)", c.adaptContact())
        self.con.commit()

    def readDatabase(self):
        self.cur.execute('select * from addressbook')
        for i,c in self.cur.fetchall():
            acontact = contact()
            acontact.convertContact(c)
            acontact.dump()
         
    def queryDatabase(self, queryString):
        queryString = '%' + queryString.strip() +'%'
        self.cur.execute('select * from addressbook where contact like %s', queryString)
        for i,c in self.cur.fetchall():
            acontact = contact()
            acontact.convertContact(base64.decodestring(c))
            acontact.dump()
        
        
    def muttQuery(self, queryString):
        queryString = '%' + queryString.strip() +'%'
        self.cur.execute('select * from addressbook where contact like %s', queryString)
        qr = []
        for i,c in self.cur.fetchall():
            acontact = contact()
            acontact.convertContact(c)
            emails = []
            for s in acontact.Sections.keys():
                emails += acontact.Sections[s].getField('Email')
            for e in emails:
                qr.append((e, acontact.Sections['Default'].getField('Name')))
        print "匹配 %s项" % len(qr)
        for e,n in qr:
            print "%s\t%s\t%s" % (e, n[0], 'Address book')
    
    def importFromLdifFile(self, fileName):
        try:
            txt = open(fileName).read().split('\n\n')
        except:
            return 1

        for i in range( len(txt) ):
            if len( txt[i] ) == 0:
                del txt[i]
            else:
                ldifList = [ f.split(': ') for f in txt[i].split('\n') ]
                for t,v in ldifList:
                    if t[-1] == ':':
                        ldifList[ldifList.index([t,v])] = t[:-1], base64.decodestring(v)
                ldifDict = dict( ldifList )
                
                name = ''
                mail = ''
                notes = ''
                if ldifDict.has_key('cn'):
                    name = ldifDict['cn']
                if ldifDict.has_key('mail'):
                    mail = ldifDict['mail']
                if ldifDict.has_key('notes'):
                    notes = ldifDict['description']
                if name == '':
                    name = 'Noname'
                c = contact(name, mail, notes)

                ps = contactSection('Personal')
                if ldifDict.has_key('mozillaNickname'):
                    ps.addField('NickName', ldifDict['mozillaNickname'])
                if ldifDict.has_key('mobile'):
                    ps.addField('Mobile', ldifDict['mobile'])
                if ldifDict.has_key('homePhone'):
                    ps.addField('Phone', ldifDict['homePhone'])
                if ldifDict.has_key('street'):
                    ps.addField('Address',  ldifDict['street'])
                ws = contactSection('Work')
                if ldifDict.has_key('telephoneNumber'):
                    ws.addField('Phone', ldifDict['telephoneNumber'])
                if ldifDict.has_key('fax'):
                    ws.addField('Fax', ldifDict['fax'])
                c.addSection(ps)
                c.addSection(ws)
                
                self.addContact(c)

        return 0
        

def adapt_contact( contact ):
    pass
def convert_contact( string ):
    pass

def usage():
    print 'sys.argv[0]'

#==========================================================================
# MAIN PROGRAM
#==========================================================================
def main (argv=None):
    if argv is None:  argv = sys.argv
    
    # Parse the command line arguments
    try:
        opts, args = getopt.getopt(argv[1:], "hq:md:", ["help", "query=", "mutt", "database="])
    except:
        print "Invalid command-line argument"
        usage()
        return 1

    # Process the switches
    query = None
    mutt = False
    database = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            return 0
        elif o in ("-q", "--query"):
            query = a
        elif o in ("-m", "--mutt"):
            mutt = True

    if not database:
        database = os.environ['HOME'] + '/etc/address/abook.db'

    try:
        open(database, "rt").close()
    except:
        print >> stderr, "can't access %s" % address
        return 1

    myabook = addressBook(database)
    # myabook.importFromLdifFile('addressbook.ldif')
    #myabook.writeDatabase()
    #myabook.dump()
    if query and mutt:
        myabook.muttQuery(query)
    if query and not mutt:
        myabook.queryDatabase(query)

if (__name__ == "__main__"):
    main()
