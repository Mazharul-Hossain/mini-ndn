#!/bin/bash
#generate data for creating convergence graphs

NEW_PING_CONTENT_ID="content from"
NEW_PING_TIMEOUT_ID="timeout"

#NEW_PING_NACK_ID="nack"

#PING_SEARCH_TERMS="$NEW_PING_CONTENT_ID\|$NEW_PING_TIMEOUT_ID\|$NEW_PING_NACK_ID"
PING_SEARCH_TERMS="$NEW_PING_CONTENT_ID\|$NEW_PING_TIMEOUT_ID"

getSecondsFromTimestamp() {

  timestamp=$1

  seconds=${timestamp:0:2}*3600+${timestamp:2:2}*60+${timestamp:4:10}
  seconds=`echo "$seconds" | bc -l`

  echo "$seconds"
}

if [ $# -lt 1 ] ; then
        echo "Usage: $0 <test folder>"
        exit
fi
dir=$1

if [ -d "$dir/hr" ] && [ -d "$dir/ls" ]
then
    y=`ls $dir/hr`

    for type in hr ls
    do
        # getting the smallest timestamp for the routing type
        start=`cat $dir/$type/*/ping-data/*.txt | grep "$PING_SEARCH_TERMS"| awk '{print substr($1,10,12)}' | sort -n | head -1`
        start=${start:0:2}*3600+${start:2:2}*60+${start:4:10}
        start=`echo "$start" | bc -l`
        for j in $y
        do
             name=$j
             rm $dir/$type/$name/ping-data/*.out
             d=`ls $dir/$type/$name/ping-data`

             tmpdir=$dir/$type/$name/ping-data
             for k in $d
             do
                 if [ ${k:(-3)} == "txt" ]
                 then
                     echo "-->Generating data for $tmpdir/$k"
                     # print timestamp along with RTT
                     # stamp=`cat $tmpdir/$k |grep "Ping Reference" | awk '{print $1}' | awk -F'T' '{print $2}'`
                     cat $tmpdir/$k |grep "$PING_SEARCH_TERMS" | awk -vstart="$start" '{ x=substr($1,10,13); sec=substr(x,0,2)*3600+60*substr(x,3,2)+substr(x,5,10); if (NF > 6) {printf "%2f %s\n", sec-start ,$(NF-1);} else printf "%2f %s\n", sec-start, " 0"}' | sed 's/time=//g' > $tmpdir/$k.out
                 fi
              done
        done
    done
else
    echo "Directory error"
fi
