#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import dbus

class NotifyMail:
    def __init__(self):
        self.bus = dbus.SessionBus()
        obj = self.bus.get_object('org.freedesktop.Notifications',
                                    '/org/freedesktop/Notifications')
        self.notif = dbus.Interface(obj, 'org.freedesktop.Notifications')
        if self.notif is None:
            raise dbus.dbus_bindings.DBusException()

    def notify(self,text,event_type='Incoming Mail',timeout=10, path_to_image='gtk-dialog-info'):
        id = self.notif.Notify(dbus.String('NotifierTest'),
                    dbus.UInt32(0),
                    dbus.String(path_to_image),
                    dbus.String(event_type),
                    dbus.String(text),
                    dbus.String(''),
                    {},
                     dbus.UInt32(timeout*1000))
    def notifyMail(self, mail_from, mail_subject):
        text = "From:      %s\nSubject:  %s" %(mail_from, mail_subject)
        self.notify(text, timeout=0)


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
        

def filterMail(lines):
    import re
    import email
    import email.Header

    mail_from = ""
    mail_subject = ""

    if lines:
        mail = email.message_from_string(lines)
        mail_subject=email.Header.decode_header(mail['subject'])[0][0]
        subcode = email.Header.decode_header(mail['subject'])[0][1]
        mail_subject = safeEncode(mail_subject, subcode)
        if mail_subject == '':
            mail_subject = 'No Subject'
        
        header = mail['from'].replace('"', '')
        mail_from = email.Header.decode_header(header)[0][0]
        subcode = email.Header.decode_header(header)[0][1]
        mail_from = safeEncode(mail_from, subcode)
        rexMailFrom = re.compile(r'^([^<]*)<([^<]+>)')
        if rexMailFrom.match(mail_from):
            mail_from = rexMailFrom.match(mail_from).groups()[0].strip()
            if mail_from == '' or mail_from == '""':
                mail_from = rexMailFrom.match(mail_from).groups()[1].strip()
        return mail_from, mail_subject
    else:
        return None

def autostart():
    """\
    setup an autostart cmd
    """
    try:
        os.mkdir(os.path.expanduser('~/.config'))
        os.mkdir(os.path.expanduser('~/.config/autostart'))
    except:
        pass
    
    try:
        file = open(os.path.expanduser('~/.config/autostart/notify-update-dbus.desktop'), 'w')
    except exceptions.IOError:
        return 1

    file.writelines('[Desktop Entry]\n')
    file.writelines('Name=snotify-dubs\n')
    file.writelines('Encoding=UTF-8\n')
    file.writelines('Version=1.0\n')
    file.writelines('Exec=%s\n' % sys.argv[0])
    file.writelines('X-GNOME-Autostart-enabled=true')
    return 0

def updateDBUSVar():
    dbus_var = "DBUS_SESSION_BUS_ADDRESS"
    if not os.getenv(dbus_var):
        try:
            txt = open(os.path.expanduser('~/.dbus')).read().strip()
            os.putenv(dbus_var, txt)
        except exceptions.IOError:
            autostart()
            return 1
    else:
        file = open(os.path.expanduser('~/.dbus'), 'w')
        file.writelines(os.getenv(dbus_var))
        file.close()

    return 0

def main():
    from getopt import getopt

    if len(sys.argv) == 1:
        lines = ''.join(sys.stdin.readlines())
        print lines,

        try:
            # audio notification
            os.system('beep -f 1000 -n -f 2000 -n -f 1500')
            
            # followed by a visual notification
            if updateDBUSVar() == 0:
                res = filterMail(lines)
                notify = NotifyMail()
                if res:
                    (f, s) = res
                    notify.notifyMail(f,s)
        except:
            pass
    else:
        try:
            opts, args = getopt(sys.argv[1:], "t", ["test"])
        except getopt.GetoptError:
            sys.exit(2)

        for o, a in opts:
            if o in ['-t', '--test']:
                updateDBUSVar()
    

if __name__ == "__main__":
    main()
