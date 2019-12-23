import sys
import controller
import constant
import re
import time
import logging

"""
日志设置
"""
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 接收参数的个数
ARGUMENTS_LEN = 7

"""
命令用法：
vmmigration.py <src_host_ip> <dst_host_ip> <dst_host_username> <vm_name> <vm_disk_file_path> <vm_conf_file_path>
如：vmmigration.py 172.16.0.1 172.16.0.2 kvm VM1 /var/lib/libvirt/images/node.qcow2 /etc/libvirt/qemu/VM1.xml

- src_host_ip：源物理机IP地址
- dst_host_ip：目的物理机IP地址
- dst_host_username：目的物理机用户名
- vm_name：虚拟机名
- vm_disk_file：虚拟机磁盘文件路径，如/var/lib/libvirt/images/node.qcow2
- vm_conf_file：虚拟机配置文件路径，如/etc/libvirt/qemu/VM1.xml
"""
def main():
    # 检查输入的参数个数
    if len(sys.argv) != ARGUMENTS_LEN :
        print("缺少参数，用法：vmmigration.py <src_host_ip> <dst_host_ip> <dst_host_username> <vm_name> <vm_disk_file_path> <vm_conf_file_path>")
        return

    # 获取命令参数
    src_host_ip = sys.argv[1]
    dst_host_ip = sys.argv[2]
    dst_host_username = sys.argv[3]
    vm_name = sys.argv[4]
    vm_disk_file_path = sys.argv[5]
    vm_conf_file_path = sys.argv[6]
    #argumetns_dict = {'src_host_ip':src_host_ip, 'dst_host_ip': dst_host_ip, 'dst_host_username':dst_host_username,'vm_name':vm_name, 'vm_disk_file_path':vm_disk_file_path, 'vm_conf_file_path':vm_conf_file_path}

    # 参数合法性检测
    # if (check_arguments(argumetns_dict) != 0):
    #     print("参数错误")

    # 将vm_disk_file_path拆分成directory和filename，如/test/vm.qcow2 -> /test和vm.qcow2
    vm_disk_file = get_file_directory_and_name(vm_disk_file_path)
    vm_conf_file = get_file_directory_and_name(vm_conf_file_path)

    # 创建一个Controller实例
    controller_instance = controller.Controller()

    # 发送"拷贝虚拟机磁盘文件"指令到源物理机上
    send_result = controller_instance.send_copy_msg(src_host_ip,dst_host_username,dst_host_ip, vm_disk_file[0], vm_disk_file[1], logger)
    if(not send_result):
        #logger.error("Controller已发送请求消息至{" + src_host_ip + "}失败：" + "指令：{" + constant.CMD_COPY_DISK_FILE + "}")
        return
    #logger.info("Controller已发送请求消息至{" + src_host_ip + "}：" + "指令：{" + constant.CMD_COPY_DISK_FILE + "}")

    # 接收“拷贝”响应信息
    recv_result = controller_instance.recv_msg(logger)
    msg = recv_result[0]
    msg_from_ip = recv_result[1][0]
    parse_result = controller_instance.parse_msg(msg, msg_from_ip, logger)
    if not parse_result :
        #logger.error("在Agent{" + str(msg_from_ip) +"} 执行指令失败：" + constant.CMD_COPY_DISK_FILE)
        return
    #logger.info("在Agent{" + str(msg_from_ip) + "} 执行指令成功：" + constant.CMD_COPY_DISK_FILE)

    # 发送"在线迁移"指令到源物理机上
    send_result = controller_instance.send_migrate_msg(src_host_ip, dst_host_username, dst_host_ip, vm_name, logger)
    if (not send_result):
        #logger.error("Controller发送请求消息至{" + src_host_ip + "}失败：" + "指令：{" + constant.CMD_LIVE_MIGRATION + "}")
        return

    #logger.info("Controller已发送请求消息至{" + src_host_ip + "}：" + "指令：{" + constant.CMD_LIVE_MIGRATION + "}")

    # 接收“迁移”响应信息
    recv_result = controller_instance.recv_msg(logger)
    msg = recv_result[0]
    msg_from_ip = recv_result[1][0]
    parse_result = controller_instance.parse_msg(msg, msg_from_ip, logger)
    if not parse_result:
        #logger.error("在Agent{" + str(msg_from_ip) + "} 执行指令失败：" + constant.CMD_LIVE_MIGRATION)
        return
    #logger.info("在Agent{" + str(msg_from_ip) + "} 执行指令成功：" + constant.CMD_LIVE_MIGRATION)

    # 发送"导出虚拟机配置文件"指令到目的物理机上
    send_result = controller_instance.send_extract_or_define_msg(dst_host_ip, constant.CMD_EXTRACT_CONFIGURE_FILE, vm_name, vm_conf_file[0], vm_conf_file[1], logger)
    if (not send_result):
        #logger.error("Controller发送请求消息至{" + dst_host_ip + "}失败：" + "指令：{" + constant.CMD_EXTRACT_CONFIGURE_FILE + "}")
        return
    #logger.info("Controller已发送请求消息至{" + dst_host_ip + "}：" + "指令：{" + constant.CMD_EXTRACT_CONFIGURE_FILE + "}")

    # 接收“导出虚拟机配置文件”响应信息
    recv_result = controller_instance.recv_msg(logger)
    msg = recv_result[0]
    msg_from_ip = recv_result[1][0]
    parse_result = controller_instance.parse_msg(msg, msg_from_ip, logger)
    if not parse_result:
       # logger.error("在Agent{" + str(msg_from_ip) + "} 执行指令失败：" + constant.CMD_EXTRACT_CONFIGURE_FILE)
        return
   # logger.info("在Agent{" + str(msg_from_ip) + "} 执行指令成功：" + constant.CMD_EXTRACT_CONFIGURE_FILE)

    # 发送"定义虚拟机"指令到目的物理机上
    send_result = controller_instance.send_extract_or_define_msg(dst_host_ip, constant.CMD_DEFINE_VIRTUAL_MACHINE, vm_name, vm_conf_file[0], vm_conf_file[1], logger)
    if (not send_result):
       # logger.error("Controller发送请求消息至{" + dst_host_ip + "}失败：" + "指令：{" + constant.CMD_DEFINE_VIRTUAL_MACHINE + "}")
        return
    #logger.info("Controller已发送请求消息至{" + dst_host_ip + "}：" + "指令：{" + constant.CMD_DEFINE_VIRTUAL_MACHINE + "}")

    # 接收“定义虚拟机”响应信息
    recv_result = controller_instance.recv_msg(logger)
    msg = recv_result[0]
    msg_from_ip = recv_result[1][0]
    parse_result = controller_instance.parse_msg(msg, msg_from_ip, logger)
    if not parse_result:
        #logger.error("在Agent{" + str(msg_from_ip) + "} 执行指令失败：" + constant.CMD_DEFINE_VIRTUAL_MACHINE)
        return
    #logger.info("在Agent{" + str(msg_from_ip) + "} 执行指令成功：" + constant.CMD_DEFINE_VIRTUAL_MACHINE)

    logger.info(vm_name + "迁移成功：" + src_host_ip + " -> " + dst_host_ip)

"""
从文件路径中获得文件所在目录与文件名
如：输入文件路径：/var/lib/libvirt/images/node.qcow2
返回（/var/lib/libvirt/images/, node.qcow2）

:param  file_path：  文件路径
:return 元组（文件所在目录，文件名）
"""
def get_file_directory_and_name(file_path):
    last_slash_pos = file_path.rfind("/")
    file_directory = file_path[0:last_slash_pos]
    file_name = file_path[last_slash_pos+1:]
    return (file_directory, file_name)


"""
参数合法性检测（检测IP地址和文件路径是否合法）

:param arguments_dict： 参数字典
：return True：参数合法  False：参数错误或缺少参数
"""
def check_arguments(argumetns_dict):
    if(check_ip_addr(argumetns_dict["src_host_ip"]) == False or  check_ip_addr(argumetns_dict["dst_host_ip"]) == False):
        return False
    # TODO:文件路径合法性检测
    # if(check_file_path(arguments_dict["vm_disk_file_path"]) == False or check_file_path(arguments_dict["vm_conf_file_path"]) == False
    return True

"""
IP地址合法性检测

:param ip_addr： IP地址
：return True：IP地址合法  False：IP地址非法
"""
def check_ip_addr(ip_addr):
    compile_ip = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ip_addr):
        return True
    else:
        return False

"""
从指定txt文件中读取代理IP，存储在列表中
TODO：将这个函数封装在Controller类里面
:param file_path:   存储代理IP地址的txt文件路径
:return 代理IP地址列表
"""
def get_agent_ip_addr_list(file_path):
    agent_ip_addr_list = []
    file = open(file_path)
    for line in file.readlines():
        line = line.strip('\n')
        agent_ip_addr_list.append(line)
    file.close()
    return agent_ip_addr_list




# 调用
if __name__ == '__main__':
    main()