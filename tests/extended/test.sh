#!/bin/bash

API_HOME="/home/aaron/sandman2"
EXT_HOME="/home/aaron/extended"
export PYTHONPATH="$EXT_HOME:$API_HOME:$API_HOME/sandman2"

# python $API_HOME/sandman2/scripts/sandman2ctl.py --port 9000 --debug "sqlite+pysqlite:///$EXT_HOME/test.db"
python $API_HOME/sandman2/scripts/sandman2ctl.py --port 9000 --debug --models 'FlatRequest.RTestExt FlatRequest.HTestExt' -e 'rtest htest htestext' "sqlite+pysqlite:///$EXT_HOME/test.db"
