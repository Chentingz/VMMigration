import socket

# 缓冲区大小
BUFF_SIZE = 1024

"""
UDP发送数据
@parma  data：     数据
@param  ip_addr：  接收方IP地址
@param  port：     接收方端口号
@return 发送数据的字节数
"""
def send(data, ip_addr, port):
    # 创建套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口，发送数据时会从绑定的端口发送，不会再生成随机端口
    #udp_socket.bind(("", 8001))
    # 使用套接字进行数据传输
    # (内容，地址）元组
    send_bytes = udp_socket.sendto(data.encode("utf-8"), (ip_addr, port))
    # 关闭套接字
    udp_socket.close()
    return send_bytes

"""
UDP接收数据
@param  port：   监听端口号
@return 元组（数据，元组（发送方IP，端口号））
"""
def recv(port):
    # 创建套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 使用套接字进行数据接收
    # 必须有一个固定的接收端口,只能接受这个端口来的消息
    udp_socket.bind(("", port))
    # 接收数据
    # recv_from的返回值是元组(数据，元组（发送方IP，端口号）)
    recv_data = udp_socket.recvfrom(BUFF_SIZE)
    # 关闭套接字
    udp_socket.close()
    msg = recv_data[0].decode("utf-8")
    send_addr = recv_data[1]
    return (msg, send_addr)