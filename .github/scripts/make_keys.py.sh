#!/bin/bash

cp keys.py.template keys.py
echo "pvwatts_api_key = '${NREL_DEV_API_KEY}'" >> keys.py
echo "developer_nrel_gov_key = '${NREL_DEV_API_KEY}'" >> keys.py

