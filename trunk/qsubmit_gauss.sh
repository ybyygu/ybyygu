#!/usr/bin/env bash
#===============================================================================#
#   DESCRIPTION: qsubmit_gauss.sh
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  screen, rsync, passwordless ssh connectoin to remote server(
#                 Remote queue and remote archive)
#         NOTES:  ---
#        AUTHOR:  Wenping Guo (ybyygu)
#         EMAIL:  win.png@gmail.com
#       VERSION:  1.4
#       CREATED:  2004-12-21
#       UPDATED:  2007-08-04 18:08
#===============================================================================#

# setup environment
export LANG=C
umask 0002   # respect group privilege

if [[ $# == 1 ]]; then
    if [[ "${1:0:1}" != "+" && "${1:0:1}" != "-" ]]; then
        export CODE=$1
    fi
fi

#------------------------------------------------------------------------
export GJF_ROOT=$HOME/gjf${CODE:+_$CODE}
export QUEUE_DIR=$GJF_ROOT/queue
export WORK_DIR=$GJF_ROOT/work${CODE:+.`hostname`}
export STATUS="$WORK_DIR/status"
export DEBUG="$WORK_DIR/debug"
export ARCHIVE_DIR=$GJF_ROOT/ARCHIVE
export LOG=$ARCHIVE_DIR/qsubmit_gauss.log
export SESSION_NAME=qsg${CODE:+-$CODE}
export REGVAR=$HOME/.regvar${CODE:+-$CODE}
#------------------------------------------------------------------------

if [[ -f $REGVAR ]]; then
   source $REGVAR
fi   

archive()
{
    local remote_log=$REMOTE_ARCHIVE_DIR/`basename $LOG`
    local gjf=$1
    local log=${gjf%.*}.log
    # [[ ! -f $WORK_DIR/$gjf ]] && return 1

    local str=$(tail "$WORK_DIR/$log" |grep  "Normal termination")

    local state='error_done' 
    if [[ "$str" != "" ]]; then
        state='norm_done'
    fi
    
    mkdir -p "$ARCHIVE_DIR/$state"

    local dir_pattern=$(date "+%Y-%m%d-%H%M.XXXXXX")
    local dir_name=$(cd $ARCHIVE_DIR/$state && mktemp -d $dir_pattern) || return 2
    mv "$WORK_DIR"/{*.gjf,*.com,*.log,*.chk} $ARCHIVE_DIR/$state/$dir_name/  2>/dev/null
    echo "++ From  : $gjf" >> $STATUS
    echo "++ To    : $ARCHIVE_DIR/$state/$dir_name/" >> $STATUS
    echo >> $STATUS
    
    cp "$STATUS" $ARCHIVE_DIR/$state/$dir_name/ 
    cp "$DEBUG" $ARCHIVE_DIR/$state/$dir_name/ 
    if [[ -n "$REMOTE_ARCHIVE_DIR" ]] ; then
        scp -q "$remote_log" $ARCHIVE_DIR/
    fi

    # TODO: maybe conflict with other queues.
    if [[ -f $STATUS ]]; then
        cat $STATUS >> $LOG
        rm -f $STATUS
    fi
    
    if [[ -n "$REMOTE_ARCHIVE_DIR" ]] ; then
        # make remote directory in order to get rid of possible error when rsync transferring
        # thank you, yan.
        local archive_server="${REMOTE_ARCHIVE_DIR%:*}"
        local archive_dir="${REMOTE_ARCHIVE_DIR#*:}"
        ssh $archive_server "mkdir -p $arcive_dir"
        rsync -e ssh -a "$ARCHIVE_DIR/$state/$dir_name/" "$REMOTE_ARCHIVE_DIR/$state/$dir_name" && \
        rm -rf "$ARCHIVE_DIR/$state/$dir_name"
        scp -q "$LOG" "$remote_log"
    fi

    return 0
}

#  pop a gjf file from queue
#+ use the global variable *GJF* to bind it
queue()
{   
    # close standard error output
    exec 2>/dev/null

    mkdir -p $QUEUE_DIR
    mkdir -p $WORK_DIR
    
    if [[ -n "$REMOTE_QUEUE_DIR" ]]; then
        local queue_server="${REMOTE_QUEUE_DIR%:*}"
        local queue_dir="${REMOTE_QUEUE_DIR#*:}"
    fi

    #  Get something from the remote queue directory when local queue is empty
    GJF=$(cd $QUEUE_DIR && /bin/ls *.gjf *.com|head -n 1)
    if [[ "$GJF" == '' ]]; then
        if [[ -n "$queue_server" ]]; then
            GJF=$(ssh $queue_server "(cd $queue_dir && ls *.gjf *.com) | head -n 1")

            if [[ "$GJF" != '' ]]; then
            	echo "queue: get $GJF from $queue_server"
            	if [[ "$1" != 'dryrun' ]]; then
            		# not a test, so delete remote file 
					scp -q "$REMOTE_QUEUE_DIR/\"$GJF\"" $WORK_DIR/ \
					&& ssh $queue_server "rm -f \"$queue_dir/$GJF\""
				else
					return 0
                fi
            else
                echo 'queue: remote queue is empty.'
                return 1
            fi
        elif [[ $GJF == '' ]]; then
            echo 'queue: local queue is empty.'
            return 1
        fi 
    elif [[ -n "$REMOTE_QUEUE_DIR"  ]]; then
        echo "queue: Local queue is not empty. I found $GJF."
        echo "queue: I will process local queue firstly."
    fi
	# not a test
	if [[ "$1" != 'dryrun' ]]; then
		mv "$QUEUE_DIR/$GJF" "$WORK_DIR/"
	fi    
    return 0
}

# carefully clean scratch files
cleaning()
{
    for file in $GAUSS_SCRDIR/{*.rwf,*.chk,*.scr,*.d2e,*.int,*.inp}; do
        local check=$(pgrep -lf `basename $file`)
        [[ "$check" == "" ]] && rm -f "$file"
    done
}

submit()
{
    # restore the default settings
    if [[ -f $REGVAR ]]; then
       source $REGVAR
    fi   

    #+ use a local scratch directory
    export GAUSS_SCRDIR=$GAUSS_SCRDIR/$(hostname)${CODE:+-$CODE}

    if  [[ ! -d "$GAUSS_SCRDIR" ]]; then
        mkdir -m 777 -p "$GAUSS_SCRDIR"
    else
        cleaning
    fi

    if ! queue; then
        echo "submit: No more queued jobs, I will exit now."
        return 0
    else
        mkdir -p "$WORK_DIR"
        # submit gaussian jobs
        echo "++ run on: `hostname`" > "$STATUS"
        echo "++ Start : $(date +%c)" >> "$STATUS"
        #  convert DOS newlines to unix format, and then submit it
        #  Sometimes, gaussian will fail to parse the gjf file when there is no  
        #+ bland line in the end of the file, so I append one to it.
        (
          cd "$WORK_DIR"
          sed -e 's/$//; $G' "$WORK_DIR/$GJF" | $GAUSSIAN_CMD > "${GJF%.*}".log 2> $DEBUG
        )
        
        # wait for a long time
        echo "++ End   : $(date +%c)" >> "$STATUS"

        # archive and submit again 
        if [[ "$1" != 'testmode' ]]; then
            archive "$GJF" && submit
        fi
    fi
}

# setup environment
configure()
{
    local groot="/export/gaussian"
    local version=g03
    
    while true; do
        # question 0: where is your gaussian root directory?
        if [[ -n "$g03root" ]]; then
            groot=$g03root
            version=g03
        elif [[ -n "$g98root" ]]; then
            groot=$g98root
            version=g98
        fi
        echo -n "configure: Where is your g03/g98's root directory? ($groot) "
        read answer
        if [[ "$answer" != "" ]]; then
            groot="$answer"
        fi

        if [[ -d "$groot/g03" && -d "$answer/g98" ]]; then
        # wait for your choice.
            while true; do
                echo -n "configure: choose your gaussian version ($version)? "
                read answer
                if [[ "$answer" == "" || "$answer" == "g03" ]]; then
                    break
                elif [[ "$answer" == "g98" ]]; then
                    version=g98
                    break 
                else
                    echo -n "configure: Unacceptable choice, retry? (Y/n) "
                    read answer
                    if [[ "$answer" != "" && "$answer" != "y" && "$answer" != "Y" ]]; then
                        echo "configure: Configuration aborted."
                        return 1
                    fi   
                fi
            done
            break
        elif [[ -d "$groot/g03" ]]; then
            version=g03
            break
        elif [[ -d "$groot/g98" ]]; then
            version=g98
            break
        else
            echo -n "configure: Directory $groot/g03 or $groot/g98 doesn't exist. retry? (Y/n) "
            read answer
            if [[ "$answer" != "" && "$answer" != "y" && "$answer" != "Y" ]]; then
                echo "configure: Configuration aborted."
                return 1
            fi             
        fi
    done

    # question 1: where is your gaussian scratch directory? 
    local gscratch="/export/scratch"
    if [[ -n "$GAUSS_SCRDIR" ]]; then
        gscratch=$GAUSS_SCRDIR
    elif [[ -d "$groot/scratch" ]]; then
        gscratch="$groot/scratch"
    else
        gscratch="/tmp"
    fi

    while true; do
        echo "configure: Where is your gaussian scratch diretory? ($gscratch) "
        echo -n "TIPS: If you want to enable TCP Linda, please make scratch directory visible to every nodes."
        read answer
        if [[ "$answer" == "" ]]; then
            break;
        else
            gscratch="$answer"
            if [[ ! -d "$gscratch" ]]; then
                echo -n "configure: You specify an nonexistent directory, would I make it for you? (Y/n)"
                read answer
                if [[ "$answer" == "" || "$answer" == "Y" || "$answer" == "y" ]]; then
                    mkdir -m 777 -p "$gscratch" || echo "configure: Can't make $gscratch for you. aborting..." && return 1
                    break
                else
                    echo -n "configure: Retry to input scratch? (Y/n)"
                    read answer
                    if [[ "$answer" != "" && "$answer" != "y" && "$answer" != "Y" ]]; then
                        echo "configure: Configuration aborted."
                        return 1
                    fi
                fi
            else
                break
            fi
        fi
    done

    # final test:
    if [[ ! -f $groot/$version/bsd/$version.profile ]]; then
        echo "configure: I can't find \"$groot/$version/bsd/$version.profile\". Did your gaussian install correctly? "
        echo "configure: Failed to setup your gaussian enviroment."
        return 2
    fi
    
    # Remote server
    local remote_server=""
    echo -n "configure: Do you want to use a remote queue/archive server? (y/N) "
    read answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        while true; do
            echo "configure: IN ORDER TO USE THIS, YOU NEED A PASSWORDLESS SSH CONNECTION TO THE REMOTE SERVER."
            echo "configure: For more detail, please google \"passwordless ssh\", and follow the instructions." 
            echo -n "configure: Now, please input your remote queue server's IP address or name. "
            read answer
            if [[ "$answer" != "" ]]; then
                remote_server="$answer"
                break
            else
                echo -n "configure: Your input is invalid. Do you want to try again? (Y/n) " 
                read answer
                if [[ "$answer" != "" && "$answer" != "y" && "$answer" != "Y" ]]; then
                    break
                fi
            fi
        done
    fi

    # dump configuration
    echo "configure: Please make sure below lines exactly match your need."
    echo "configure: If not, configure again or edit $REGVAR directly by yourself."
    echo "------------------------------------------------------------"
    echo "export ${version}root=$groot" | tee $REGVAR
    echo "export GAUSS_SCRDIR=$gscratch" | tee -a $REGVAR
    echo "export GAUSSIAN_CMD=$version" | tee -a $REGVAR

    if [[ "$remote_server" != "" ]]; then
        echo "export REMOTE_QUEUE_DIR=$remote_server:$QUEUE_DIR" | tee -a $REGVAR
        echo "export REMOTE_ARCHIVE_DIR=$remote_server:$ARCHIVE_DIR" | tee -a $REGVAR
    fi
    echo "------------------------------------------------------------"

    echo "configure: Configuration finished."
    return 0
}

# summary log file
summary()
{
    egrep 'STEP|Step|step|m D|S     D|m F|S     F|TOTAL E|Linear|Angle b|#|DONE|Energy=|MM Force|SCF Done' $1
}

# send gaussian with STOP or CONT signal
signal_gauss()
{
    pid_gauss=$(/usr/bin/pgrep 'g03|g98')
    if ! getpid; then
        echo $pid_gauss
        return 1
    fi
    # guess if pid_gauss is contained by screen session
    echo " Waiting..."
    for pid in $pid_gauss; do
        # use echo to eliminate blank space from command output
        sid=$(echo `ps -o sid= $pid`)
        if [[ "$sid" == "$SID" ]]; then
            gpid=$(/usr/bin/pgrep -P $pid)
            while [[ "$gpid" != "" ]]; do
                if [[ "$1" == "-STOP" || "$1" == "-CONT" ]]; then
                    /bin/kill $1 $gpid
                else
                    return 1
                fi
                gpid=$(/usr/bin/pgrep -P $gpid)
            done
            # one is enough 
            break
        fi
    done

}

# use *SID* to get the screen session id
getpid()
{
    PID=$(screen -list | grep ".$SESSION_NAME[^\w-]" | tail -n 1)
    PID=${PID%.$SESSION_NAME*}
    [[ "$PID" == "" ]] && return 1
    # the whole session id is the sub process of screen program
    SID=$(/usr/bin/pgrep -P $PID)
    [[ "$SID" == "" ]] && return 1
    # the l*.exe, eg. l502.exe
    LID=$(/usr/bin/pgrep "l*.exe")
    if [[ "$LID" == "" ]]; then
    	return 1
    fi
    for id in $LID; do
    	sid=$(echo `/bin/ps -o sid= $id`)
    	if [[ "$sid" == "$SID" ]]; then
    	    GID=$id
            return 0
    	fi
    done

    return 1
}

jobcontrol()
{
    local PS="jc>> "
    echo "Enter into jobcontrol mode..."
    echo "${PS}Please enter help to show available command, and enter quit or q to exit."
    echo -n "$PS"

    local answer check
    while true; do
        if ! getpid; then
            echo "queue was terminated. exit ..."
            break 
        fi
        status=$(ps -o stat= "$GID" | grep 'T')
        if [[ "$status" != "" ]]; then
            echo "Job was paused, please enter continue to resume it."
            echo -n "$PS"
        fi
        read answer
        # test answer
        if [[ "$answer" == "help" ]]; then
            echo "available command: pause, continue, kill, terminate, summary, log, top, clear"
            echo -n "$PS"
        elif [[ "$answer" == "pause" ]]; then
            signal_gauss -STOP
            echo -n "$PS"
        elif [[ "$answer" == "continue" || "$answer" == "resume" ]]; then
            signal_gauss -CONT
            echo "Job was resumed, and use top to check."
            echo -n "$PS"
        elif [[ "$answer" == "kill" ]]; then
            echo -n "${PS}Are you really want to kill current job? Queued jobs will be continued. (y/N) "
            read answer
            if [[ "$answer" == "y" ]]; then
                kill $GID 
                echo "${PS}Current job has been killed."
                echo -n "$PS"
            else
                echo -n "$PS"
            fi
        elif [[ "$answer" == "terminate" ]]; then
            echo -n "${PS}Are you really want to terminate current queue? (y/N) "
            read answer
            if [[ "$answer" == "y" ]]; then
                (kill $PID; kill $GID) && echo "${PS}Queue has been terminated. exiting..." && break
            else
                echo -n "$PS"
            fi
        elif [[ "$answer" == "summary" ]]; then
            echo -n "Summary current running job. Press enter to begin and q to exit pager."
            local temp
            read -s temp
            echo
            summary $WORK_DIR/*.log | less
            echo -n "$PS"
        elif [[ "$answer" == "log" ]]; then
            echo -n "Show `basename $LOG` content. Press enter to begin and q to exit pager."
            local temp
            read -s temp
            echo
            cat $LOG | less
            echo -n "$PS"
        elif [[ "$answer" == "top" ]]; then
            top
            echo -n "$PS"
        elif [[ "$answer" == "clear" || "$answer" == "c" ]]; then
            clear
            echo -n "$PS"
        elif [[ "$answer" == "exit" || "$answer" == "quit" || "$answer" == "q" ]]; then
            break
        else
            echo -n "$PS"
        fi
    done
}

# main #
if [[ ! -f $REGVAR ]]; then
    echo "Before use this command, you need answer a few questions. Press Ctrl+C to abort."
    configure
    echo "Now, you can run this command again."
    exit 0
fi

# parse paremeters
if [[ $# == 0 ]]; then
    echo "Tips: You can give me a word to distinguish you from others. eg. $0 qxf"
elif [[ $# == 1 ]]; then
    # for internal usage    
    if [[ "$1" == "+submit" ]]; then
        submit
        exit 0 
    elif [[ "$1" == "+testmode" ]]; then
        submit testmode
        exit 0
    elif [[ "$1" == "+job" ]]; then
        jobcontrol
        exit 0
    # common parameters
    elif [[ "$1" == "--configure" ]]; then
        configure
        exit 0
    elif [[ "$1" == "--test" ]]; then
        export TESTMODE=1
        echo "Running in test mode ..."
    elif [[ "$1" == "--local" ]]; then
        export LOCAL=1
        echo "scan your local queue only ..."
    elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
        echo "`basename $0` [options]:"
        echo "  with no option: directly submit the jobs in your gjf queue"
        echo " or with following options:"
        echo "  --help: show this screen."
        echo "  --configure: configure the environment."
        echo "  --install site1 site2 ... : install this script into home-bin directories of remote sites using scp command."
        echo "  --test: simply sibmit the job and over. no queue, no archive"
        echo "  --local: use local queue only, even when a remote site specified in .regvar file."
        echo "  --nodelist node1 node2 ...: enable TCP Linda on node1, node2 etc."
        exit 0
    else
        CODE=$1
    fi
elif [[ "$1" == "--install" ]]; then
    shift 1
    for site in $*; do
        scp "$0" "$site:$HOME/bin/"
    done
    exit 0
elif [[ "$1" == "--nodelist" ]]; then
    shift 1
    echo "TCP Linda will be enabled among nodes: $*."
    echo "If encount error, please google \"g03 linda\" for more information."

    export GAUSS_LFLAGS="-opt 'Tsnet.Node.lindarsharg: ssh' -vv -nodelist '$*'"
fi

# restore the default settings
if [[ -f $REGVAR ]]; then
   source $REGVAR
fi
# set up runtime environment
source $g03root/$GAUSSIAN_CMD/bsd/$GAUSSIAN_CMD.profile
if [[ -n "$GAUSS_LFLAGS" ]]; then
    echo "Set up Linda runtime enviroment..."
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$g03root/g03/linda7.1/intel-linux2.4/lib
    export GAUSS_EXEDIR=$g03root/g03/linda-exe:$GAUSS_EXEDIR
fi

# do real work

if ! getpid; then
    if ! queue dryrun; then
        echo "Please put something into \"$QUEUE_DIR\", then run this command again."
        exit 0
    fi

    echo -n "Do you want to process $QUEUE_DIR? (Y/n)"
    read answer
    if [[ "$answer" == "" || "$answer" == "y" || "$answer" == "Y" ]]; then
        # use screen to store our session
        if [[ -z "$TESTMODE" ]]; then
            screen -S $SESSION_NAME -D -m $0 +submit &
        else
            screen -S $SESSION_NAME -D -m $0 +testmode &
        fi
        echo "Please wait ..."
        sleep 2
        echo "your GJF_ROOT is $GJF_ROOT."
        $0 +job
    else
        exit 0
    fi
else
    echo "Your previous queue is still running. "
    $0 +job
    exit 1
fi

exit 0
