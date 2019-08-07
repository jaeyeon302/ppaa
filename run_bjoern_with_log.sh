#!/usr/bin/env bash
virtual_env="./flask-env"
bjoern_py=bjoern_run.py
log_txt=./log.txt
source ${virtual_env}/bin/activate
python ${bjoern_py} > ${log_txt}
