#!/bin/bash
job_id=$1
work_time=$(echo $RANDOM |cut -c-2)
echo job $job_id start...
sleep $work_time
echo job $job_id complete
