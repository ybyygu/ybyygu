#!/bin/bash
# Written by ybyygu at 2004
# Last updated at 19-10-2006

#  What you need: screen, rsync
#+ and passwordless ssh connection to the remote server

#------------------------------------------------------------------------
GJF_ROOT=$HOME/gjf
QUEUE_DIR=$GJF_ROOT/queue
WORK_DIR=$GJF_ROOT/work
STATUS="$WORK_DIR/status"
DEBUG="$WORK_DIR/debug"
ARCHIVE_DIR=$GJF_ROOT/ARCHIVE
LOG=$ARCHIVE_DIR/qsubmit_gauss.log
#------------------------------------------------------------------------


archive()
{
    local remote_log=$REMOTE_ARCHIVE_DIR/`basename $LOG`
    local gjf=$1
    local log=${gjf%.*}.log
    [[ ! -f $WORK_DIR/$gjf ]] && return 1

    local str=$(tail "$WORK_DIR/$log" |grep  "Normal termination")

    local state='error_done' 
    if [[ "$str" != "" ]]; then
        state='norm_done'
    fi
    
    mkdir -p "$ARCHIVE_DIR/$state"

    local dir_pattern=$(date "+%Y-%m%d-%H%M.XXXXXX")
    local dir_name=$(cd $ARCHIVE_DIR/$state && mktemp -d $dir_pattern) || return 2
    mv "$WORK_DIR"/{$gjf,$log,*.chk} $ARCHIVE_DIR/$state/$dir_name/  2>/dev/null
    echo "++ From  : $gjf" >> $STATUS
    echo "++ To    : $ARCHIVE_DIR/$state/$dir_name/" >> $STATUS
    echo >> $STATUS
    
    if [[ -n "$REMOTE_ARCHIVE_DIR" ]] ; then
        scp -q "$remote_log" $ARCHIVE_DIR/
    fi

    # TODO: maybe conflict with other queues.
    if [[ -f $STATUS ]]; then
        cat $STATUS >> $LOG
        rm -f $STATUS
    fi
    
    if [[ -n "$REMOTE_ARCHIVE_DIR" ]] ; then
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
                scp -q "$REMOTE_QUEUE_DIR/\"$GJF\"" $WORK_DIR/ && \
                # not a test, so delete remote file
                [[ "$1" != '-' ]] && ssh $queue_server "rm -f \"$queue_dir/$GJF\""
                echo "queue: get $GJF from $queue_server"
            else
                echo 'queue: remote queue is empty.'
                return 1
            fi
        elif [[ $GJF == '' ]]; then
            echo 'queue: local queue is empty.'
            return 1
        fi 
    elif [[ -n "$REMOTE_QUEUE_DIR"  ]]; then
        echo "queue: Local queue is not empty."
        echo "queue: I will process local queue firstly."

        # not a test
        [[ "$1" != '-' ]] && mv "$QUEUE_DIR/$GJF" "$WORK_DIR/"
    else
        # do the same thing as before
        [[ "$1" != '-' ]] && mv "$QUEUE_DIR/$GJF" "$WORK_DIR/" 
    fi
    
    return 0
}

# carefully clean scratch files
cleaning()
{
    for file in $GAUSS_SCRDIR/{*.rwf,*.chk,*.scr,*.d2e,*.int,*.inp}; do
        local check=$(pgrep -lf `basename $file`)
        [[ "$check" ]] || rm -f "$file"
    done
}

submit()
{
    if  [[ ! -d "$GAUSS_SCRDIR" ]]; then
        mkdir -p "$GAUSS_SCRDIR"
        echo "submit: Please export GAUSS_SCRDIR in your .bashrc or $HOME/.regvar." >&2
        return 1
    else
        cleaning
    fi
    
    if ! queue; then
        echo "submit: No more jobs, I will exit now." >&2
        return 0
    else
        mkdir -p "$WORK_DIR"
        # submit gaussian jobs
        echo "++ run on: `hostname`" > "$STATUS"
        echo "++ Start : $(date +%c)" >> "$STATUS"
        # convert DOS newlines to unix format, and then submit it
        (
          cd "$WORK_DIR"
          cat "$WORK_DIR/$GJF" | tr -d '\r' | $GAUSSIAN_CMD &> "${GJF%.*}".log
        )
        
        # wait for a long time
        echo "++ End   : $(date +%c)" >> "$STATUS"
    
        archive "$GJF" && submit
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

jobcontrol()
{
    local pid=$1

    local answer sid eid
    sid=$(/usr/bin/pgrep -P $pid)

    echo "jobcontrol: Please enter help to show available command, and enter quit or q to exit."
    echo -n "jobcontrol: "
    while true; do
        read answer

        if [[ "$answer" == "help" ]]; then
            echo "available command: pause, continue, kill, terminate, summary, queue, jobs"
            echo -n "jobcontrol: "
        elif [[ "$answer" == "pause" ]]; then
            eid=$(/bin/ps -s $sid -o pid | tail -n 1)
            if [[ "$eid" != "" ]]; then
                kill -STOP $eid
                echo "Current job was paused, and enter continue to resume it." 
                echo -n "jobcontrol: "
            fi
        elif [[ "$answer" == "continue" ]]; then
            eid=$(/bin/ps -s $sid -o pid | tail -n 1)
            if [[ "$eid" != "" ]]; then
                kill -CONT $eid && echo -n "jobcontrol: "
            fi
        elif [[ "$answer" == "kill" ]]; then
            echo -n "jobcontrol: Are you really want to kill current job? (y/N) "
            read answer
            if [[ "$answer" == "y" ]]; then
                eid=$(/bin/ps -s $sid -o pid | tail -n 1)
                if [[ "$eid" != "" ]]; then
                    kill $eid 
                    echo "jobcontrol: Current job has been killed."
                    echo -n "jobcontrol: "
                fi
            else
                echo -n "jobcontrol: "
            fi
        elif [[ "$answer" == "terminate" ]]; then
            echo -n "jobcontrol: Are you really want to terminate current queue? (y/N) "
            read answer
            if [[ "$answer" == "y" ]]; then
                eid=$(/bin/ps -s $sid -o pid | tail -n 1)
                if [[ "$eid" != "" ]]; then
                    (kill $pid; kill $eid) && echo "jobcontrol: Queue has been terminated. exiting..." && break
                fi
            else
                echo -n "jobcontrol: "
            fi
        elif [[ "$answer" == "queue" ]]; then
            echo -n "queued jobs:"
            local files=$(ls $QUEUE_DIR/{*.gjf,*.com} 2>/dev/null)
            if [[ "$files" == "" ]]; then
                echo "  none"
            else
                for f in "$files"; do
                    echo "  `basename $f`"
                done
            fi

            echo -n "jobcontrol: "
        elif [[ "$answer" == "jobs" ]]; then
            echo -n "current running job:"
            local files=$(ls $WORK_DIR/*.gjf)
            if [[ "$files" == "" ]]; then
                echo "  none"
            else
                for f in "$files"; do
                    echo "  `basename $f`"
                done
            fi

            echo -n "jobcontrol: "
        elif [[ "$answer" == "summary" ]]; then
            echo -n "Summary current running job. Press enter to begin and q to exit pager."
            local temp
            read -s temp
            echo
            summary $WORK_DIR/*.log|pager
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
else
    # Leave a chance for customing gaussian environment
    source ~/.regvar
fi

mkdir -p "$WORK_DIR"
if [ $# == 0 ]; then

    check=$(screen -list | grep qsg)
    if [[ "$check" == "" ]]; then
        if ! queue -; then
            echo "Please put something into \"$QUEUE_DIR\", then run this command again."
            exit 0
        fi

        # use screen to store our session
        screen -S qsg -D -m $0 -submit &
        $0 -job $pid
#        echo "your GJF_ROOT is $GJF_ROOT."
#        echo "Use \"screen -r qsg\" to attach the session."
    else
        pid=${check%.*}
        echo "The previous queue is still running. "
        $0 -job $pid
        exit 1
    fi
elif [[ $# -ge 1 ]]; then
    if [[ "$1" == "-submit" ]]; then
        submit
        exit 0 
    elif [[ "$1" == "-job" ]]; then
        jobcontrol $2
        exit 0
    elif [[ "$1" == "--configure" ]]; then
        configure
        exit 0
    elif [[ "$1" == "--help" ]]; then
        echo "$0 --help: show this screen."
        echo "$0 --configure: configure the environment."
        echo "$0 : directly submit the queued jobs."
    fi
fi

exit 0
