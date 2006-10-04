#!/bin/bash
# Written by ybyygu at 2004
# Last updated at 2006 10/3

#  What you need: screen, rsync
#+ and passwdless ssh connection to the remote server

#------------------------------------------------------------------------
GAUSSIAN_CMD="g03"      #  if you want use gaussian 98, please change 
                        #+ this to g98
GJF_ROOT=$HOME/gjf
QUEUE_DIR=$GJF_ROOT/queue
WORK_DIR=$GJF_ROOT/work
STATUS="$WORK_DIR/status"
DEBUG="$WORK_DIR/debug"
ARCHIVE_DIR=$GJF_ROOT/ARCHIVE
LOG=$ARCHIVE_DIR/qsubmit_gauss.log
REMOTE_QUEUE_DIR="192.168.5.15:$QUEUE_DIR"      #  I can get the queued files from a remote server
                                                #+ If you don't want this happen, just comment this
REMOTE_ARCHIVE_DIR="192.168.5.15:$ARCHIVE_DIR"  #  I can archive the log files into a remote server
                                                #+ If you don't want this happen, just comment this
REMOTE_LOG=$REMOTE_ARCHIVE_DIR/`basename $LOG`                                    
#------------------------------------------------------------------------

# Leave a chance for customing gaussian enviroment
[ -f ~/.regvar ] && source ~/.regvar

archive()
{
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
        scp -q "$REMOTE_LOG" $ARCHIVE_DIR/
    fi

    # TODO: maybe conflict with other queues.
    if [[ -f $STATUS ]]; then
        cat $STATUS >> $LOG
        rm -f $STATUS
    fi
    
    if [[ -n "$REMOTE_ARCHIVE_DIR" ]] ; then
        rsync -e ssh -a "$ARCHIVE_DIR/$state/$dir_name/" "$REMOTE_ARCHIVE_DIR/$state/$dir_name" && \
        rm -rf "$ARCHIVE_DIR/$state/$dir_name"
        scp -q "$LOG" "$REMOTE_LOG"
    fi

    return 0
}

#  pop a gjf file from queue
#+ use the global variable *GJF* to get it
queue()
{   
    # close standard error output
    # exec 2>/dev/null

    mkdir -p $QUEUE_DIR
    
    if [[ -n "$REMOTE_QUEUE_DIR" ]]; then
        local queue_server="${REMOTE_QUEUE_DIR%:*}"
        local queue_dir="${REMOTE_QUEUE_DIR#*:}"
    fi

    #  Get sth. from the remote queue diretory when local queue is empty
    GJF=$(cd $QUEUE_DIR && /bin/ls *.gjf *.com|head -n 1)
    if [[ "$GJF" == '' ]]; then
        if [[ -n "$queue_server" ]]; then
            GJF=$(ssh $queue_server "(cd $queue_dir && ls *.gjf *.com) | head -n 1")

            if [[ "$GJF" != '' ]]; then
                scp -q $REMOTE_QUEUE_DIR/$GJF $WORK_DIR/ && \
                # not a test, so delete remote file
                [[ "$1" != '-' ]] && ssh $queue_server "rm -f $queue_dir/$GJF"
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

submit()
{
    #  clean scratch before starting
    if ! [ -d "$GAUSS_SCRDIR" ]; then
        mkdir -p "$GAUSS_SCRDIR"
        echo "Please export GAUSS_SCRDIR in your .bashrc or $HOME/.regvar." >&2
        return 1
    else
        rm -f "$GAUSS_SCRDIR"/{*.rwf,*.int,*.inp,*.chk,*.scr,*.d2e}
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

# main #

mkdir -p "$WORK_DIR"
if [ $# == 0 ]; then
    if ! queue -; then
        echo "Please put something into \"$QUEUE_DIR\", then run this command again."
        exit 0
    fi
    
    # use screen to store our session
    screen -S qsg -d -m $0 -submit
    echo "your GJF_ROOT is $GJF_ROOT."
    echo "Use \"screen -r qsg\" to attach the session."
elif [ $# == 1 ]; then
    if [ $1 == '-submit' ]; then
        submit &> "$DEBUG"
    fi
fi

exit 0
