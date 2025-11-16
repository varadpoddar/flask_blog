Vagrant timing and usage

This project includes a Vagrantfile and a provisioning script that records the VM setup start and end times to `vagrant_setup_time.json` in the project root (shared `/vagrant` inside the VM).

How to use

1. Make sure you have Vagrant and VirtualBox installed on your host.
2. From the project root run:

```bash
vagrant up --provision
```

3. When provisioning completes, inspect the timing file:

```bash
cat vagrant_setup_time.json
# Example output: {"start": 163..., "end": 163..., "duration": 42.12345}
```

Notes
- Repeat `vagrant destroy -f && vagrant up --provision` multiple times to gather average timings.
- The provisioning script installs dependencies and seeds the database. Adjust `scripts/provision.sh` if you want a lighter-weight setup.
