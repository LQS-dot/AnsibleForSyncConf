项目介绍:
此项目是自动化配置管理Ansible，其中还ansible.cfg是配置文件，hosts中包含了组名bdsec，以及安装时候写入的全局变量IPADDR。
roles 中是各个组件相关的代码及配置，属于Ansible的角色。


role:
     .
├── handlers
│   └── main.yml
├── tasks
│   ├── conf.yml
│   ├── main.yml
│   └── modify_conf.yml
├── templates
│   └── business_manager.cfg.j2
└── vars
    └── business_manager.cfg.yml

其中handles负责控制组件启停，tasks中负责修改vars中的内容和拷贝templates中的模板至对应的位置，templates中是模板，内容来源是vars文件，vars是变量文件。

如果想要增加改查配置，修改修改vars文件和模板文件。
例如想要新增一个配置STAT_DROP=1：

修改business_manager.cfg.yml 变量文件，增加一行
STAT_DROP: 1 (yml文件语法)

修改business_manager.cfg.j2 模板文件，增加一行:
STAT_DROP={{STAT_DROP}}

注意如果变量key值含有 "." ，请在vars变量文件中将 "." 替换为 "_"。