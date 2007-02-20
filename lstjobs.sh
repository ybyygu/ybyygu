#!/bin/bash
# list_job.sh -- created 22-12月-2006, <Wenping Guo> ybyygu@gmail.com
# @Last Change: 19-2-2007
# @Revision:    0.4

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
    exec 2>/dev/null
    server=$1
    if [[ "$server" == "" ]]; then
        return 
    fi
    txt=`ssh $server pgrep "g03"`
    if [[ "$txt" == "" ]]; then
        txt=`ssh $server pgrep "g98"`
    fi
    if [[ "$txt" == "" ]]; then
        return 
    fi
    for pid in $txt; do
        # the l*.exe, eg. l502.exe
        exeid=$(ssh $server /usr/bin/pgrep -P $pid)
	status=$(ssh $server ps -o stat $exeid|tail -n 1)
	check=$(echo $status | grep 'T')
        if [[ "$status" != "" && "$check" != "" ]]; then
            STATUS="${BLUE}[paused ]${NC}"
        else
	    STATUS="[running]"
        fi

        txt=`ssh $server grep -z -m 1 PWD= /proc/$pid/environ`
        path=${txt#PWD=}
        log=`ssh $server ls -1tr $path/\*.log | tail -n 1`
        LOG=`basename $log`
    done 
}

# Liyan: append or remove your machine here
SERVERS="
	 c0155
	 c0156
	 c0157
	 c0158
	 c0159
         c0131
         c0133
         c0515
	"
	
WELCOME="Jobs in C0515 (qsubmit_gauss.sh):"
echo -e $WELCOME
for s in $SERVERS; do
    STATUS="[.......]"
    LOG="${BLUE}no working job found.${NC}"
    show_working_job $s
    echo -e "${RED}$s${NC}\t\t$STATUS\t$LOG"
done

# Liyan: append or remove your machine here
NODES="
       192.168.1.32
       192.168.1.15
       192.168.1.21
       192.168.5.6
       192.168.5.8
       192.168.5.13
      "
WELCOME="and...\nVacation jobs in nodes (qsubmit_gauss.sh liyan):"
echo -e $WELCOME
for s in $NODES; do
    STATUS="[.......]"
    LOG="${BLUE}no working job found.${NC}"
    show_working_job $s
    echo -e "${RED}$s${NC}\t$STATUS\t$LOG"
done
