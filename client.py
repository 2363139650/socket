import math
import os
import socket
import struct
import json
import time


def get_speed(total_size, time):
    time = math.ceil(time) if math.ceil(time) == 0 else 1
    origin_speed = total_size / time
    if origin_speed > 1024 * 1024:
        return '%.3f'%(origin_speed/(1024 * 1024)) + 'MB/S'
    elif origin_speed > 1024:
        return '%.3f'%(origin_speed / 1024) + 'KB/S'
    else:
        return '%.3f'%(origin_speed) + 'B/S'


def get_size(total_size):
    if total_size > 1024 * 1024:
        return '%.3f'%(total_size / (1024 * 1024)) + 'MB'
    elif total_size > 1024:
        return '%.3f'%(total_size / 1024) + 'KB'
    else:
        return '%.3f'%(total_size) + 'B'


def process_get():
    '''接收文件的内容，以写的方式打开一个新文件并写入来实现下载功能'''
    # 获取包头长
    header_size = struct.unpack('i', soc.recv(4))[0]
    # 获得包头
    header_dict = json.loads(soc.recv(header_size).decode('GBK'))
    # 解析包头信息 和 文件夹命名
    total_size = header_dict.get('file_size')
    file_path = '%s/%s' % (local_dir, header_dict.get('file_name'))
    print(file_path)
    # 写入到新的文件
    with open(file_path, 'wb') as f:  # 必须要用二进制模式打开
        start_time = time.time()
        recv_size = 0
        while recv_size < total_size:
            lene = soc.recv(1024*1024)
            f.write(lene)
            recv_size += len(lene)
            print('总大小：%s  已下载大小:%s' % (total_size, recv_size))  # 打印下载进度
        end_time = time.time()
        print('下载完成，总大小：', get_size(total_size),  '下载速度为：', get_speed(total_size, end_time-start_time))



def process_put(file_name, conn):
    file_path = '%s/%s' % (local_dir, file_name)
    print(file_name)
    '''【读文件内容发送给服务端】'''
    # 组装包头信息
    header_dict = {
        'file_name': file_name,
        'file_size': os.path.getsize(file_path)  # 获取文件大小
    }
    # 转换包头信息
    header_json = json.dumps(header_dict)
    header_byte = header_json.encode('GBK')
    # 发送包头长度
    soc.send(struct.pack('i', len(header_byte)))
    # 发送包头
    soc.send(header_byte)
    # 发送包内容  自动粘包
    with open(file_path, 'rb') as f:  # 必须要用二进制模式打开
        for line in f:  # 逐行发送，防止发送内容超过几个G的容量，更节省内存
            soc.send(line)

local_dir = r'D:/client/download'  # 下载目录全局  .

soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
conn = soc.connect(('127.0.0.1', 8080))

while True:
    # 发送命令
    cmd = input('>>>').strip()  # get a.txt
    if not cmd:
        continue
    soc.send(cmd.encode('utf-8'))

    method = cmd.split()[0]
    file_name = cmd.split()[1]
    if method == 'get':
        process_get()
    elif method == 'put':
        process_put(file_name, conn)
soc.close()


