#!/bin/sh

USERNAME="idpl"
PASSWORD="idpl"
HOSTNAME="localhost:8000"
API_URI="/condor/measurementdata/"

SENDER=$1
RECEIVER=$2
TIME_START=$3
TIME_END=$4
CHECKSUM_EQUAL=$5
DURATION=$6
DATA_SIZE=$7
BANDWIDTH=$8
MEASUREMENT=$9

shift 9
export  "$@"

API_URL=http://$HOSTNAME$API_URI

curl -u $USERNAME:$PASSWORD -H "Content-Type: application/json" -d "{\"source\": \"$SENDER\", \"destination\": \"$RECEIVER\", \"time_start\": $TIME_START, \"time_end\": $TIME_END, \"md5_equal\": $CHECKSUM_EQUAL, \"duration\": $DURATION, \"data_size\": $DATA_SIZE, \"bandwidth\": $BANDWIDTH, \"measurement\": \"$MEASUREMENT\"}" $API_URL
