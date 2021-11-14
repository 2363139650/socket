import socket
import struct
import json

download_dir = r'D:/client/download'  # 下载目录全局  .

soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
soc.connect(('127.0.0.1', 8080))

while True:
    # 发送命令
    cmd = input('>>>').strip()  # get a.txt
    if not cmd:
        continue
    soc.send(cmd.encode('utf-8'))

    '''接收文件的内容，以写的方式打开一个新文件并写入来实现下载功能'''
    # 获取包头长
    header_size = struct.unpack('i',soc.recv(4))[0]
    # 获得包头
    header_dict = json.loads(soc.recv(header_size).decode('GBK'))
    # 解析包头信息 和 文件夹命名
    total_size = header_dict.get('file_size')
    file_path = '%s/%s' % (download_dir, header_dict.get('file_name'))
    print(file_path)
    # 写入到新的文件
    with open(file_path,'wb') as f:  # 必须要用二进制模式打开
        recv_size = 0
        while recv_size < total_size:
            lene = soc.recv(1024)
            f.write(lene)
            recv_size += len(lene)
            print('总大小：%s  已下载大小:%s' % (total_size, recv_size))  # 打印下载进度

soc.close()