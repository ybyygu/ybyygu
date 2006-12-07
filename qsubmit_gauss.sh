#!/bin/bash
# VERSION: 1.0
# Written by ybyygu at 2004
# Last updated at 30-11-2006

#  What you need: screen, rsync and passwordless
#+                ssh connection to the remote server

export LANG=C

#------------------------------------------------------------------------
export GJF_ROOT=$HOME/gjf${CODE:+_$CODE}
export QUEUE_DIR=$GJF_ROOT/queue
export WORK_DIR=$GJF_ROOT/work${CODE:+.`hostname`}
export STATUS="$WORK_DIR/status"
export DEBUG="$WORK_DIR/debug"
export ARCHIVE_DIR=$GJF_ROOT/ARCHIVE
export LOG=$ARCHIVE_DIR/qsubmit_gauss.log
#------------------------------------------------------------------------

[[ -f ~/.regvar ]] && source ~/.regvar

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
    if [[ -z "$LOCAL" && -n "$REMOTE_ARCHIVE_DIR" ]] ; then
        scp -q "$remote_log" $ARCHIVE_DIR/
    fi

    # TODO: maybe conflict with other queues.
    if [[ -f $STATUS ]]; then
        cat $STATUS >> $LOG
        rm -f $STATUS
    fi
    
    if [[ -z "$LOCAL" && -n "$REMOTE_ARCHIVE_DIR" ]] ; then
        rsync -e ssh -a "$ARCHIVE_DIR/$state/$dir_name/" "$REMOTE_ARCHIVE_DIR/$state/$dir_name" && \
        rm -rf "$ARCHIVE_DIR/$state/$dir_name"
        scp -q "$LOG" "$remote_log"
    fi

    return 0
}

#  pop a gjf file from queue
#+ use the global variable *GJF* to get it
queue()
{   
    # close standard error output
    exec 2>/dev/null

    mkdir -p $QUEUE_DIR
    
    if [[ -z "$LOCAL" && -n "$REMOTE_QUEUE_DIR" ]]; then
        local queue_server="${REMOTE_QUEUE_DIR%:*}"
        local queue_dir="${REMOTE_QUEUE_DIR#*:}"
    fi

    #  Get something from the remote queue directory when local queue is empty
    GJF=$(cd $QUEUE_DIR && /bin/ls *.gjf *.com|head -n 1)
    if [[ "$GJF" == '' ]]; then
        if [[ -n "$queue_server" ]]; then
            GJF=$(ssh $queue_server "(cd $queue_dir && ls *.gjf *.com) | head -n 1")

            if [[ "$GJF" != '' ]]; then
                scp -q "$REMOTE_QUEUE_DIR/\"$GJF\"" $WORK_DIR/ && \
                # not a test, so delete remote file
                [[ "$1" != 'dryrun' ]] && ssh $queue_server "rm -f \"$queue_dir/$GJF\""
                echo "queue: get $GJF from $queue_server"
            else
                echo 'queue: remote queue is empty.'
                return 1
            fi
        elif [[ $GJF == '' ]]; then
            echo 'queue: local queue is empty.'
            return 1
        fi 
    elif [[ -z "$LOCAL" && -n "$REMOTE_QUEUE_DIR"  ]]; then
        echo "queue: Local queue is not empty. I found $GJF."
        echo "queue: I will process local queue firstly."

        # not a test
        if [[ "$1" != 'dryrun' ]]; then
            mv "$QUEUE_DIR/$GJF" "$WORK_DIR/"
        fi
    else
        # do the same thing as before
        echo "queue: get $GJF from $QUEUE_DIR"
        if [[ "$1" != 'dryrun' ]]; then
            mv "$QUEUE_DIR/$GJF" "$WORK_DIR/"
        fi
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
    source ~/.regvar
    #+ use a local scratch directory
    export GAUSS_SCRDIR=$GAUSS_SCRDIR/$(hostname)

    if  [[ ! -d "$GAUSS_SCRDIR" ]]; then
        mkdir -p "$GAUSS_SCRDIR"
    else
        cleaning
    fi

    if ! queue; then
        echo "submit: No more jobs, I will exit now."
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
          sed -e 's/$//; $G' "$WORK_DIR/$GJF" | $GAUSSIAN_CMD &> "${GJF%.*}".log
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
    local groot="/gaussian"
    local version=g03
    
    while true; do
        # question 0: where is your gaussian root directory?
        echo -n "configure: Where is your g03/g98's root directory? (/gaussian) "
        read answer
        if [[ "$answer" != "" ]]; then
            groot="$answer"
        fi

        if [[ -d "$groot/g03" && -d "$answer/g98" ]]; then
        # wait for your choice.
            while true; do
                echo -n "configure: choose your gaussian version (g03)? "
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
    local gscratch="/tmp"
    if [[ -d "$groot/scratch" ]]; then
        gscratch="$groot/scratch"
    fi

    while true; do
        echo -n "configure: Where your gaussian scratch diretory? ($gscratch) "
        read answer
        if [[ "$answer" == "" ]]; then
            break;
        else
            gscratch="$answer"
            if [[ ! -d "$gscratch" ]]; then
                echo -n "configure: You specify an nonexistent directory, would I make it for you? (Y/n)"
                read answer
                if [[ "$answer" == "" || "$answer" == "Y" || "$answer" == "y" ]]; then
                    mkdir -p "$gscratch" || echo "configure: Can't make $gscratch for you. aborting..." && return 1
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
        echo "configure: Failed to configurate your gaussian enviroment."
        return 2
    fi
    
    # Remote server
    local remote_server=""
    echo -n "configure: Do you want to use a remote queue/archive server? (y/N) "
    read answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        while true; do
            echo "configure: IN ORDER TO USE THIS, YOU NEED A PASSWORDLESS SSH CONNECTION TO THE REMOTE SERVER."
            echo "configure: For more detail, please goole \"passwordless ssh\", and follow the instructions." 
            echo -n "configure: Now, please input your remote queue server's IP address or name. "
            read answer
            if [[ "$answer" != "" ]]; then
                remote_server="$answer"
                break
            else
                echo -n "configure: Your input is invalid, do you want to try again? (Y/n) " 
                read answer
                if [[ "$answer" != "" && "$answer" != "y" && "$answer" != "Y" ]]; then
                    break
                fi
            fi
        done
    fi

    # show dump
    echo "configure: Please check below lines exactly match your need."
    echo "configure: If not, configurate again or edit ~/.regvar directly by yourself."
    echo "------------------------------------------------------------"
    echo "export ${version}root=$groot" | tee ~/.regvar
    echo "export GAUSS_SCRDIR=$gscratch" | tee -a ~/.regvar
    echo "source $groot/$version/bsd/$version.profile" |tee -a ~/.regvar
    echo "export GAUSSIAN_CMD=$version" | tee -a ~/.regvar

    if [[ "$remote_server" != "" ]]; then
        echo "export REMOTE_QUEUE_DIR=$remote_server:$QUEUE_DIR" | tee -a ~/.regvar
        echo "export REMOTE_ARCHIVE_DIR=$remote_server:$ARCHIVE_DIR" | tee -a ~/.regvar
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

# use *PID* to get the process id
getpid()
{
    PID=$(screen -list | grep ".$SESSION_NAME" | tail -n 1)
    PID=${PID%.$SESSION_NAME*}
    [[ "$PID" == "" ]] && return 1
    # the whole session id
    SID=$(/usr/bin/pgrep -P $PID)
    [[ "$SID" == "" ]] && return 1
    # the l*.exe, eg. l502.exe
    GID=$(/bin/ps -s "$SID" -o pid | tail -n 1)
    
    return 0
}

jobcontrol()
{
    echo "jobcontrol: Please enter help to show available command, and enter quit or q to exit."
    echo -n "jobcontrol: "

    local answer check
    while true; do
        if ! getpid; then
            echo "queue was terminated. exit ..."
            break 
        fi
        
        read answer
        # test answer
        if [[ "$answer" == "help" ]]; then
            echo "available command: pause, continue, kill, terminate, summary, queue, status, log, top, clear"
            echo -n "jobcontrol: "
        elif [[ "$answer" == "pause" ]]; then
            kill -STOP $GID
            echo "Current job was paused, and enter continue to resume it." 
            echo -n "jobcontrol: "
        elif [[ "$answer" == "continue" || "$answer" == "resume" ]]; then
            kill -CONT $GID && echo -n "jobcontrol: "
        elif [[ "$answer" == "kill" ]]; then
            echo -n "jobcontrol: Are you really want to kill current job? (y/N) "
            read answer
            if [[ "$answer" == "y" ]]; then
                kill $GID 
                echo "jobcontrol: Current job has been killed."
                echo -n "jobcontrol: "
            else
                echo -n "jobcontrol: "
            fi
        elif [[ "$answer" == "terminate" ]]; then
            echo -n "jobcontrol: Are you really want to terminate current queue? (y/N) "
            read answer
            if [[ "$answer" == "y" ]]; then
                (kill $PID; kill $GID) && echo "jobcontrol: Queue has been terminated. exiting..." && break
            else
                echo -n "jobcontrol: "
            fi
        elif [[ "$answer" == "queue" || "$answer" == "ls" ]]; then
            local files=$(ls $QUEUE_DIR/{*.gjf,*.com} 2>/dev/null)
            if [[ "$files" == "" ]]; then
                echo "  none"
            else
                for f in $files; do
                    echo "  `basename $f`"
                done
            fi

            echo -n "jobcontrol: "
        elif [[ "$answer" == "status" ]]; then
            local files=$(ls $WORK_DIR/*.gjf 2>/dev/null)
            if [[ "$files" == "" ]]; then
                echo "  none"
            else
                for f in "$files"; do
                    echo -n "`basename \"$f\"`: "
                    break
                done
            fi
            
            local check=$(ps -o stat $GID|wc -l)
            if [[ "$check" -ne 2 ]]; then
                echo "You should not see this."
                break;
            fi

            check=$(ps -o stat $GID | tail -n 1 |grep 'T')
            if [[ "$check" != "" ]]; then
                echo "  [paused]"
            else
                echo "  [running]"
            fi

            echo -n "jobcontrol: "
        elif [[ "$answer" == "summary" ]]; then
            echo -n "Summary current running job. Press enter to begin and q to exit pager."
            local temp
            read -s temp
            echo
            summary $WORK_DIR/*.log | less
            echo -n "jobcontrol: "
        elif [[ "$answer" == "log" ]]; then
            echo -n "Show `basename $LOG` content. Press enter to begin and q to exit pager."
            local temp
            read -s temp
            echo
            cat $LOG | less
            echo -n "jobcontrol: "
        elif [[ "$answer" == "top" ]]; then
            top
            echo -n "jobcontrol: "
        elif [[ "$answer" == "clear" || "$answer" == "c" ]]; then
            clear
            echo -n "jobcontrol: "
        elif [[ "$answer" == "exit" || "$answer" == "quit" || "$answer" == "q" ]]; then
            break
        else
            echo -n "jobcontrol: "
        fi
    done
}

# main #
if [[ ! -f ~/.regvar ]]; then
    echo "Before use this command, you need answer a few questions."
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
        echo "  --local: use local queue only, even a remote site specified in .regvar file."
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

fi

# do real work
export SESSION_NAME=qsg${CODE:+-$CODE}

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
        echo "Enter jobcontrol mode ..."
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
