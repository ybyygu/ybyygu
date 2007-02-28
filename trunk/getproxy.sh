#!/bin/bash
#===============================================================================
#
#         FILE:  getproxy.sh
#
#        USAGE:  ./getproxy.sh 
#
#  DESCRIPTION:  download proxylist from web
#      OPTIONS:  ---none
# REQUIREMENTS:  ---curl, w3m
#        NOTES:  ---add this command to cron job list
#       AUTHOR:   (ybyygu) 
#      CREATED:  2005年11月18日 14时43分06秒 CST
#      UPDATED:  2006 3/14
#===============================================================================

# Where we save the proxylist?
list=$HOME/.proxy/proxylist

temp=$(mktemp)

function download(){
    local url=$1

    local html=$(mktemp)
    curl -s -o $html $url && w3m -dump -T "text/html" $html>>$temp

    if [ -f $html ];then
        rm $html
    fi
}

# hustu online
(download "http://info.hustonline.net/index/proxyshow.aspx") &

# IPCN
(download "http://proxy.ipcn.org/proxylist.html") &

# lqqm
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=1") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=2") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=2") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=4") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=5") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=6") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=7") &
(download "http://lqqm.net/cgi-bin/proxylist?proxytype=1&pageindex=8") &

# CN Proxy
(download "http://www.cnproxy.com/proxyedu1.html") &
(download "http://www.cnproxy.com/proxyedu2.html") &
(download "http://www.cnproxy.com/proxy1.html") &
(download "http://www.cnproxy.com/proxy2.html") &
(download "http://www.cnproxy.com/proxy3.html") &
(download "http://www.cnproxy.com/proxy4.html") &
(download "http://www.cnproxy.com/proxy5.html") &
(download "http://www.cnproxy.com/proxy6.html") &
(download "http://www.cnproxy.com/proxy7.html") &
(download "http://www.cnproxy.com/proxy8.html") &
(download "http://www.cnproxy.com/proxy9.html") &

# wait for background jobs done
wait

egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} *:[0-9]+' $temp|tr -d " "|sort|uniq>/tmp/proxy.list

if [ -f $temp ];then
    rm $temp
fi

# if proxies less than 5, discard it.
count=`cat /tmp/proxy.list|wc -l`
if (($count>5));then
    mv /tmp/proxy.list $list
    ~/bin/checkproxy.sh $list
fi

