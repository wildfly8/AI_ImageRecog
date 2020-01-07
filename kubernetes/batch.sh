echo "Starting Batch.sh"

echo "Running Container"

# Log the current time to std output so autosys job log file has it
/bin/date

UUID=$(uuidgen)

kubectl run -it --rm=true ${ORG}-${REPO}-${ENV}-pod --namespace ${ORG}-default --overrides='
{
  "kind": "Pod",
  "apiVersion": "v1",
  "metadata": {
    "name": "${ORG}-${REPO}-${ENV}-'${UUID:0:13}'-pod",
    "namespace": "${ORG}-default",
    "labels": {
      "role": "${ORG}-${REPO}-${ENV}"
    }
  },
  "spec": {
   "hostAliases": [{
            "ip": "10.199.1.180",
            "hostnames": ["compass"]
      }
    ],
    "containers": [{
        "name": "${ORG}-${REPO}-${ENV}-'${UUID:0:13}'",
        "image": "imagehub.westernasset.com/${REPO_KEY}/${ORG}/${REPO}:${TAG}",
        "command": ["/code/run.sh"]
      }
    ]
  }
}
' --image=imagehub.westernasset.com/${REPO_KEY}/${ORG}/${REPO}:${TAG} --restart=Never

rc=$?; if [[ ${rc} != 0 ]]; then exit ${rc}; fi
echo "Process Completed"