#! /bin/bash
set -e

SH=${HOME}/slave_health
OUTPUT_DIR=/var/www/html/builds/slave_health
LOCK=${SH}/lockfile_slave_health.cron
lockfile -5 -r 1 ${LOCK} 2>&1 | logger -t slave_health_cron
trap "rm -f $LOCK" EXIT

cd ${SH}
source bin/activate

# Update the required repos
for d in slave_health tools buildbot-configs; do
    if [ -d ${d} ]; then
      pushd ${d}
      hg -q pull -u
      popd
    else
      hg clone http://hg.mozilla.org/build/${d}
    fi
done

if [ ! -e config_builders.py ]; then
  ln -s buildbot-configs/mozilla/production_config.py config_builders.py
fi
if [ ! -e config_testers.py ]; then
  ln -s buildbot-configs/mozilla-tests/production_config.py config_testers.py
fi

# Run the script
cp slave_health/scripts/slave_health.py .
nice -n 19 python slave_health.py -v

# Sync results to output dir
cd ${SH}/slave_health
rsync -qa --delete --exclude .hg/ --exclude .hgignore . ${OUTPUT_DIR}
cd ..
