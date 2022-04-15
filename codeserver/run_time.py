import sys, socket
import docker
import time
import re
import os
import urllib3
from flask import Flask
from flask_apscheduler import APScheduler # 引入APScheduler

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE_URL = "tcp://139.224.55.101:2376" #docker ip:端口
PORT = '8443/tcp'
IMAGE_NAME = 'wddx/codeserver-gcc'
SERVER_IP = 'http://139.224.55.101'
VOLUMES_PATH = '/root/student/volumes/'
ROOT_PATH = '/data/docker/volumes/'
TLS_CONFIG = docker.tls.TLSConfig(
  client_cert=('/data/dockertls/cert.pem', '/data/dockertls/key.pem')
)

def get_lastfiletime(userfile_path):
    time_list = []
    for root, dir, files in os.walk(userfile_path):
        for file in files:
            full_path = os.path.join(root, file)
            mtime = os.stat(full_path).st_mtime
            time_list.append(mtime)
    return time_list

def RemoveContainer(container_name,base_url):

    client = docker.DockerClient(base_url=base_url, tls=TLS_CONFIG)
    container = client.containers.get(str(container_name))
    # container_status = ContainerInfo.objects.filter(container_name=str(container_name)).values('container_status')

    # if container_status[0]['container_status'] == ContainerStatus.ContainerRun:
    container.stop()
    container.remove()

    # stu = ContainerInfo.objects.get(container_name=str(container_name))
    # stu.container_status = ContainerStatus.ContainerStop
    # stu.save()
    return 0


def get_logtime(container_name, server_url):
    client1 = docker.DockerClient(server_url, tls=TLS_CONFIG)
    containers = client1.containers.get(container_name)
    log = containers.logs()
    log_str = str(log, encoding='utf-8')
    res = ".*\[(.*)\].*"
    time_list = re.findall(res, log_str)
    for time_l in time_list[::-1]:
        if time_l[0] == '2':
            break
    time_all = time_l.split('T')
    times = time_all[1].split('.')
    time_str = time_all[0] + ' ' + times[0]
    timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)

    return timestamp+28800




#任务配置类
class SchedulerConfig(object):
    JOBS = [
        {
            'id': 'print_job', # 任务id
            'func': '__main__:DeleteContainer', # 任务执行程序
            'args': None, # 执行程序参数
            'trigger': 'interval', # 任务执行类型，定时器
            'seconds': 60, # 任务执行时间，单位秒
        }
    ]
#定义任务执行程序
def DeleteContainer():
    run_time = 3600
    flag = 0
    client = docker.DockerClient(base_url=BASE_URL, tls=TLS_CONFIG)
    cons = client.containers.list()
    used_time = 0
    # user = ContainerInfo.objects.filter(container_status=ContainerStatus.ContainerRun).values('container_name')
    for con in cons:
        # try:
        file_time = get_lastfiletime(ROOT_PATH+con.name+'workspace/')
        log_time = get_logtime(con.name, BASE_URL)
        if file_time:
            file_time = max(file_time)
            used_time = max(file_time, log_time)
        else:
            used_time = log_time

        current_time = time.time()
        if current_time-used_time > run_time:
            RemoveContainer(con.name, BASE_URL)
            print('ok')


    return 0
app = Flask(__name__)
#为实例化的flask引入定时任务配置
app.config.from_object(SchedulerConfig())
if __name__ == '__main__':
    scheduler = APScheduler()  # 实例化APScheduler
    scheduler.init_app(app)  # 把任务列表载入实例flask
    scheduler.start()  # 启动任务计划
    app.run()
