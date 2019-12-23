""""
控制器
完成发送指令、接收指令在远端的执行结果

控制器的部署可能有下列三种情况
1.控制器在源物理机上
2.控制器在目的物理机上
3.控制器在第三台机器
"""
import udpmodule
import json
import constant
import time

class Controller:
    # 指定代理IP地址
    __agent_ip_list = []

    """
    构造函数

    :param controller_ip_addr_txt: 定义控制器IP地址的txt文件路径
    """
    def __init__(self):
        self.__get_agent_ip_list_from_file(constant.TXT_AGENT_IP_ADDR)

    """
    从指定txt文件中读取代理IP，存储在列表中

    :param file_path:   存储代理IP地址的txt文件路径
    """
    def __get_agent_ip_list_from_file(self, file_path):
        file = open(file_path)
        for line in file.readlines():
            line = line.strip('\n')  # 去掉换行
            self.__agent_ip_list.append(line)
        file.close()


    """
    发送“拷贝虚拟机磁盘文件”请求消息给代理（源物理机）

    :param  agent_ip：   执行指令的主机IP地址
    :param  dst_host_username: 目的物理机的用户名
    :param  dst_host_ip: 目的物理机的IP地址
    :param  vm_disk_file_directory: 虚拟机磁盘文件目录
    :param  vm_disk_file_name:  虚拟机磁盘文件名
    :param  logger: 打印日志
    :return True:发送成功   False：发送失败
    """
    def send_copy_msg(self, agent_ip, dst_host_username, dst_host_ip, vm_disk_file_directory, vm_disk_file_name, logger):
        # 组装请求消息
        json_msg = json.dumps({'msg_type': 'request',
                               'agent_ip': agent_ip,
                               'cmd': constant.CMD_COPY_DISK_FILE,
                               'cmd_arguments':
                                   {
                                       "dst_host_username": dst_host_username,
                                       "dst_host_ip": dst_host_ip,
                                       "vm_disk_file_directory": vm_disk_file_directory,
                                       "vm_disk_file_name": vm_disk_file_name,
                                   }
                               })
        # UDP发送
        send_bytes = udpmodule.send(json_msg, agent_ip, constant.PORT_AGENT)
        if (send_bytes <= 0):
            logger.error(" Controller发送失败：{“" + constant.CMD_COPY_DISK_FILE + "”请求消息} -> {" + agent_ip + "}")
            return False
        else:
            logger.info(" Controller发送成功：{“" + constant.CMD_COPY_DISK_FILE + "”请求消息} -> {" + agent_ip + "}")
            return True

    """
    发送“迁移”请求消息给代理（源物理机）
    
    :param  agent_ip：   执行指令的主机IP地址
    :param  dst_host_username: 目的物理机的用户名
    :param  dst_host_ip: 目的物理机的IP地址
    :param  vm_name: 虚拟机名称
    :param  logger: 打印日志
    :return True:发送成功   False：发送失败
    """
    def send_migrate_msg(self, agent_ip, dst_host_username, dst_host_ip, vm_name, logger):
        # 组装请求消息
        json_msg = json.dumps({'msg_type': 'request',
                               'agent_ip': agent_ip,
                               'cmd': constant.CMD_LIVE_MIGRATION,
                               'cmd_arguments':
                                   {
                                       "dst_host_username": dst_host_username,
                                       "dst_host_ip": dst_host_ip,
                                       "vm_name": vm_name,
                                   }
                               })
        # UDP发送
        send_bytes = udpmodule.send(json_msg, agent_ip, constant.PORT_AGENT)
        if (send_bytes <= 0):
            logger.error(" Controller发送失败：{“" + constant.CMD_LIVE_MIGRATION + "”请求消息} -> {" + agent_ip + "}")
            return False
        else:
            logger.info(" Controller发送成功：{“" + constant.CMD_LIVE_MIGRATION + "”请求消息} -> {" + agent_ip + "}")
            return True

    """
   发送“导出虚拟机配置文件”或“定义虚拟机”请求消息给代理（目的物理机）
   
   :param  agent_ip：   执行指令的主机IP地址
   :param  cmd: cmd.CMD_EXTRACT_CONFIGURE_FILE 或 cmd.CMD_DEFINE_VIRTUAL_MACHINE
   :param  vm_name: 虚拟机名称
   :param  vm_conf_file_directory: 虚拟机配置文件所在目录
   :param  vm_conf_file_name: 虚拟机配置文件名
   :param  logger:  打印日志
   :return True:发送成功   False：发送失败
   """
    def send_extract_or_define_msg(self, agent_ip, cmd, vm_name, vm_conf_file_directory, vm_conf_file_name, logger):
        # 组装请求消息
        json_msg = json.dumps({'msg_type': 'request',
                               'agent_ip': agent_ip,
                               'cmd': cmd,
                               'cmd_arguments':
                                   {
                                       "vm_name": vm_name,
                                       "vm_conf_file_directory": vm_conf_file_directory,
                                       "vm_conf_file_name": vm_conf_file_name
                                   }
                               })
        # UDP发送
        send_bytes = udpmodule.send(json_msg, agent_ip, constant.PORT_AGENT)

        text = ""
        if(cmd == constant.CMD_EXTRACT_CONFIGURE_FILE):
            text = "导出虚拟机配置文件"
        elif(cmd == constant.CMD_DEFINE_VIRTUAL_MACHINE):
            text = "定义虚拟机"

        if (send_bytes <= 0):
           #logger.error("" Controller发送失败：{“" + text + "”请求消息} -> {" + agent_ip + "}")
            return False
        else:
            logger.info("Controller发送成功：{“" + text + "”请求消息} -> {" + agent_ip + "}")
            return True

    """
    从监听端口接收来自指定Agent发来的响应消息（json格式字符串），将其转换成字典类型
    检查消息是否来自指定Agent
    
    :param  logger: 打印日志
    :return 元组（消息（字典类型），发送方IP地址）:接收成功   空元组：接收失败
    """
    def recv_msg(self, logger):
        recv_data = udpmodule.recv(constant.PORT_CONTROLLER)
        msg = json.loads(recv_data[0]) # 转换成字典
        msg_from_addr = recv_data[1]

        # 检查消息是否来自指定控制器，防止接收第三方伪造的请求消息
        msg_from_ip = msg_from_addr[0]
        msg_from_port = msg_from_addr[1]
        valid_msg_from_ip_addr = self.__authenticate_ip(msg_from_ip)

        if (valid_msg_from_ip_addr):
            logger.info(" Controller接收成功：来自Agent{" + str(msg_from_ip) + ":" + str(msg_from_port) +"}的{" + msg["cmd"] + "}响应消息")
            return (msg, msg_from_addr)
        else:
            logger.warn(" Controller接收成功：来自未知主机{" + str(msg_from_ip) + ":" + str(msg_from_port) + "}的{" + msg["cmd"] +"}消息")
            return ()

    """
    解析消息
    1.根据msg是否为空来验证消息来源是否为指定Agent
    2.判断是否为响应消息
    3.根据响应消息的cmd_result字段，判断指令是否执行成功

    :param  msg:                接收的消息（字典类型）
    :param  msg_from_ip:        消息来源
    :param  logger:             打印日志
    :return True：指令执行成功  False：指令执行失败
    """
    def parse_msg(self, msg, msg_from_ip, logger):
        # 判断消息是否来自指定Agent
        if not msg:
            return False

        # 判断是否为响应消息
        if msg["msg_type"] != "response":
            return False

        # 根据响应消息的cmd_result字段，判断指令是否执行成功
        if(msg["cmd_result"] == True):
            logger.error("在Agent{" + str(msg_from_ip) + "} 执行指令失败：" + msg["cmd"])
        else:
            logger.info("在Agent{" + str(msg_from_ip) + "} 执行指令成功：" + msg["cmd"])

        return msg["cmd_result"]


    """
    对接收到的消息，进行IP地址认证，只接收来自指定代理的消息

    :param msg_from_ip: 发送该消息的主机IP地址
    :return True：IP地址认证成功   False:IP地址认证失败
    """
    def __authenticate_ip(self, msg_from_ip):
        # 检查消息是否来自指定代理，防止接收第三方伪造的请求消息
        valid_ip_addr = False
        for ip_addr in self.__agent_ip_list:
            if (msg_from_ip == ip_addr):
                valid_ip_addr = True
                break

        return valid_ip_addr