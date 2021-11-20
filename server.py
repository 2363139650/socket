import socket
import json
import struct
import os
import threading
import prettytable as pt

def show_ip_list():
    global client_addr_list
    tb = pt.PrettyTable()
    tb.field_names = ["IP"]
    for addr in client_addr_list:
        tb.add_row([addr])
    print(tb)

def server_thread(conn, addr):
    show_ip_list()
    while True:
        try:
            res = conn.recv(1024)  # b'get a.txt
            print('用户指令：', res)
            if not res:
                break

            # 解析命令，提取相应命令参数
            cmd = res.decode('utf-8').split()  # ['get', '文件名']
            if cmd[0] == 'get':
                process_get_cmd(conn, cmd)
            elif cmd[0] == 'put':
                process_put_cmd(conn)
        except ConnectionResetError:
            print(addr, '断开连接')
            break
    conn.close()
    client_addr_list.remove(addr)
    show_ip_list()

def process_put_cmd(conn):
    header_size = struct.unpack('i', conn.recv(4))[0]
    # 获得包头
    header_dict = json.loads(conn.recv(header_size).decode('GBK'))
    # 解析包头信息 和 文件夹命名
    total_size = header_dict.get('file_size')
    file_path = '%s/%s' % (share_dir, header_dict.get('file_name'))
    print(file_path)
    # 写入到新的文件
    with open(file_path, 'wb') as f:  # 必须要用二进制模式打开
        recv_size = 0
        while recv_size < total_size:
            lene = conn.recv(1024)
            f.write(lene)
            recv_size += len(lene)


def process_get_cmd(conn, cmd):
    file_name = cmd[1]
    file_path = '%s/%s' % (share_dir, cmd[1])
    print(file_name)
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

client_addr_list = [] # 客户端IP地址集合

share_dir = r'D:/server/share'  # 下载目录全局

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind(('127.0.0.1', 8080))
soc.listen(5)
while True:
    conn, addr = soc.accept()
    client_addr_list.append(addr)
    threading.Thread(target=server_thread, args=(conn,addr, )).start()
soc.close()
