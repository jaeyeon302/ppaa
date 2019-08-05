virtual_env="./flask-env"
bjoern_py=bjoern_run.py
log_txt=./log.txt
touch ${log_txt}
deactivate
source ${virtual_env}/bin/activate
python ${bjoern_py} >> ./log.txt
