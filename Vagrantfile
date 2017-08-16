Vagrant.configure(2) do |config|
  config.vm.box = 'ubuntu/trusty64'

  config.vm.define "unbound" do |machine|
    machine.vm.hostname = "unbound.local"
    machine.vm.network "private_network", ip: "192.168.77.42"

    config.vm.provision :ansible,
      playbook: 'playbook.yml',
      groups: { unbound: %w(unbound) },
      raw_arguments: %w(-vv --diff),
      limit: :all
  end
end
