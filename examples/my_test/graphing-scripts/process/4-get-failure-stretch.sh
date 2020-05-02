#!/bin/bash
#generate data for creating failure stretch graphs

if [ $# -lt 1 ]; then
        echo "Usage: $0 <test folder>"
        exit
fi
dir=$1

#Remove second folder each time
rm -r $dir/hr/*/second

rm $dir/*.stretch

if [ -d "$dir/hr" ]
then
    y=`ls $dir/ls`

    for j in $y
    do
        for k in $y
        do
             #skip files that don't exist for less than 100% traffic
             if [ ! -f "$dir/hr/$j/ping-data/$k.txt.out" ]
             then
                 continue
             fi

             if [ "$k" != "$j" ]
             then
                  # The single ">" make sures that file is rewritten every time
                  # This commands awks two files, divides the columns, and stores it in a .stretch file
                  # This will ignore the columns that are zero in the second file
                  awk 'FNR==NR{a[FNR]=$2 FS $3;next}{ if (a[FNR] + 0 != 0) print $1 " " $2/a[FNR]}' $dir/ls/$j/ping-data/$k.txt.out $dir/hr/$j/ping-data/$k.txt.out > $dir/hr/$j/ping-data/$k.stretch
             fi
        done
 done
fi

echo "Division is done"


if [ -d "$dir/hr" ] && [ -d "$dir/ls" ]
then

    # All the second data will reside here
    mkdir $dir/hr/second

    for file in $dir/hr/*/ping-data/*.stretch
    do
        # This line appends the stretch value for each second in int(second).second, ignores if stretch is zero
        # Such that in each file the RTT value corresponding to some second (ex 1.something) would be appended to the correct file (1.second)
        cat $file | awk -vdir="$dir" '{ sec=int($1); if ($2 + 0 != 0) print $1 " " $2 >> (dir"/hr/second/"sec".second")}'
    done

    ordered=`ls $dir/hr/second | grep second | sort -n`

    for file in $ordered
    do
        # Making this in one line does not work
        tmp=`cat $dir/hr/second/$file | sort -nk2`
        echo "$tmp" > $dir/hr/second/$file
    done

    for file in $ordered
    do
        # Cat the the sorted seconds file and calculates median, 95th, 75th, 25th, and 5th percentile
        cat $dir/hr/second/$file | awk -vdir="$dir" '{ count[NR] = $2;}END { if (NR % 2) { print count[(NR + 1) / 2] >> (dir"/failure-median.stretch")} else { print (count[(NR / 2)] + count[(NR / 2) + 1]) / 2.0 >> (dir"/failure-median.stretch")} }  END{print count[int(NR*0.95 - 0.5)] >> (dir"/failure-95th.stretch") }  END{print count[int(NR*0.05 - 0.5)] >> (dir"/failure-5th.stretch")}  END{print count[int(NR*0.75 - 0.5)] >> (dir"/failure-75th.stretch")} END{print count[int(NR*0.25 - 0.5)] >> (dir"/failure-25th.stretch")}'
    done
fi
# done

echo "Completed. Stretch data written."
