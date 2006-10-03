#!/bin/bash
# Written by ybyygu at 2004
# Last updated at 2006 10/3

# What you need: screen

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
#------------------------------------------------------------------------

# Leave a chance for customing gaussian enviroment
[ -f ~/.regvar ] && source ~/.regvar

archive()
{
    local ERROR_DONE_DIR="$ARCHIVE_DIR/error_done"
    local NORM_DONE_DIR="$ARCHIVE_DIR/norm_done"

    local str=$(tail "$WORK_DIR/${1%.*}.log" |grep  "Normal termination") || return 1
    local dir_name=$(date "+%Y-%m%d-%H%M.XXXXXX")
    
    if [ "$str" == "" ]; then
        mkdir -p $ERROR_DONE_DIR
        local arch_dir=$(mktemp -d $ERROR_DONE_DIR/$dir_name) || return 2
        ( cd $WORK_DIR; mv "$1" *.log *.chk $arch_dir/ 2>/dev/null )
        echo "++ From  : $QUEUE_DIR/$1" >> $STATUS
        echo "++ To    : $arch_dir/" >> $STATUS
        echo >> $STATUS
    else
        mkdir -p $NORM_DONE_DIR
        local arch_dir=$(mktemp -d $NORM_DONE_DIR/$dir_name) || return 2
        
        ( cd $WORK_DIR; mv "$1" *.log *.chk $arch_dir/ 2>/dev/null )
        echo "++ From : $QUEUE_DIR/$1" >> $STATUS
        echo "++ To   : $arch_dir/" >> $STATUS
        echo >> $STATUS
    fi
    
    if [ -n "$REMOTE_ARCHIVE_DIR" ] ; then
        rsync -e ssh -a "$REMOTE_ARCHIVE_DIR"/`basename $LOG` $ARCHIVE_DIR/
    fi

    # TODO: maybe conflict with other queues.
    if [ -f $STATUS ]; then
        cat $STATUS >> $LOG
        rm -f $STATUS
    fi
    
    if [ -n "$REMOTE_ARCHIVE_DIR" ] ; then
        rsync -e ssh -a "$ARCHIVE_DIR/$arch_dir/" "$REMOTE_ARCHIVE_DIR" && rm -rf "$arch_dir"
    fi
}

#  pop a gjf file from queue
#+ use the global variable *GJF* to get it
queue()
{   
    # close standard error output
    exec 2>/dev/null

    mkdir -p $QUEUE_DIR

    rsynced=0
    #  Get sth. from the remote queue diretory when local queue is empty
    #+ We use rsync to do this.
    GJF=$(cd $QUEUE_DIR && /bin/ls *.gjf *.com|head -n 1)
    if [ "$GJF" == "" ]; then
        if [[ -n "$REMOTE_QUEUE_DIR"  ]]; then
            rsync -e ssh -a --delete "$REMOTE_QUEUE_DIR/" "$QUEUE_DIR" || return 1
            rsynced=1
        else
            return 1
        fi 
    elif [[ -n "$REMOTE_QUEUE_DIR"  ]]; then
        echo "Local queue is not empty, I will process local queue firstly. "
    fi
    
    # try again
    GJF=$(cd $QUEUE_DIR && /bin/ls *.gjf *.com|head -n 1)
    if [ "$GJF" == "" ]; then
        return 1
    else
        if ! [ "$1" == '-' ]; then
            mv "$QUEUE_DIR/$GJF" "$WORK_DIR/"

            # for remote deleting
            if [ $rsynced -eq 1 ]; then
                rsync -e ssh -a --delete "$QUEUE_DIR/" "$REMOTE_QUEUE_DIR" 
            fi
        fi
        return 0
    fi
}

submit()
{
    #  clean scratch before starting
    if ! [ -d "$GAUSS_SCRDIR" ]; then
        mkdir -p "$GAUSS_SCRDIR"
        echo "Please export GAUSS_SCRDIR in your .bashrc or $HOME/.regvar." >&2
        return 1
    else
        rm -f "$GAUSS_SCRDIR/{*.rwf,*.int,*.inp,*.chk,*.scr,*.d2e}"
    fi
    
    if ! queue; then
        echo "No more jobs, I will exit now." >&2
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
