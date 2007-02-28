#!/usr/bin/env python 
# An interactive rolodex
 
import string, sys, pickle, cmd
 
class Rolodex(cmd.Cmd):
 
    def __init__(self):
        cmd.Cmd.__init__(self)              # initialize the base class
        self.prompt = "gsg >> "             # customize the prompt
        self.people = {}                    # at first, we know nobody
        #self. = {}                    # at first, we know nobody
 
    def help_add(self): 
        print "Adds an entry (specify a name)"
    def do_add(self, name):
        if name == "": name = raw_input("Enter Name: ")
        phone = raw_input("Enter Phone Number for "+ name+": ")
        self.people[name] = phone           # add phone number for name
 
    def help_find(self):
        print "Find an entry (specify a name)"
    def do_find(self, name):
        if name == "": name = raw_input("Enter Name: ")
        if self.people.has_key(name):
            print "The number for %s is %s." % (name, self.people[name])
        else:
            print "We have no record for %s." % (name,)
 
    def help_list(self):
        print "Prints the contents of the directory"
    def do_list(self, line):        
        names = self.people.keys()         # the keys are the names
        if names == []: return             # if there are no names, exit
        names.sort()                       # we want them in alphabetic order
        print '='*41
        for name in names:
           print string.rjust(name, 20), ":", string.ljust(self.people[name], 20)
        print '='*41
 
    def help_EOF(self):
        print "Quits the program"
    def do_EOF(self, line):
        sys.exit()
 
    def help_save(self):
        print "save the current state of affairs"
    def do_save(self, filename):
        if filename == "": filename = raw_input("Enter filename: ")
        saveFile = open(filename, 'w')
        pickle.dump(self.people, saveFile)
 
    def help_load(self):
        print "load a directory"
    def do_load(self, filename):
        if filename == "": filename = raw_input("Enter filename: ")
        saveFile = open(filename, 'r')
        self.people = pickle.load(saveFile) # note that this will override
                                            # any existing people directory
 
if __name__ == '__main__':               # this way the module can be
    rolo = Rolodex()                     # imported by other programs as well
    rolo.cmdloop()                             
