#!/bin/sh
set -e

SH=${HOME}/slave_health
cd ${SH}
if [ ! -d slave_health ]; then
  hg clone https://hg.mozilla.org/build/slave_health/
  ln -s slave_health/scripts/buildduty_report.py
else
  hg -q -R slave_health pull -u
fi

if [ ! -d bztools ]; then
  git clone https://github.com/ccooper/bztools.git
else
  cd bztools
  git reset --hard --quiet
  git clean -f -d --quiet
  git pull --quiet
  cd ..
fi

source ${SH}/bin/activate
export PYTHONPATH=${SH}/bztools

python buildduty_report.py -v
