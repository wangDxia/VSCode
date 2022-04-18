from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
# from CodeserverDocker.models import ContainerInfo, ContainerStatus
import time
import re
import shutil
import os
import random
import yaml
import docker
import sys
import socket
from codeserver.settings import VOLUMES_PATH, SERVER_IP, BASE_URL, IMAGE_NAME, PORT, TLS_CONFIG,PASSWORD_PATH,ROOT_PATH,DATA_PATH
import requests, json
from django.views import View
import urllib3
import hashlib
import logging
logger = logging.getLogger('django')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Create your views here.


def testpage(request):

    return render(request, 'test.html')

class OpenDockerAPI(View):

    def get(self, request):
        # username = request.GET['user_id']
        logger.info('OpenDocker start...')
        access_token = request.GET.get('access_token')
        #从水杉获取用户信息
        url = 'http://api.shuishan.net.cn/api/user/oauth/info'
        data = {"accessToken": access_token, "appId": "vscode"}
        res = requests.post(url=url, json=data)
        if res.status_code != 200:
            return HttpResponse("post failed")
        if json.loads(res.text)['respCode'] != '20000':
            return HttpResponse("wrong access_token")
        user_dic = json.loads(res.text)['data']['data']
        logger.info(user_dic)
        if user_dic == None:
            return HttpResponse("学号为空！")
        username = user_dic['userNumber']

        if user_dic['passwdSha256'] == None:
            password_sha = hashlib.sha256(str(username).encode('utf-8')).hexdigest()
        else:
            password_sha = user_dic['passwdSha256']
        logger.info(password_sha)

        client = docker.DockerClient(base_url=BASE_URL, tls=TLS_CONFIG)
        cons = client.containers.list()

        #判断容器是否已经创建
        flag = 0
        for con in cons:
            if con.name == username:
                flag=1
                break
        if flag == 1:
            #如果已经创建，只需要获取容器的映射端口
            client = docker.DockerClient(base_url=BASE_URL, tls=TLS_CONFIG)
            container = client.containers.get(str(username))
            container.start()
            container = client.containers.get(str(username))
            user_ports = container.ports[PORT][0]['HostPort']
            logger.info(username+'start container')
        else:
            #如果没有创建，需要创建容器，再获取映射端口
            container = CreateDocker(username,password_sha)
            container.start()
            client = docker.DockerClient(base_url=BASE_URL, tls=TLS_CONFIG)
            container = client.containers.get(str(username))
            user_ports = container.ports[PORT][0]['HostPort']
            logger.info(username + 'creat container')
        docker_path = 'http://'+SERVER_IP + ':' + user_ports
        data = {'data': docker_path}
        return redirect(docker_path)
        # return JsonResponse(data)
        
def docker_filecopy(root_path,data_path,user_id):

    user_dirs = root_path + user_id
    if not os.path.exists(user_dirs):
        shutil.copytree(data_path, user_dirs+'//')
    return user_dirs

def CreateDocker(user_id,password):
    #创建容器

    port = get_free_port()
    client = docker.DockerClient(base_url=BASE_URL, tls=TLS_CONFIG)
    volumes_path = str(user_id)
    password_path = creat_file(user_id,password)
    # user_dirs = docker_filecopy(ROOT_PATH,DATA_PATH,user_id)
    volumes = {'/etc/localtime': {'bind': '/etc/localtime', 'mode': 'rw'},
               password_path: {'bind': '/config/.config/code-server', 'mode': 'rw'}
               }
    #设置sudo passwd
    try:
        v = client.volumes.get(volumes_path+'workspace')
        environment = ["HASHED_PASSWORD=" + password, 'TZ=Asia/Shanghai']
    except docker.errors.NotFound:
        environment = [ 'SUDO_PASSWORD=user',"HASHED_PASSWORD=" + password, 'TZ=Asia/Shanghai']
    volumes_mount1 = docker.types.Mount(target='/config/workspace', source=volumes_path+'workspace')
    volumes_mount2 = docker.types.Mount(target='/config/extensions', source=volumes_path+'extensions')
    volumes_mount3 = docker.types.Mount(target='/config/data', source=volumes_path + 'data')
    m1 = docker.types.Mount(target='/bin', source=str(user_id) + 'bin')
    m2 = docker.types.Mount(target='/lib', source=str(user_id) + 'lib')
    m3 = docker.types.Mount(target='/usr', source=str(user_id) + 'usr')
    m4 = docker.types.Mount(target='/var', source=str(user_id) + 'var')
    m5 = docker.types.Mount(target='/etc', source=str(user_id) + 'etc')
    container = client.containers.create(image=IMAGE_NAME, name=str(user_id),environment=environment,cap_add=["SYS_PTRACE"], mounts=[volumes_mount1,volumes_mount2,volumes_mount3,m1,m2,m3,m4,m5], volumes=volumes,ports={PORT: port}, detach=True)
    return container


def creat_file(user_id,password):
    #创建需要映射的密码文件
    dirs = PASSWORD_PATH + str(user_id) + '/.config/'
    yaml_obj = {'bind-addr': '127.0.0.1:8080', 'auth': 'password', 'password': [], 'cert': 'false'}
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    with open(dirs + "config.yaml", "w") as yaml_file:
        yaml_obj["password"] = password
        yaml_obj["cert"] = 'false'
        yaml.dump(yaml_obj, yaml_file)
    path = dirs
    return path

def Get_Port():
    port = random.randint(8001, 9000)
    return port

def isInuseLinux(port):
    if os.popen('netstat -na | grep :' + str(port)).readlines():
        portIsUse = True
    else:
        portIsUse = False
    return portIsUse

def get_free_port():

    flag = True
    while(1):
        port = random.randint(8001, 9000)
        if not isInuseLinux(port):
            flag = False
            break
    return port