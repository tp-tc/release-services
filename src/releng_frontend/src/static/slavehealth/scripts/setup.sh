#! /bin/bash
set -e

ROOT_DIR=${HOME}
SH=${ROOT_DIR}/slave_health

virtualenv ${SH}
cd ${SH}
source bin/activate
wget https://hg.mozilla.org/build/slave_health/raw-file/default/scripts/requires.txt
pip install -r requires.txt

for d in slave_health tools buildbot-configs; do
    hg clone https://hg.mozilla.org/build/${d}
done

ln -s buildbot-configs/mozilla/production_config.py config_builders.py
ln -s buildbot-configs/mozilla-tests/production_config.py config_testers.py
ln -s slave_health/scripts/buildduty_report.py .
cp slave_health/scripts/slave_health.py .
cp slave_health/scripts/slave_health_cron.sh .
cp slave_health/scripts/buildduty_report.sh .
cp slave_health/scripts/last_build_creds.py.template last_build_creds.py

echo "You need to update last_build_creds.py with the connection credentials"
echo "for the buildbot and slavealloc databases."
echo
echo "vi ${SH}/last_build_creds.py"
echo
