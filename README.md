# VMMigration
 
## 简介
VMMigration借助virsh实现管理主机上远程控制虚拟机在两台采用[本地存储方式的物理机](https://chentingz.github.io/2019/12/11/%E3%80%8C%E8%99%9A%E6%8B%9F%E5%8C%96%E3%80%8D%E5%9F%BA%E4%BA%8Evirsh%E5%AE%9E%E7%8E%B0%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%8A%A8%E6%80%81%E8%BF%81%E7%A7%BB/#%E5%9F%BA%E4%BA%8E%E6%9C%AC%E5%9C%B0%E5%AD%98%E5%82%A8)上进行在线迁移的需求。

VMMigration由vmmigration和vmmigration-agent两部分组成，分别用于部署在管理机和受控物理机上。

<p align=center>
  <img src="https://github.com/Chentingz/VMMigration/blob/master/imgs/vmmigration%E6%95%B4%E4%BD%93%E6%9E%B6%E6%9E%84.png" width = 75% height = 75%/>
</p>  

## 术语
- 代理：Agent，主要负责接收控制器发来的指令（封装在json格式的消息中），解析并在本地执行相关的命令，部署在需要迁移的源、目的物理机上
- 控制器：Controller，主要负责发送指令，和接收代理执行指令的结果
- 管理机：用于管理物理机的机器，除了需要迁移的源、目的物理机外的第三台机器

## 目录结构
- vmmigration.py：控制器命令，部署在管理机上，根据输入的参数，向代理发送消息指示其进行虚拟机迁移，调用controller.py
- vmmigration-agent.py：代理命令，分别部署在需要迁移的源、目的物理机上，监听控制器发来的消息并在本地执行命令，调用agent.py
- controller.py：控制器类，定义消息的发送、接收、处理。调用udpmodule.py
- agent.py：代理类，定义消息的发送、接收、处理。调用udpmodule.py
- constant.py：常量定义，包括指令、虚拟机磁盘文件路径、合法IP地址列表、Agent和Controller的监听端口
- udpmodule.py：UDP发送、接收的实现
- ControllerIPAddr.txt：合法控制器的IP地址，被Agent.py使用
- AgentIPAddr.txt：合法的代理IP地址，被Controller.py使用

## 使用前需要安装的工具
- 必装
  - ssh：scp和virsh需要依赖ssh服务
  - scp：用于拷贝虚拟机磁盘文件
  - virsh：用于迁移虚拟机
- 可选
  - virt-manager：虚拟机管理可视化界面，方便观察迁移的过程

## 使用前需要进行的配置
- ssh免密码访问：需要迁移的物理机之间需要设置ssh免密码访问，如源物理机需要能够ssh免密码访问目的物理机
- 目录提权：虚拟机磁盘文件、配置文件所在的**目录以及文件**需要有**读写权限**，一般KVM虚拟机磁盘文件所在目录：`/var/lib/libvirt/images/`，虚拟机配置文件所在目录：`/etc/libvirt/qemu`
- 设置合法IP地址:需要在ControllerIPAddr.txt和AgentIPAddr.txt中设置IP地址

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
假设需要将虚拟机VM1从kvm-node1在线迁移至kvm-node2，测试环境如下所示：

```
名称        主机名      IP地址              操作系统          
源物理机    kvm-node1   192.168.111.130     ubuntu-16.04.4-desktop
目的物理机  kvm-node2   192.168.111.132     ubuntu-16.04.4-desktop
虚拟机      VM1         192.168.122.18      ubuntu-16.04.3-server
管理机      BOSS        192.168.111.1       win7
```  
### 1. 安装必要的工具  
   在管理机、源物理机、目的物理机上安装好ssh服务（ssh-server、ssh-client），scp命令，virsh命令

### 2. 配置存放虚拟机磁盘文件、配置文件的目录权限
- 在源、目的物理机上配置存放虚拟机磁盘文件的目录权限
```
chmod -R 777 /var/lib/libvirt
```

- 在目的物理机上配置存放虚拟机配置文件的目录权限
```
chmod -R 777 /etc/libvirt/qemu
```

### 3. 定义合法的控制器、代理IP地址  
- 在ControllerIPAddr.txt添加控制器IP地址
- 在AgentIPAddr.txt添加代理IP地址

![定义合法控制器和代理IP地址](https://github.com/Chentingz/VMMigration/blob/master/imgs/%E5%AE%9A%E4%B9%89%E5%90%88%E6%B3%95%E6%8E%A7%E5%88%B6%E5%99%A8%E5%92%8C%E4%BB%A3%E7%90%86IP%E5%9C%B0%E5%9D%80.png)  

### 4. 验证源物理机上需要在线迁移的虚拟机正在运行
```
virt-manager
```
  ![virt-manager验证源物理机上VM1正在运行](https://github.com/Chentingz/VMMigration/blob/master/imgs/virt-manager%E9%AA%8C%E8%AF%81%E6%BA%90%E7%89%A9%E7%90%86%E6%9C%BA%E4%B8%8AVM1%E6%AD%A3%E5%9C%A8%E8%BF%90%E8%A1%8C.png)  
  ![virt-manager验证目的物理机无虚拟机](https://github.com/Chentingz/VMMigration/blob/master/imgs/virt-manager%E9%AA%8C%E8%AF%81%E7%9B%AE%E7%9A%84%E7%89%A9%E7%90%86%E6%9C%BA%E6%97%A0%E8%99%9A%E6%8B%9F%E6%9C%BA.png)
  
  或者使用  
   ```
  virsh list
  ```
若显示虚拟机VM1处于"running"状态，说明正在运行


### 5. 部署Agent，在源物理机、目的物理机上分别输入
```
python vmmigration-agent.py
```

![源、目的物理机上使用vmmigration-agent命令](https://github.com/Chentingz/VMMigration/blob/master/imgs/%E6%BA%90%E3%80%81%E7%9B%AE%E7%9A%84%E7%89%A9%E7%90%86%E6%9C%BA%E4%B8%8A%E4%BD%BF%E7%94%A8vmmigration-agent%E5%91%BD%E4%BB%A4.png)

### 6. 部署Controller，在管理机上输入
```
python vmmigration.py 192.168.111.130 192.168.111.132 kvm VM1 /var/lib/libvirt/images/node.qcow2 /etc/libvirt/qemu/VM1.xml
```
![管理机上输入vmmigration命令](https://github.com/Chentingz/VMMigration/blob/master/imgs/%E7%AE%A1%E7%90%86%E6%9C%BA%E4%B8%8A%E8%BE%93%E5%85%A5vmmigration%E5%91%BD%E4%BB%A4.png)

### 7. 查看迁移结果

在源物理机上，可通过virt-manager看见VM1已经关闭

![迁移成功_源物理机上VM1已关闭](https://github.com/Chentingz/VMMigration/blob/master/imgs/%E8%BF%81%E7%A7%BB%E6%88%90%E5%8A%9F_%E6%BA%90%E7%89%A9%E7%90%86%E6%9C%BA%E4%B8%8AVM1%E5%B7%B2%E5%85%B3%E9%97%AD.png)

在目的物理机上，可通过virt-manager看见VM1已经运行

![迁移成功_目的物理机上VM1已在运行](https://github.com/Chentingz/VMMigration/blob/master/imgs/%E8%BF%81%E7%A7%BB%E6%88%90%E5%8A%9F_%E7%9B%AE%E7%9A%84%E7%89%A9%E7%90%86%E6%9C%BA%E4%B8%8AVM1%E5%B7%B2%E5%9C%A8%E8%BF%90%E8%A1%8C.png)

## 参考
- [「虚拟化」基于virsh实现虚拟机动态迁移](https://chentingz.github.io/2019/12/11/%E3%80%8C%E8%99%9A%E6%8B%9F%E5%8C%96%E3%80%8D%E5%9F%BA%E4%BA%8Evirsh%E5%AE%9E%E7%8E%B0%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%8A%A8%E6%80%81%E8%BF%81%E7%A7%BB/#%E5%9F%BA%E4%BA%8E%E6%9C%AC%E5%9C%B0%E5%AD%98%E5%82%A8)

