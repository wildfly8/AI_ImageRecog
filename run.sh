#!/bin/bash

#sleep 2000m # for debugging

if [[ -z "${SECRETS_LOCATION}" ]]
then
      echo "Missing Secret Variable (SECRETS_LOCATION)"
      exit 1
fi
if [[ -z "${LOG_LOCATION}" ]]
then
      echo "Missing Secret Variable (LOG_LOCATION)"
      exit 1
fi

echo "Creating log folder if not exist"
#mkdir -p ${LOG_LOCATION}
#chmod 777 ${LOG_LOCATION}

echo "Using SECRET_LOCATION=${SECRETS_LOCATION}"
echo "Using LOGS=${LOG_LOCATION}"

echo "Showing Contents for some folders"
echo "Logs -> ${LOG_LOCATION}"
echo $(ls "${LOG_LOCATION}")
echo " ******* "
echo $(ls /var/run)
echo " ******* "
echo $(ls /var/run/secrets)
echo " ******* "
FILENAME=config.json
FILE=${SECRETS_LOCATION}/${FILENAME}
if [[ -f "$FILE" ]]; then
    echo "Configuration file found"
else
 echo "File ${FILENAME} not found in ${SECRETS_LOCATION}, we cannot start the application"
 exit 1
fi

MY_PATH=/code/src/
FILE=updates.py
if [[ -f "$MY_PATH$FILE" ]]; then
    echo "Running Wardini Scraper"
    cd ${MY_PATH}
    python3 ${FILE}
    status=$?
    if [[ ${status} -ne 0 ]]; then
      echo "Failed to run Wardini Scraper: $status"
      exit ${status}
    fi
else
 echo "Cannot start application, file not found: ${FILE}"
 echo "Keeping container alive..."
 sleep 2000m
 exit 1
fi
