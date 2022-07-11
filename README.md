# AnsibleForSyncConf

### This Ansible project is to provide modifying component configuration, restarting services, modifying network card configuration, etc...
---
#### This is the directory structure:
```
├── file_store
│   ├── handlers
│   │   └── main.yml
│   ├── tasks
│   │   ├── conf.yml
│   │   ├── main.yml
│   │   └── modify_conf.yml
│   ├── templates
│   │   └── file_store.cfg.j2
│   └── vars
│       └── file_store.cfg.yml
├── hostname
│   └── tasks
│       ├── main.yml
│       └── modify_conf.yml
├── management
│   ├── handlers
│   │   └── main.yml
│   ├── tasks
│   │   ├── conf.yml
│   │   ├── main.yml
│   │   └── modify_conf.yml
│   ├── templates
│   │   ├── default.j2
│   │   ├── management.j2
│   │   └── network.j2
│   └── vars
│       ├── default.yml
│       └── management.yml
├── network
│   ├── handlers
│   │   └── main.yml
│   └── tasks
│       ├── main.yml
│       └── modify_conf.yml
├── network_only
│   ├── handlers
│   │   └── main.yml
│   └── tasks
│       ├── main.yml
│       └── modify_conf.yml

```  
##### Special is the network role, which uses nmcli to manage network configuration
* tasks/conf.yml (Configuration replacement using template files)
* tasks/modify_conf.yml (Modify the vars directory Shade variable file)
* tasks/main.yml (Responsible for calling conf.yml and modify_conf.yml)
* templates (The template overrides the configuration file, the value source is the variable of vars.)
* handlers (Trigger, triggered by modify_conf.yml and conf.yml)

---
## There are two entrances, the yml file and the py file
```
python3.10-ansible
site.py:
 python3 site.py '{\"role\":\"network\",\"key\":\"IPADDR\",\"value\":\"'$ipaddr'\",\"tags\":\"ansible_hosts\"}'
```
```
site.yml:
  /usr/bin/ansible-playbook site.yml -e \"role=network ifname=$interface ip=$ipaddr gw=$gw4 dns=$dns4 netmask=$netmask key=restart value=$iseffect\"
```
