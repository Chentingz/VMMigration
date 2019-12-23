"""
指令定义
"""
CMD_COPY_DISK_FILE = "COPY_DISK_FILE"
CMD_LIVE_MIGRATION = "LIVE_MIGRATION"
CMD_EXTRACT_CONFIGURE_FILE = "EXTRACT_CONFIGURE_FILE"
CMD_DEFINE_VIRTUAL_MACHINE = "DEFINE_VIRTUAL_MACHINE"


"""
监听端口
"""
PORT_CONTROLLER = 8001
PORT_AGENT = 8002

TXT_CONTROLLER_IP_ADDR = "./ControllerIPAddr.txt"
TXT_AGENT_IP_ADDR = "./AgentIPAddr.txt"

PATH_VM_CONFIGURE_FILE = "/etc/libvirt/qemu"
PATH_VM_DISK_FILE = "/var/lib/libvirt/images"

"""
请求消息定义
{
    msg_type: request，
    agent_ip: ,
    cmd: ，
    cmd_arguments:
        {
           ...
        }
}

响应消息定义
{
    msg_type: request，
    agent_ip: ,
    cmd: ，
    cmd_arguments:
        {
           ...
        }
    cmd_result: True/False
}
"""



"""
1.拷贝磁盘文件 请求/响应消息：
{
msg_type:request，
agent_ip: src_host_ip_addr，
cmd: copy，
cmd_arguments:
	{
		dst_host_username:
		dst_host_ip: 
		vm_disk_file_directory:
		vm_disk_file_name:
	}
}

{
msg_type:response
agent_ip: src_host_ip_addr
cmd: copy
cmd_arguments:
	{
		dst_host_username:
		dst_host_ip: 
		vm_disk_file_directory:
		vm_disk_file_name:
	}
cmd_result:True / False
}



2.迁移 请求/响应消息：
{
msg_type:request
agent_ip: src_host_ip_addr
cmd: migrate
cmd_arguments:
	{
		dst_host_username: 
		dst_host_ip:
		vm_name: 
	}
}

{
msg_type:response
agent_ip: src_host_ip_addr
cmd: migrate
cmd_arguments:
	{
		dst_host_username: 
		dst_host_ip:
		vm_name: 
	}
cmd_result: Ture / False
}

3.导出配置文件 请求/响应消息：
{
msg_type:request
agent_ip: dst_host_ip_addr
cmd: extract
cmd_arguments:
	{
		vm_name:
		vm_conf_file_diretory:
		vm_conf_file_name:
	}
}

{
msg_type:response
agent_ip: src_host_ip_addr
cmd: extract
cmd_arguments:
	{
		vm_name:
		vm_conf_file_diretory:
		vm_conf_file_name:
	}
cmd_result: Ture / False
}

4.定义配置文件 请求/响应消息：
{
msg_type:request
agent_ip: dst_host_ip_addr
cmd: define
cmd_arguments:
	{
		vm_name: 
		vm_conf_file_diretory:
		vm_conf_file_name:
	}
}

{
msg_type:response
agent_ip: src_host_ip_addr
cmd: extract
cmd_arguments:
	{
		vm_name: 
		vm_conf_file_diretory:
		vm_conf_file_name:
	}
cmd_result: Ture / False
}
"""
