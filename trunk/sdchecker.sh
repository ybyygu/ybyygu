#!/bin/bash
# This script would help you finding literature_proxy in proxylist
# What you need: curl(>7.12.3), bash
# Written by ybyygu_at_yahoo.com.cn
# Created at 2005/7/6
# Last updated at 2006-3-26

#------------------------------------------------------------------------#
TIMEOUT=20                      # check timeout
MAX_CONNECTIONS=50              # max concurrent connections
#------------------------------------------------------------------------#

#
# Wiley InterScience
#
checkWiley() 
{
    local host=$1
    local port=$2
    
    local url='http://www3.interscience.wiley.com/cgi-bin/home'
    local cookie=$(mktemp)

    # we need cookie
    curl -N -s -m $TIMEOUT -x "$host:$port" -L -c "$cookie" -o /dev/null "$url"
    if [ -z "$(cat $cookie)" ]; then
        rm $cookie >/dev/null
	return 1
    fi
    
    # with this cookie, we can view wiley licenses
    local url='http://www3.interscience.wiley.com/cgi-bin/licenses'
    local check_str=$(curl -N -s -m $TIMEOUT -x "$host:$port" -b "$cookie" -L "$url"|grep -o 'Seamless Access')

    [[ -f $cookie ]] && rm $cookie
    [[ "$check_str" == "" ]] && exit
    
    echo -ne "${host}:${port}\r\n"
} 

#
# check proxy by pdf file test
# 
checkProxy()
{
    local host=$1
    local port=$2
    local url=$3
    local state=$(mktemp)
     
    # check with content_type 
    local resp=$(curl -N  -w %{content_type} -s -m 10  -x "$host:$port" -L -c /dev/null -o $state $url)
    [[ "$resp" != 'application/pdf' ]] && return 1
    resp=$(head -n 1 $state|hexdump|grep "5025 4644 312d")
    if [ -n "$resp" ]; then
        echo -ne "${host}:${port}\r\n" 
    fi
}

#
# Royal Society of Chemistry
#
checkRSC()
{
    url='http://pubs.rsc.org/ej/P1/2002/b205227j.pdf?&Yr=2002&VOLNO=%20&Fp=1963&Ep=1967&JournalCode=P1&Iss=17'
    
    checkProxy $1 $2 $url	
}


#
# Science Direct
#
checkSD()
{
    url='http://www.sciencedirect.com/science?_ob=MImg&_imagekey=B6WHJ-484VB1G-3-1J&_cdi=6852&_user=2352656&_orig=search&_coverDate=04%2F01%2F2003&_qd=1&_sk=997849998&view=c&wchp=dGLbVzb-zSkzS&md5=21e57b605905a50a3073e23417073eea&ie=/sdarticle.pdf'
    checkProxy $1 $2 $url
}

#
# thieme connect
#
checkThieme()
{
    url='http://www.thieme-connect.com/ejournals/pdf/synthesis/doi/10.1055/s-2003-42482.pdf'

    checkProxy $1 $2 $url
}

#
# Nature magazine
#
checkNature()
{
    url='http://www.nature.com/nature/journal/v440/n7082/pdf/nature04554.pdf'

    checkProxy $1 $2 $url
}

#
# Science magazine
#
checkScience()
{
    url='http://www.sciencemag.org/cgi/reprint/281/5377/666.pdf'

    checkProxy $1 $2 $url
}

#
# American Chemical Society
#
checkACS()
{
    local host=$1
    local port=$2

    local url='http://pubs.acs.org/cgi-bin/article.cgi/jpcbfk/2000/104/i09/pdf/jp993194h.pdf'
    local resp=$(curl -N -s -m $TIMEOUT -x "$host:$port" -L -c /dev/null "$url")
    local str="Click here if your browser does not automatically redirect you"
    
    resp=$(echo "$resp" | grep "$str")
    if [ "$resp" != "" ]; then
        url=$(echo "$resp"|egrep -o 'http://[^"]+')
        checkProxy "$host" "$port" "$url"
    fi
}

#
# ISI Web of Science
# 
checkISI()
{
    local host=$1
    local port=$2

    local url='http://isi01.isiknowledge.com/portal.cgi/'
    local cookie=$(mktemp)

    local resp=$(curl -N -s -m $TIMEOUT -x "$host:$port" -L -c "$cookie" "$url")
    url=$( echo "$resp" | grep -o 'http[^"]*' | tail -n 1) 

    resp=$(echo "$url"|grep 'portal\.cgi?SID=')
    if [ "$resp" == "" ]; then
        rm $cookie >/dev/null
	return 1
    fi

    resp=$(curl -N -s -m 60 -x "$host:$port" -L -b "$cookie" "$url")

    local str=$(echo $resp|grep "Web of Science")
    if [ "$str" != "" ]; then
         echo -ne "$host:$port\r\n"
    fi

    [[ -f $cookie ]] && rm $cookie
}

#
# JSTOR
#
checkJSTOR()
{
    local host=$1
    local port=$2

    local url='http://www.jstor.org/browse'
    local resp=$(curl -N -s -m $TIMEOUT -x "$host:$port" -L -c /dev/null "$url")
    local str="JSTOR Journals Browser"
    
    resp=$(echo "$resp" | grep "$str")
    if [ "$resp" != "" ]; then
        echo -ne "${host}:${port}\r\n"
    fi
}

#------------------------------------------------------------------------# 
#                      things about progress bar                         #
#------------------------------------------------------------------------# 
indicator()
{
    local cols=$(tput cols)
    tput cub $cols
    cols=$(echo "scale=4; 0.65*$cols"|bc)
    cols=${cols%.*}         # trim decimal fraction

    local cur_pos=$(echo "$cols*$1/$2"|bc)
    cur_pos=${cur_pos%.*}
     
    echo -en "$1 of $2\t["
    for i in $(seq $cur_pos); do
        echo -n "="
    done
    local spaces=$(($cols-$cur_pos-2))
    for i in $(seq $spaces); do
        echo -n " "
    done

    if (($spaces!=0)); then
        echo -n "] checking..."
    else
        echo -n "] done       "
    fi
} 


#------------------------------------------------------------------------#
#                           MAIN ROUTINE                                 #
#------------------------------------------------------------------------#

# help screen
if [ $# != 1 ]; then
    echo "Usage: $(basename $0) <proxylist-file>"
    echo "proxylist format - proxy_host:proxy_port"
    exit 0
fi

# prepare proxylist
if [ -f "$1" ]; then
    list=$(mktemp)
    egrep -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+' "$1"|sort|uniq >$list
    declare -i counts=$(cat "$list"|wc -l)
    if (( $counts <= 0 )); then
        echo "No valid proxies found."
        rm $list >/dev/null
        exit 1
    fi
    echo "$counts proxies loaded......"
else
    echo "$1 doesn't exist!"
    exit 1
fi


# begin check
if (($counts<=$MAX_CONNECTIONS)); then
    MAX_CONNECTIONS=$counts
fi
declare -i begin=1
declare -i end=$MAX_CONNECTIONS

tput civis
while [ $begin -le $counts ]; do
    for ps in $(sed -n "$begin,$end p" ${list}); do
        proxy_host=$(echo $ps|cut -d : -f 1)
        proxy_port=$(echo $ps|cut -d : -f 2)
        (sleep 1) &
        (checkRSC $proxy_host $proxy_port >> rsc.txt) &
        (checkSD $proxy_host $proxy_port >> sd.txt) &
        (checkWiley $proxy_host $proxy_port >> wiley.txt) &
        (checkScience $proxy_host $proxy_port >> science.txt ) &
        (checkNature $proxy_host $proxy_port >> nature.txt ) &
        (checkACS $proxy_host $proxy_port >> acs.txt ) &
        (checkISI $proxy_host $proxy_port >> isi.txt) &
        (checkThieme $proxy_host $proxy_port >> thieme.txt) &
        (checkJSTOR $proxy_host $proxy_port >> jstor.txt) &
    done

    old_pos=0
    indicator $begin $counts

    # wait for background processes done
    wait

    # next loop
    begin=$(($end + 1))
    end=$(($end + $MAX_CONNECTIONS-1))

    if (( $end > $counts )); then
        end=$counts
    fi
done

tput cnorm
echo 

[[ -f $list ]] && rm $list
exit 0
