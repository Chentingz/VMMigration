# VMMigration
 
## 简介
基于Virsh实现虚拟机在两台物理机上进行在线迁移，实现了两条命令：vmmigration和vmmigration-agent

![VMMigration整体架构]("./vmmigration整体架构.png")

## 术语
- 代理：Agent，主要负责接收控制器发来的指令（封装在json格式的消息中），解析并在本地执行相关的命令，部署在需要迁移的源、目的物理机上
- 控制器：Controller，主要负责发送指令，和接收代理执行指令的结果
- 管理机：用于管理物理机的机器

## 目录结构
- vmmigration.py：控制器命令，部署在管理机上，根据输入的参数，向代理发送消息指示其进行虚拟机迁移
- vmmigration-agent.py：代理命令，分别部署在需要迁移的源、目的物理机上，监听控制器发来的消息并在本地执行命令
- controller.py：控制器类，定义消息的发送、接收、处理
- agent.py：代理类，定义消息的发送、接收、处理
- constant.py：常量定义，包括指令、虚拟机磁盘文件路径、合法IP地址列表、Agent和Controller的监听端口
- udpmodule.py：UDP发送、接收的实现
- ControllerIPAddr.txt：合法控制器的IP地址
- AgentIPAddr.txt：合法的代理IP地址

## 使用前需要安装的工具
- ssh：scp和virsh需要依赖ssh服务
- scp：用于拷贝虚拟机磁盘文件
- virsh：用于迁移虚拟机


## 使用方法
- vmmigration命令
```
python vmmigration.py <src_host_ip> <dst_host_ip> <dst_host_username> <vm_name> <vm_disk_file_path> <vm_conf_file_path>

- src_host_ip：源物理机IP地址
- dst_host_ip：目的物理机IP地址
- dst_host_username：目的物理机用户名
- vm_name：虚拟机名
- vm_disk_file：虚拟机磁盘文件路径
- vm_conf_file：虚拟机配置文件路径
```
- vmmigration-agent命令
```
python vmmigration-agent.py 
```



## 例子
1. 安装必要的工具  
   在管理机、源物理机、目的物理机上安装好ssh服务（ssh-server、ssh-client），scp命令，virsh命令

2. 部署Agent  
   在源物理机、目的物理机上分别输入
```
python3 vmmigration-agent.py
``` 
3. 部署Controller  
   在管理机上输入
```
python vmmigration.py 192.168.111.130 192.168.111.132 kvm VM1 /var/lib/libvirt/images/node.qcow2 /etc/libvirt/qemu/VM1.xml
```