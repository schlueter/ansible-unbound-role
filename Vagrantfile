Vagrant.configure(2) do |config|
  config.vm.box = 'ubuntu/trusty64'

  N = 2
  (1..N).each do |machine_id|
    config.vm.define "unbound#{machine_id}" do |machine|
      machine.vm.hostname = "unbound#{machine_id}.local"
      machine.vm.network "private_network", ip: "192.168.77.#{20+machine_id}"

      config.vm.provision :shell,
        inline: 'sudo apt-get install -y python-minimal'

      if machine_id == N then
        config.vm.provision :ansible,
          playbook: 'playbook.yml',
          groups: { unbound: (1..N).map { |n| "unbound#{n}" }},
          raw_arguments: %w(-vv --diff),
          limit: :all
      end
    end
  end
end
