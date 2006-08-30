#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#==========================================================================
# Original "Mindy" copyright: Kumaran Santhanam <kumaran@alumni.stanford.org>
#
# Subsequent butchery: Mike Hoye <mhoye@off.net>
#
# Just to be absolutely clear about this, Santhanam did all the heavy lifting
# here. This is a straight-up pattern-recognition hack; I don't even speak
# python.
#
#--------------------------------------------------------------------------
# Project : demork - takes in Mork files, spits out XML(ish)
# File    : demork.py
# Version : 0.1
#--------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# Version 2 (1991) as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For the full text of the GNU General Public License, refer to:
#   http://www.fsf.org/licenses/gpl.txt
#
# For alternative licensing terms, please contact the author.
#--------------------------------------------------------------------------
#
#  This widget has hardcoded XML entity tags in places that make it pretty
#  much specifically meant for the Mozilla history.db file. They're tagged
#  with a "#HDBXML" comment nearby, for easy searching and replacing if
#  you intend to do anything else with this and want semantics that make
#  some kind of sense. 
#
#==========================================================================
# modified by ybyygu at 2006-7-22
# use this python script to do a mutt query

#==========================================================================
# IMPORTS
#==========================================================================
import sys
import re
import getopt
import os

from sys import stdin, stdout, stderr


#==========================================================================
# GLOBALS
#==========================================================================
VERSION = "0.2"
PROGRAM = "mab_query.py"

#==========================================================================
# FUNCTIONS
#==========================================================================
def usage ():
    print
    print "%s: use this script to do a mutt address query." % PROGRAM
    print
    print "Version %s, (c) ybyygu, 2006." % VERSION
    print "Based on a Demork.py (c) 2005 Mike Hoye."
    print "Please visit here:"
    print "http://off.net/~mhoye/moz/demork.py"
    print
    print "usage: %s [-a MAB_AddressBook] Query_Str" % PROGRAM
    print

#==========================================================================
# DATABASE
#==========================================================================
class Database:
    def __init__ (self):
        self.cdict  = { }
        self.adict  = { }
        self.tables = { }

class Table:
    def __init__ (self):
        self.id     = None
        self.scope  = None
        self.kind   = None
        self.rows   = { }

class Row:
    def __init__ (self):
        self.id     = None
        self.scope  = None
        self.cells  = [ ]

class Cell:
    def __init__ (self):
        self.column = None
        self.atom   = None


#==========================================================================
# UTILITIES
#==========================================================================
def invertDict (dict):
    idict = { }
    for key in dict.keys():
        idict[dict[key]] = key
    return idict

def hexcmp (x, y):
    try:
        a = int(x, 16)
        b = int(y, 16)
        if a < b:  return -1
        if a > b:  return 1
        return 0

    except:
        return cmp(x, y)


#==========================================================================
# MORK INPUT
#==========================================================================
def escapeData (match):
    return match.group() \
               .replace('\\\\n', '$0A') \
               .replace('\\)', '$29') \
               .replace('>', '$3E') \
               .replace('}', '$7D') \
               .replace(']', '$5D')

pCellText   = re.compile(r'\^(.+?)=(.*)')
pCellOid    = re.compile(r'\^(.+?)\^(.+)')
pCellEscape = re.compile(r'((?:\\[\$\0abtnvfr])|(?:\$..))')

backslash = { '\\\\' : '\\',
              '\\$'  : '$',
              '\\0'  : chr(0),
              '\\a'  : chr(7),
              '\\b'  : chr(8),
              '\\t'  : chr(9),
              '\\n'  : chr(10),
              '\\v'  : chr(11),
              '\\f'  : chr(12),
              '\\r'  : chr(13) }

def unescapeMork (match):
    s = match.group()
    if s[0] == '\\':
        return backslash[s]
    else:
        return chr(int(s[1:], 16))

def decodeMorkValue (value):
    global pCellEscape
    return pCellEscape.sub(unescapeMork, value)

def addToDict (dict, cells):
    for cell in cells:
        eq  = cell.find('=')
        key = cell[1:eq]
        val = cell[eq+1:-1]
        dict[key] = decodeMorkValue(val)

def getRowIdScope (rowid, cdict):
    idx = rowid.find(':')
    if idx > 0:
        return (rowid[:idx], cdict[rowid[idx+2:]])
    else:
        return (rowid, None)
        
def delRow (db, table, rowid):
    (rowid, scope) = getRowIdScope(rowid, db.cdict)
    if scope:
        rowkey = rowid + "/" + scope
    else:
        rowkey = rowid + "/" + table.scope

    if table.rows.has_key(rowkey):
        del table.rows[rowkey]

def addRow (db, table, rowid, cells):
    global pCellText
    global pCellOid

    row = Row()
    (row.id, row.scope) = getRowIdScope(rowid, db.cdict)

    for cell in cells:
        obj = Cell()
        cell = cell[1:-1]

        match = pCellText.match(cell)
        if match:
            obj.column = db.cdict[match.group(1)]
            obj.atom   = decodeMorkValue(match.group(2))

        else:
            match = pCellOid.match(cell)
            if match:
                obj.column = db.cdict[match.group(1)]
                obj.atom   = db.adict[match.group(2)]

        if obj.column and obj.atom:
            row.cells.append(obj)

    if row.scope:
        rowkey = row.id + "/" + row.scope
    else:
        rowkey = row.id + "/" + table.scope

    if table.rows.has_key(rowkey):
        print >>stderr, "ERROR: duplicate rowid/scope %s" % rowkey
        print >>stderr, cells

    table.rows[rowkey] = row
    
def inputMork (data):
    # Remove beginning comment
    pComment = re.compile('//.*')
    data = pComment.sub('', data, 1)

    # Remove line continuation backslashes
    pContinue = re.compile(r'(\\(?:\r|\n))')
    data = pContinue.sub('', data)

    # Remove line termination
    pLine = re.compile(r'(\n\s*)|(\r\s*)|(\r\n\s*)')
    data = pLine.sub('', data)

    # Create a database object
    db          = Database()

    # Compile the appropriate regular expressions
    pCell       = re.compile(r'(\(.+?\))')
    pSpace      = re.compile(r'\s+')
    pColumnDict = re.compile(r'<\s*<\(a=c\)>\s*(?:\/\/)?\s*(\(.+?\))\s*>')
    pAtomDict   = re.compile(r'<\s*(\(.+?\))\s*>')
    pTable      = re.compile(r'\{-?(\d+):\^(..)\s*\{\(k\^(..):c\)\(s=9u?\)\s*(.*?)\}\s*(.+?)\}')
    pRow        = re.compile(r'(-?)\s*\[(.+?)((\(.+?\)\s*)*)\]')

    pTranBegin  = re.compile(r'@\$\$\{.+?\{\@')
    pTranEnd    = re.compile(r'@\$\$\}.+?\}\@')

    # Escape all '%)>}]' characters within () cells
    data = pCell.sub(escapeData, data)

    # Iterate through the data
    index  = 0
    length = len(data)
    match  = None
    tran   = 0
    while 1:
        if match:  index += match.span()[1]
        if index >= length:  break
        sub = data[index:]

        # Skip whitespace
        match = pSpace.match(sub)
        if match:
            index += match.span()[1]
            continue

        # Parse a column dictionary
        match = pColumnDict.match(sub)
        if match:
            m = pCell.findall(match.group())
            # Remove extraneous '(f=iso-8859-1)'
            if len(m) >= 2 and m[1].find('(f=') == 0:
                m = m[1:]
            addToDict(db.cdict, m[1:])
            continue

        # Parse an atom dictionary
        match = pAtomDict.match(sub)
        if match:
            cells = pCell.findall(match.group())
            addToDict(db.adict, cells)
            continue

        # Parse a table
        match = pTable.match(sub)
        if match:
            id = match.group(1) + ':' + match.group(2)

            try:
                table = db.tables[id]

            except KeyError:
                table = Table()
                table.id    = match.group(1)
                table.scope = db.cdict[match.group(2)]
                table.kind  = db.cdict[match.group(3)]
                db.tables[id] = table

            rows = pRow.findall(match.group())
            for row in rows:
                cells = pCell.findall(row[2])
                rowid = row[1]
                if tran and rowid[0] == '-':
                    rowid = rowid[1:]
                    delRow(db, db.tables[id], rowid)

                if tran and row[0] == '-':
                    pass

                else:
                    addRow(db, db.tables[id], rowid, cells)
            continue

        # Transaction support
        match = pTranBegin.match(sub)
        if match:
            tran = 1
            continue

        match = pTranEnd.match(sub)
        if match:
            tran = 0
            continue

        match = pRow.match(sub)
        if match and tran:
            print >>stderr, "WARNING: using table '1:^80' for dangling row: %s" % match.group()
            rowid = match.group(2)
            if rowid[0] == '-':
                rowid = rowid[1:]

            cells = pCell.findall(match.group(3))
            delRow(db, db.tables['1:80'], rowid)
            if row[0] != '-':
                addRow(db, db.tables['1:80'], rowid, cells)
            continue

        # Syntax error
        print >>stderr, "ERROR: syntax error while parsing MORK file"
        print >>stderr, "context[%d]: %s" % (index, sub[:40])
        index += 1

    # Return the database
    return db

#==========================================================================
# mutt query output
#==========================================================================
def outputMuttQuery (db, query=[]):
    columns = db.cdict.keys()
    columns.sort(hexcmp)

    tables = db.tables.keys()
    tables.sort(hexcmp)

    print "Searching database ...",
    emails = []
    names = []
    for table in [ db.tables[k] for k in tables ]:
        rows = table.rows.keys()
        rows.sort(hexcmp)
        for row in [ table.rows[k] for k in rows ]:
            name = None
            email = None
            semail = None
            got = False
            for cell in row.cells:
                tag, value = cell.column, cell.atom
                if tag == 'DisplayName':
                    name = value
                if tag == 'PrimaryEmail':
                    email = value
                if tag == 'SecondEMail':
                    semail = value
                for q in query:
                    if value.find(q) >=0:
                        got = True
                        break
            if not email :
                continue
            if got:
                emails.append(email)
                if not name:
                    name = email
                names.append(name)
                if semail:
                    emails.append(semail)
                    names.append(name)

    print "匹配 %s项" % len(emails)
    for (e, n) in zip(emails, names):
        print "%s\t%s\t%s" % (e, n, 'Mozilla Address book')

#==========================================================================
# MAIN PROGRAM
#==========================================================================
def main (argv=None):
    if argv is None:  argv = sys.argv

    # Parse the command line arguments
    try:
        opts, args = getopt.getopt(argv[1:], "ha:", ["help", "address"])
    except:
        print "Invalid command-line argument"
        usage()
        return 1

    # Process the switches
    address = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            return 0
        elif o in ("-a", "--address"):
            address = a

    if not address:
        address = os.environ['HOME'] + '/etc/address/abook.mab'

    # auto detect filename
    # address = autodectAddressPath()

    try:
        file = open(address, "rt")
    except:
        print >> stderr, "can't access %s" % address
        return 1
    data = file.read()
    file.close()

    # Determine the file type and process accordingly
    if (data.find('<mdb:mork') >= 0):
        db = inputMork(data)
        outputMuttQuery(db, args)
    else:
        print >> stderr, "unknown file format: %s (I only deal with Mork, sorry)" % filename
        return 1

    # Return success
    return 0


if (__name__ == "__main__"):
    result = main()
    # Comment the next line to use the debugger
    sys.exit(result)
