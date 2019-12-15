# Waits till django is up at localhost:8000

echo Waiting for Django to start at localhost:8000
i=0
while :
do
  if [ $i -gt 8 ]
  then
    echo ERROR: Timeout while trying to set up Django.
    exit 1
  fi
  if nc -z -w 1 127.0.0.1 8000 &> /dev/null
  then
    echo Django server is up
    break
  fi
  sleep 1m 30s
  echo It may take up to 12 minutes to get Django started
  let i++
  echo Tries: $i
done
