#!/bin/bash

##say we have 4 CPU cores on the computer
ntasks=4

##run batch job until finish all 20 jobs
ntasks_running=0
for job_id in {1..20}; do

    ./run_job.sh $job_id &

    ntasks_running=$((ntasks_running+1))
    if [ $ntasks_running -eq $ntasks ]; then
        ntasks_running=0
        wait
    fi
done
wait

echo "all jobs are complete"

