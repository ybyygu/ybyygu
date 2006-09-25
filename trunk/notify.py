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
        

def filterMail():
    import re
    import email.Header

    mail_from = ""
    mail_subject = ""

    lines = ''.join(sys.stdin.readlines())
    print lines,

    if lines:
        mail = email.message_from_string(lines)
        mail_subject=email.Header.decode_header(mail['subject'])[0][0]
        subcode = email.Header.decode_header(mail['subject'])[0][1]
        mail_subject = safeEncode(mail_subject, subcode)
        if mail_subject == '':
            mail_subject = 'No Subject'
        
        mail_from = email.Header.decode_header(mail['from'])[0][0]
        subcode = email.Header.decode_header(mail['from'])[0][1]
        mail_from = safeEncode(mail_from, subcode)

        rexMailFrom = re.compile(r'^([^<]*)<([^<]+>)')
        if rexMailFrom.match(mail_from):
            mail_from = rexMailFrom.match(mail_from).groups()[0].strip()
            if mail_from == '' or mail_from == '""':
                mail_from = rexMailFrom.match(mail_from).groups()[1].strip()
        return mail_from, mail_subject
    else:
        return None


if __name__ == "__main__":
    os.system("beep -f 1000 -n -f 2000 -n -f 1500")

    dbus_var = "DBUS_SESSION_BUS_ADDRESS"
    if not os.environ.get(dbus_var):
        user = os.popen("/usr/bin/whoami").read().strip()
        pid = os.popen("pgrep -u %s gnome-session" % user).read().strip()
        fp = open("/proc/%s/environ" % pid, 'r')
        txt = os.popen("grep -z %s /proc/%s/environ" % (dbus_var,pid) ).read().strip()[:-1]
        os.putenv(dbus_var, txt[len(dbus_var + "="):])
        fp.close()
         
    notify = NotifyMail()
    res = filterMail()
    if res:
        (f, s) = res
        notify.notifyMail(f,s)

    sys.exit(0)
