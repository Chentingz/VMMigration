import agent
import constant
import logging

"""
日志设置
"""
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
vmmigration-agent命令，负责接收指令（封装在请求消息中），在本机上执行相应命令，向控制器发送执行结果（封装在响应消息中）

命令用法：
vmmigration-agent.py
"""
def main():
    # 创建一个Agent实例
    agent_instance = agent.Agent()

    # 监听端口并接收消息
    while(True):
        logger.info("Agent正在监听端口：" + str(constant.PORT_AGENT) + "...")
        recv_result = agent_instance.recv_msg(logger)

        msg = recv_result[0]
        msg_addr = recv_result[1]
        msg_from_ip = msg_addr[0]
        msg_from_port = msg_addr[1]
        #logger.info("Agent接收到来自{" + str(msg_from_ip) + ":" +  str(msg_from_port) + "}的消息: {" + msg["cmd"] + "}")

        # TODO: 创建线程处理消息
        agent_instance.create_thread(msg, msg_from_ip, logger)
        #agent_instance.parse_msg(msg, msg_from_ip)
        #logger.info("Agent处理完来自{" + str(msg_from_ip) + ":" +  str(msg_from_port) +"}的消息: {" + msg["cmd"] + "}")

# 调用
if __name__ == '__main__':
    main()