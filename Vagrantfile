Vagrant.configure("2") do |config|
  # Base box (Ubuntu 24.04 LTS)
  config.vm.box = "utm/ubuntu-24.04"
  config.vm.box_version = "0.0.1"

  # Sync the project root into /vagrant inside the VM (default)
  config.vm.synced_folder ".", "/vagrant"

  # Optional: customize VM resources via environment variables
  mem = ENV['VAGRANT_VM_MEMORY'] || "2048"
  cpus = ENV['VAGRANT_VM_CPUS'] || "2"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = mem
    vb.cpus = cpus
  end

  # Forward the Flask port so you can access the app from host
  config.vm.network "forwarded_port", guest: 5000, host: 5000, auto_correct: true

  # Provision the VM using the bundled shell script. The script will write
  # a timing file to /vagrant/vagrant_setup_time.json with start/end/duration.
  config.vm.provision "shell", path: "scripts/provision.sh", privileged: true
end
