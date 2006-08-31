#!/bin/bash
# Written by ybyygu at 2004
# Last updated at 2006 8/31

#------------------------------------------------------------------------
GAUSSIAN_VAR=$HOME/gaussian/regvar-g03
GAUSSIAN_CMD="g03"
GJF_ROOT=$HOME/gjf
QUEUE_DIR=$GJF_ROOT/queue
WORK_DIR=$GJF_ROOT/work
NORM_DONE_DIR=$GJF_ROOT/norm_done
ERROR_DONE_DIR=$GJF_ROOT/error_done
LOG=$GJF_ROOT/qsubmit_gauss.log
#------------------------------------------------------------------------

# set up gaussian environment
source $GAUSSIAN_VAR


submit()
{
    exec 2>/dev/null        # turn off all standard error output
    
    # clean scratch before starting
    if [ -d $GAUSS_SCRDIR ]; then
        rm -f $GAUSS_SCRDIR/*
    fi

    local files=$(cd $QUEUE_DIR; ls *.gjf *.com)
    if [ "$files" == "" ]; then
        exit 1
    fi

    # submit gaussian jobs
    local gauss_input
    for gauss_input in $files; do
        local start_time=$(date +%c)
        # convert DOS newlines to unix format, and submit it
        (
          [[ -d $WORK_DIR ]] || mkdir -p $WORK_DIR
          cd $WORK_DIR
          mv $QUEUE_DIR/$gauss_input $WORK_DIR/
          cat $gauss_input|tr -d '\r' \
          |$GAUSSIAN_CMD &> ${gauss_input/%.*/.log}
        )
        
        # wait for a long time
        local str=$(tail $WORK_DIR/${gauss_input%.*}.log |grep "Normal termination")
        local dir_name=$(date "+%Y-%m%d-%H%M.XXXXXX")

        if [ "$str" == "" ]; then
            [[ -d $ERROR_DONE_DIR ]] || mkdir -p $ERROR_DONE_DIR
            local arch_dir=$(mktemp -d $ERROR_DONE_DIR/$dir_name)
            ( cd $WORK_DIR; mv "$gauss_input" *.log *.chk $arch_dir/ )
            echo "--------------------------------------"
            echo "  (II) informational,  (WW) warning   "
            echo "--------------------------------------"
            echo "(WW) Gaussian did not terminate normally "
            echo "(II) Start at $start_time"
            echo "(II) End at `date +%c`"
            echo "(II) From: $QUEUE_DIR/$gauss_input"
            echo "(II) To  : $arch_dir/"
            echo
        else
            [[ -d $NORM_DONE_DIR ]] || mkdir -p $NORM_DONE_DIR
            local arch_dir=$(mktemp -d $NORM_DONE_DIR/$dir_name)
            
            ( cd $WORK_DIR; mv "$gauss_input" *.log *.chk $arch_dir/ )
            echo "--------------------------------------"
            echo "  (II) informational,  (WW) warning   "
            echo "--------------------------------------"
            echo "(II) Start at $start_time"
            echo "(II) End at`date +%c` "
            echo "(II) From: $QUEUE_DIR/$gauss_input"
            echo "(II) To  : $arch_dir/"
            echo
        fi
    done

    #recursive call
    submit
}

if [ -d "$QUEUE_DIR" ]; then
    submit >> $LOG
else
    echo -n "Your $QUEUE_DIR doesn't exist, do you want to creat it?(y/n)"
    read answer

    if [ "$answer" == "y" ]; then
        mkdir -p $QUEUE_DIR
        echo "Now you can put something into $QUEUE_DIR, then restart this command."
    fi
fi

exit 0
