""""
代理
完成指令的接收、指令的本地执行、指令执行结果的发送
"""
import udpmodule
import json
import constant
import subprocess
import threading

class Agent:
    # 指定控制器IP地址
    __controller_ip_list = []

    """
    构造函数
    
    :param controller_ip_addr_txt: 定义控制器IP地址的txt文件路径
    """
    def __init__(self):
        self.__get_controller_ip_list_from_file(constant.TXT_CONTROLLER_IP_ADDR)

    """
    从指定txt文件中读取控制器IP，存储在列表中

    :param file_path:   存储控制器IP地址的txt文件路径
    """
    def __get_controller_ip_list_from_file(self, file_path):
        file = open(file_path)
        for line in file.readlines():
            line = line.strip('\n') # 去掉换行
            self.__controller_ip_list.append(line)
        file.close()

    """
    发送响应消息到控制器，告知其指令的执行结果

    :param  controller_ip:      控制器IP地址
    :param  agent_ip:           执行指令的主机IP地址
    :param  cmd:                指令
    :param  cmd_arguments:      执行指令所需的参数
    :param  cmd_result:         指令执行的结果
    :return True:发送成功   False: 发送失败    
    """
    def send_msg(self, controller_ip, agent_ip, cmd, cmd_arguments, cmd_result, logger):
        # 封装成json格式，dumps()将字典转换成json串
        json_msg = json.dumps({'msg_type': 'response',
                               'agent_ip': agent_ip,
                               'cmd': cmd,
                               'cmd_agruments': cmd_arguments,
                               'cmd_result': cmd_result
                              })
        # UDP发送
        send_bytes = udpmodule.send(json_msg, controller_ip, constant.PORT_CONTROLLER)
        if (send_bytes <= 0):
            logger.error(
                "Agent发送失败：{" + cmd + "}响应消息" + " -> {" + str(controller_ip) + "}")
            return False
        else:
            logger.info(
                "Agent发送成功：{" + cmd + "}响应消息" + " -> {" + str(controller_ip) + "}")
            return True

    """
    从监听端口接收来自指定Controller发来的请求消息（json格式字符串），将其转换成字典类型
    检查消息是否来自指定Controller
    
    :param logger:  打印日志
    :return 元组（消息（字典类型），元组（发送方IP地址，端口号））或 空元组
    """
    def recv_msg(self, logger):
        # 元组（数据，元组（发送方IP地址，端口号））
        recv_data = udpmodule.recv(constant.PORT_AGENT)
        msg = json.loads(recv_data[0])  # 转换成字典
        msg_from_addr = recv_data[1]

        # 检查消息是否来自指定控制器，防止接收第三方伪造的请求消息
        msg_from_ip = msg_from_addr[0]
        msg_from_port = msg_from_addr[1]
        valid_msg_from_ip_addr = self.__authenticate_ip(msg_from_ip)

        # 返回
        if (valid_msg_from_ip_addr):
            logger.info("Agent接收成功：来自Controller{" + str(msg_from_ip) + ":" + str(msg_from_port) +"}的{" + msg["cmd"] + "}请求消息")
            return (msg, msg_from_addr)
        else:
            logger.warn(" Agent接收成功：来自未知主机{" + str(msg_from_ip) + ":" + str(msg_from_port) + "}的未知类型{" + msg["cmd"] +"}消息")
            return ()

    """
    解析消息
    1.验证消息来源是否为指定控制器
    2.判断是否为请求消息
    2.根据消息中的指令类型，在本地执行命令，发送响应消息给控制器
    
    :param  msg:                接收的消息（字典类型）
    :param  msg_from_ip:        消息来源（指定控制器IP）
    :param  logger:             打印日志
    :return True：解析消息成功  False：解析消息失败
    """
    def parse_msg(self, msg, msg_from_ip, logger):
        # 判断消息是否来自指定Controller
        if not msg:
            logger.error(" Agent解析消息失败：来自未知主机{" + msg_from_ip + "}")
            return False

        # 判断是否为请求消息
        if msg["msg_type"] != "request":
            logger.error(" Agent解析消息失败：非请求消息，来自{" + msg_from_ip + "}")
            return False

        # TODO：根据agent_ip判断消息是否发给自己


        # 指令执行结果初始化
        retcode = -1
        # 根据cmd在本地执行命令
        if(msg["cmd"] == constant.CMD_COPY_DISK_FILE):
            # sudo scp /var/lib/libvirt/images/node.qcow2 root@192.168.200.132:/var/lib/libvirt/images
            retcode = subprocess.call("scp "
                                      + msg["cmd_arguments"]["vm_disk_file_directory"]+ "/" + msg["cmd_arguments"]["vm_disk_file_name"]
                                      + " " + msg["cmd_arguments"]["dst_host_username"] + "@" + msg["cmd_arguments"]["dst_host_ip"] + ":" + msg["cmd_arguments"]["vm_disk_file_directory"], shell=True)
        elif (msg["cmd"] == constant.CMD_LIVE_MIGRATION):
            # sudo virsh migrate --live --verbose VM1 qemu+ssh://root@192.168.200.131/system tcp://root@192.168.200.131 --unsafe
            retcode = subprocess.call("virsh migrate --live --verbose "
                                      + msg["cmd_arguments"]["vm_name"]
                                      + " qemu+ssh://" + msg["cmd_arguments"]["dst_host_username"] + "@" + msg["cmd_arguments"]["dst_host_ip"] + "/system"
                                      + " tcp://" + msg["cmd_arguments"]["dst_host_username"] + "@" + msg["cmd_arguments"]["dst_host_ip"]
                                      + " --unsafe", shell=True)
        elif (msg["cmd"] == constant.CMD_EXTRACT_CONFIGURE_FILE):
            # sudo virsh dumpxml VM1 > /etc/libvirt/qemu/VM1.xml
            retcode = subprocess.call("virsh dumpxml "
                                      + msg["cmd_arguments"]["vm_name"] + " > "
                                      + msg["cmd_arguments"]["vm_conf_file_directory"] + "/" + msg["cmd_arguments"]["vm_conf_file_name"], shell=True)

        elif (msg["cmd"] == constant.CMD_DEFINE_VIRTUAL_MACHINE):
            # sudo virsh define /etc/libvirt/qemu/VM1.xml
            retcode = subprocess.call("virsh define "
                                      + msg["cmd_arguments"]["vm_conf_file_directory"] + "/" + msg["cmd_arguments"]["vm_conf_file_name"], shell=True)

        # 根据retcode的值（0-255，或-1）来判断指令是否成功执行
        cmd_result = False
        if(retcode == 0):
            cmd_result = True

        # 给控制器发送响应消息
        send_bytes = Agent.send_msg(self, msg_from_ip, msg["agent_ip"], msg["cmd"], msg["cmd_arguments"], cmd_result, logger)
        if(send_bytes <= 0):
            logger.error("Agent处理完来自控制器{" + str(msg_from_ip)  + "}的{" + msg["cmd"] + "}请求消息，向控制器发送响应信息失败！" )
            return False
        else:
            logger.info("Agent处理完来自控制器{" + str(msg_from_ip) + "}的{" + msg["cmd"] + "}请求消息，已向控制发送响应信息")
            return True

    """
    对接收到的消息，进行IP地址认证，只接收来自指定控制器的消息
    
    :param msg_from_ip: 发送该消息的主机IP地址
    :return True：IP地址认证成功   False:IP地址认证失败
    """
    def __authenticate_ip(self, msg_from_ip):
        # 检查消息是否来自指定控制器，防止接收第三方伪造的请求消息
        valid_ip_addr = False
        for ip_addr in self.__controller_ip_list:
            if (msg_from_ip == ip_addr):
                valid_ip_addr = True
                break

        return valid_ip_addr

    """
    创建一个新的进程，调用解析消息函数
    
    :param msg:         消息
    :param msg_from_ip: 发送该消息的主机IP地址
    :param logger:      打印日志
    """
    def create_thread(self, msg, msg_from_ip, logger):
        th1 = threading.Thread(target=Agent.parse_msg, args=(self, msg, msg_from_ip, logger))
        th1.start()
        # TODO：线程结束时才打印这句话
        #logger.info("Agent处理完来自{" + str(msg_from_ip) + "}的消息: {" + msg["cmd"] + "}")
        #th1.join() # 等th1线程执行完毕后才往下执行

