#!/usr/bin/env bash
set -euo pipefail

# This script reads the timing file from the Vagrant-shared folder,
# then halts and destroys the VM. Run it from the project root.

TIMING_FILE=vagrant_setup_time.json

if [ ! -f "$TIMING_FILE" ]; then
  echo "Timing file $TIMING_FILE not found in project root. Is the VM provisioned?"
  exit 1
fi

echo "Contents of $TIMING_FILE (from host-shared file):"
cat "$TIMING_FILE"

echo "Attempting to ssh into the VM and cat /vagrant/$TIMING_FILE directly (if VM running)"
vagrant ssh -c "cat /vagrant/$TIMING_FILE" || echo "vagrant ssh failed or VM not running"

echo "Halting VM (if running)..."
vagrant halt || echo "vagrant halt returned non-zero"

echo "Destroying VM..."
vagrant destroy -f || echo "vagrant destroy returned non-zero"

echo "Done."
