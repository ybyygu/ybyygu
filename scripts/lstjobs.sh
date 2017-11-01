#!/usr/bin/env bash
#===============================================================================#
#   DESCRIPTION: lstjobs.sh 
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#         NOTES:  ---
#        AUTHOR:  Wenping Guo (ybyygu)
#         EMAIL:  win.png@gmail.com
#       VERSION:  0.5
#       CREATED:  2006-12-22
#       UPDATED:  2007-07-28 17:11
#===============================================================================#

# Liyan: append or remove your machine here
SERVERS="
	 c0154
	 c0155
	 c0156
	 c0157
	 c0158
	 c0159
	 c0161
	 c0162
	 c0163
	"
# Liyan: append or remove your nodes here
NODES="
      gauss@192.168.1.1
      gauss@192.168.1.12
      gauss@192.168.1.13
      gauss@192.168.1.32
      g03@192.168.5.7            
      "

# Define some colors first:
red='\e[0;31m'
RED='\e[1;31m'
blue='\e[0;34m'
BLUE='\e[1;34m'
cyan='\e[0;36m'
CYAN='\e[1;36m'
NC='\e[0m' # No Color

# use global variable LOG to store the log filename
show_working_job()
{
    # make silence
    exec 2>/dev/null
    
    # get response from remote server
    server=$1
    [[ "$server" == "" ]] && return
    resp=`ssh $server /usr/bin/pgrep -u '$USER' "g03\|g98"`
    [[ "$resp" == "" ]] && return 

    for pid in $resp; do
        # l*.exe, eg. l502.exe
        # maybe more than one, but only get the last one
        exeid=""
        exeid=$(ssh $server /usr/bin/pgrep -u '$USER' 'l\*.exe' | tail -n 1)
        [[ "$exeid" == "" ]] && return
	status=$(ssh $server ps -o stat= $exeid | grep 'T')
        if [[ "$status" != "" ]]; then
            STATUS="[${RED}paused ${NC}]"
        else
	    STATUS="[running]"
        fi

        txt=`ssh $server grep -z -m 1 'PWD=' /proc/$pid/environ`
        path=${txt#PWD=}
        log=`ssh $server /bin/ls -1tr $path/\*.log | tail -n 1`
        LOG=`basename $log`
    done 
}

	
WELCOME="Jobs in PCs (qsubmit_gauss.sh):"
echo -e $WELCOME
for s in $SERVERS; do
    STATUS="[.......]"
    LOG="${BLUE}no working job found.${NC}"
    show_working_job $s
    echo -e "$s\t\t$STATUS\t$LOG"
done

WELCOME="and...\njobs in NODEs (qsubmit_gauss.sh liyan):"
echo -e $WELCOME
for s in $NODES; do
    STATUS="[.......]"
    LOG="${BLUE}no working job found.${NC}"
    show_working_job $s
    echo -e "$s   \t$STATUS\t$LOG"
done

