#!/bin/bash
# First-boot installer for the dedicated, newly created lab VM only.
set -euo pipefail
if test -e /opt/income-lab; then
  echo 'Existing /opt/income-lab preserved; bootstrap will not overwrite it.'
  exit 0
fi
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv curl
useradd --system --no-create-home --shell /usr/sbin/nologin income-api
useradd --create-home --shell /bin/bash income-ci
usermod -a -G systemd-journal income-ci
python3 - <<'PY'
import os, urllib.request
from pathlib import Path
req = urllib.request.Request(
    'http://metadata.google.internal/computeMetadata/v1/instance/attributes/income-ci-public-key',
    headers={'Metadata-Flavor': 'Google'})
key = urllib.request.urlopen(req).read()
folder = Path('/home/income-ci/.ssh')
folder.mkdir(mode=0o700)
with (folder / 'authorized_keys').open('xb') as stream:
    stream.write(key)
import pwd
user = pwd.getpwnam('income-ci')
os.chown(folder, user.pw_uid, user.pw_gid)
os.chown(folder / 'authorized_keys', user.pw_uid, user.pw_gid)
os.chmod(folder / 'authorized_keys', 0o600)
PY
test ! -e /etc/sudoers.d/income-lab-restart
python3 - <<'PY'
from pathlib import Path
with Path('/etc/sudoers.d/income-lab-restart').open('x') as stream:
    stream.write('income-ci ALL=(root) NOPASSWD: /usr/bin/systemctl restart income-api\n')
Path('/etc/sudoers.d/income-lab-restart').chmod(0o440)
PY
visudo -cf /etc/sudoers.d/income-lab-restart
mkdir /opt/income-lab
python3 - <<'PY'
import json, urllib.request
from pathlib import Path
req = urllib.request.Request(
    'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
    headers={'Metadata-Flavor': 'Google'})
token = json.load(urllib.request.urlopen(req))['access_token']
req = urllib.request.Request(
    'https://storage.googleapis.com/lday21-income-mlops-dngvinh/deployment/serving-v1.tar.gz',
    headers={'Authorization': 'Bearer ' + token})
with Path('/opt/income-lab/serving-v1.tar.gz').open('xb') as stream:
    stream.write(urllib.request.urlopen(req).read())
PY
tar -xzf /opt/income-lab/serving-v1.tar.gz -C /opt/income-lab
python3 -m venv /opt/income-lab/.venv
/opt/income-lab/.venv/bin/pip install --no-cache-dir -r /opt/income-lab/deploy/requirements-serving.txt
test ! -e /etc/systemd/system/income-api.service
install -m 644 /opt/income-lab/deploy/income-api.service /etc/systemd/system/income-api.service
systemctl daemon-reload
systemctl enable income-api
# Release starts the service only after publishing a model.
echo 'INCOME_LAB_BOOTSTRAP_READY'
echo 'INCOME_LAB_HOST_KEY_BEGIN'
cat /etc/ssh/ssh_host_ed25519_key.pub
echo 'INCOME_LAB_HOST_KEY_END'
