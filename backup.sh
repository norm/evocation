#!/bin/sh

database=${EVOCATION_DB}
bucket=${EVOCATION_BUCKET}
timestamp=`date +'%Y/%m/%Y-%m-%d-%H-%M-%S'`
dumpfile=$( mktemp /tmp/pgdump.XXXXX )

pg_dump -cf $dumpfile $database
aws s3 mv $dumpfile s3://${bucket}/${timestamp}.sql
aws s3 sync --delete media s3://${bucket}/media
