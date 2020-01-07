#!/usr/bin/env bash
# Remember the Container is Running in Debian
# Please make sure to validate the following variables
# - Ensure right Python_Command [python or python3]
# - Create a unique project virtualenv across the applications.

VIRTUALENV_NAME=gup_venv
PYTHON_COMMAND=python3
SRC_CODE=minerva-mail

echo "Creating new virtual env"
${PYTHON_COMMAND} -m virtualenv ${VIRTUALENV_NAME}
status=$?
if [[ ${status} -ne 0 ]]; then
  echo "Failed to Create Virtual Env: $status"
  exit ${status}
fi

echo "Activating virtual env"
source ./${VIRTUALENV_NAME}/bin/activate
status=$?
if [[ ${status} -ne 0 ]]; then
  echo "Failed to Activate Virtual Env: $status"
  exit ${status}
fi

echo "-----------------------------"
echo "Which Python going to be used:"
which python
echo "-----------------------------"

FILE=requirements.dev.txt
if [[ -f "$FILE" ]]; then
    echo "Installing Dev Requirements"
    pip install -r ${FILE}
    status=$?
    if [[ ${status} -ne 0 ]]; then
      echo "Failed to Install Dev Requirements: $status"
      exit ${status}
    fi
else
 echo "No $FILE found, skipping"
fi

FILE=requirements.txt
if [[ -f "$FILE" ]]; then
    echo "Installing Requirements"
    pip install -r ${FILE}
    status=$?
    if [[ ${status} -ne 0 ]]; then
      echo "Failed to Install Requirements: $status"
      exit ${status}
    fi
else
 echo "No $FILE found, skipping"
fi

python -c "import pytest"
status=$?
if [[ ${status} -eq 0 ]]; then
    echo "Running Testing"
    pytest -v
    status=$?
    if [[ ${status} -ne 0 && ${status} -ne 5 ]]; then
      echo "Failed to Run Test Suite: $status"
      exit ${status}
    fi
else
    echo "Pytest command not found, skipping"
fi

python -c "import pylint"
status=$?
if [[ ${status} -eq 0 ]]; then
    echo "Running Lint"
    pylint ${SRC_CODE} -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero > pylint-report.txt
    status=$?
    if [[ ${status} -ne 0 ]]; then
      echo "Failed to Run PyLint: $status"
      exit ${status}
    fi
else
    echo "Pylint command not found, skipping"
fi

python -c "import bandit"
status=$?
if [[ ${status} -eq 0 ]]; then
    echo "Running Bandit"
    # There is no a --exit-zero option
    # https://github.com/PyCQA/bandit/issues/419
    bandit --format json --output bandit-report.json --recursive ${SRC_CODE} || exit 0
else
    echo "Bandit command not found, skipping"
fi
