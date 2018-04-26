#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from subprocess import Popen, PIPE
from .models import Delivery
import os
import shutil
from time import sleep
import re
import sh


@shared_task
def deploy(job_name, server_list, app_path, source_address, project_id, auth_info):
    """真正的部署函数"""
    cmd = ""
    p1 = Delivery.objects.get(job_name_id=project_id)
    job_workspace = "/var/opt/adminset/workspace/{0}/".format(job_name)
    log_path = job_workspace + 'logs/'
    log_name = 'deploy-' + str(p1.deploy_num) + ".log"
    with open(log_path + log_name, 'wb+') as f: #部署日志开始
        f.writelines("<h4>Deploying project {0} for {1}th</h4>".format(job_name, p1.deploy_num))
    if not app_path.endswith("/"):
        app_path += "/"

    # clean build code
    p1.bar_data = 20
    p1.save()
    sleep(1)
    if p1.build_clean or p1.version:
        try:
            shutil.rmtree("{0}code/".format(job_workspace)) #递归删除code目录以及目录内的所有内容
        except Exception as msg:
            print("code dir is not exists, build clean over")
    if p1.job_name.source_type == "git":
        cmd = git_clone(job_workspace, auth_info, source_address, p1)
    if p1.job_name.source_type == "svn":
        cmd = svn_clone(job_workspace, auth_info, source_address, p1,log_path,log_name)
    data = cmd_exec(cmd) #把最新的包下载下来
    p1.bar_data = 30
    p1.save()
    with open(log_path + log_name, 'ab+') as f:
        f.writelines(cmd)
        f.writelines(data)
    if p1.shell:#需要执行脚本的，在堡垒机创建好对应目录
        deploy_shell = job_workspace + 'scripts/deploy-' + str(p1.deploy_num) + ".sh"
        deploy_shell_name = 'deploy-' + str(p1.deploy_num) + ".sh"
        with open(deploy_shell, 'wb+') as f:
            f.writelines(p1.shell)
        cmd = "/usr/bin/dos2unix {}".format(deploy_shell)#转成unix格式
        data = cmd_exec(cmd)
    for server in server_list:
        cmd = "rsync --progress -raz --delete --exclude '.git' --exclude '.svn' {0}/code/ {1}:{2}".format(
                job_workspace, server, app_path)#分发代码或包到对端服务器
        data = cmd_exec(cmd)
        with open(log_path + log_name, 'ab+') as f:
            f.writelines(cmd)
            f.writelines(data)
        if p1.shell and not p1.shell_position:  #远端执行shell脚本
            cmd = "scp {0} {1}:/tmp".format(deploy_shell, server)  #脚本复制到目标机器 /tmp
            data = cmd_exec(cmd)
            with open(log_path + log_name, 'ab+') as f:
                f.writelines(data)
            cmd = "ssh {1} '/usr/bin/bash /tmp/{0}'".format(deploy_shell_name, server)  #执行脚本
            data = cmd_exec(cmd)
            with open(log_path + log_name, 'ab+') as f:
                f.writelines(data)
        if p1.bar_data <= 125:
            cur_bar = p1.bar_data
            p1.bar_data = cur_bar+5
            p1.save()
    if p1.shell and p1.shell_position: #堡垒机本地执行shell脚本
        # cmd = "/usr/bin/bash {0}'".format(deploy_shell)
        data = sh.bash(deploy_shell)
        with open(log_path + log_name, 'ab+') as f:
            f.writelines(data)
    p1.bar_data = 130
    p1.status = False
    p1.save()
    with open(log_path + log_name, 'ab+') as f:
        f.writelines("<h4>Project {0} have deployed for {1}th </h4>".format(p1.job_name, p1.deploy_num))
    return data


def cmd_exec(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    data = p.communicate()
    return data


def parser_url(source_address, url_len, user_len, auth_info, url_type=None):
    if url_type:
        new_suffix = source_address[url_len:][user_len:]
        final_add = source_address[:url_len] + auth_info["username"] + ":" + auth_info["password"] + new_suffix
    else:
        new_suffix = source_address[url_len:]
        final_add = source_address[:url_len] + auth_info["username"] + ":" + auth_info["password"] + new_suffix
    return final_add


def git_clone(job_workspace, auth_info, source_address, p1):
    if os.path.exists("{0}code/.git".format(job_workspace)):
        cmd = "cd {0}code/ && git pull".format(job_workspace)
        return cmd
    if auth_info and p1.job_name.source_address.startswith("http"):
        url_type = re.search(r'(@)', source_address)
        if url_type:
            user_len = len(auth_info["username"])
            if source_address.startswith("https://"):
                url_len = 8
            else:
                url_len = 7
            source_address = parser_url(source_address, url_len, user_len, auth_info, url_type)
        else:
            if source_address.startswith("https://"):
                url_len = 8
            else:
                url_len = 7
            source_address = parser_url(source_address, url_len, auth_info, url_type)
    if p1.version:
        cmd = "git clone -b {2} {0} {1}code/".format(source_address, job_workspace, p1.version)
    else:
        cmd = "git clone {0} {1}code/".format(source_address, job_workspace)
    return cmd


def svn_clone(job_workspace, auth_info, source_address, p1,log_path,log_name):
    """实现包裹部署"""
    if p1.version:
        if not source_address.endswith("/") and not p1.version.endswith('/'):
            source_address += '/'
        source_address += p1.version
        # job_version_workspace = "{0}/code/{1}/".format(job_workspace,p1.version)
        # os.system("mkdir -p {0}".format(job_version_workspace))#创建 jobname/1.1/ 目录

    if os.path.exists("{0}code/.svn".format(job_workspace)): #存在就更新,
        cmd = "svn --non-interactive --trust-server-cert --username {2} --password {3} checkout {0} {1}".format(
                source_address, job_workspace, auth_info["username"], auth_info["password"])
    else: #no就checkout
        cmd_0 ='sed -i  "s@# store-plaintext-passwords = no@store-plaintext-passwords = yes@g"  /root/.subversion/servers'
        cmd_1 ='sed -i  "s@# store-passwords = no@store-passwords = yes@g"  /root/.subversion/servers'
        data_0 = cmd_exec(cmd_0)#修改svn ，在命令行连接时允许填充密码
        with open(log_path + log_name, 'ab+') as f:
            f.writelines(data_0)
        data_1 = cmd_exec(cmd_1)
        with open(log_path + log_name, 'ab+') as f:
            f.writelines(data_1)
        cmd = "echo p | svn --non-interactive --trust-server-cert --username {2} --password {3} checkout {0} {1}".format(
                source_address, job_workspace, auth_info["username"], auth_info["password"])
    return cmd
