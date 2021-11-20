import socket
import json
import struct
import os
import threading


def server_thread(conn):
    while True:
        try:
            res = conn.recv(1024)  # b'get a.txt
            print('用户指令：', res)
            if not res:
                break
            # 解析命令，提取相应命令参数
            cmd = res.decode('utf-8').split()  # ['get', '文件名']
            file_name = cmd[1]
            file_path = '%s/%s' % (share_dir, cmd[1])
            print(file_name)
            if cmd[0] == 'get':
                server_getfile(conn, file_name, file_path)
            elif cmd[0] == 'put':
                server_putfile(conn, file_name, file_path)
        except ConnectionResetError:
            print('断开连接')
            break
    conn.close()


def server_getfile(conn, file_name, file_path):
    '''【把客户端要下载的文件，以读的方式打开，读文件内容发送给客户端】'''
    # 组装包头信息
    header_dict = {
        'file_name': file_name,
        'file_size': os.path.getsize(file_path)  # 获取文件大小
    }
    # 转换包头信息
    header_json = json.dumps(header_dict)
    header_byte = header_json.encode('GBK')
    # 发送包头长度
    conn.send(struct.pack('i', len(header_byte)))
    # 发送包头
    conn.send(header_byte)
    # 发送包内容  自动粘包
    with open(file_path, 'rb') as f:  # 必须要用二进制模式打开
        for line in f:  # 逐行发送，防止发送内容超过几个G的容量，更节省内存
            conn.send(line)
def server_putfile(conn, file_name, file_path):
    '''【把客户端要下载的文件，以读的方式打开，读文件内容发送给客户端】'''
    # 组装包头信息
    header_dict = {
        'file_name': file_name,
        'file_size': os.path.getsize(file_path)  # 获取文件大小
    }
    # 转换包头信息
    header_json = json.dumps(header_dict)
    header_byte = header_json.encode('GBK')
    # 发送包头长度
    conn.recv(struct.pack('i', len(header_byte)))
    # 发送包头
    conn.recv(header_byte)
    # 发送包内容  自动粘包
    with open(file_path, 'rb') as f:  # 必须要用二进制模式打开
        for line in f:  # 逐行发送，防止发送内容超过几个G的容量，更节省内存
            conn.recv(line)


share_dir = r'D:/server/share'  # 下载目录全局

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind(('127.0.0.1', 8080))
soc.listen(5)
while True:
    conn, adder = soc.accept()
    print('客户端连接:', adder)
    threading.Thread(target=server_thread, args=(conn,)).start()
soc.close()
