#!/bin/bash
set -e

cd "$( dirname "$0"  )"
cur_dir=$(pwd)
work_dir=/var/opt/adminset/client
# 安装依赖包
os=$(cat /proc/version)
if (echo $os|grep centos) || (echo $os|grep 'Red Hat')
then
    yum makecache fast
    yum install -y epel-release
    yum install -y gcc smartmontools dmidecode python-pip python-devel  libselinux-python dos2unix
elif (echo $os|grep Ubuntu)
then
    apt-get install smartmontools dmidecode python-pip python-dev tofrodos
    sed -i "s/PermitRootLogin/\#PermitRootLogin/g" /etc/ssh/sshd_config
    service ssh restart
else
    echo "your os version is not supported!"
fi


echo "####install pip mirror####"
mkdir -p  ~/.pip
cat <<EOF > ~/.pip/pip.conf
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host=mirrors.aliyun.com
EOF

echo "####install pip packages####"
mkdir -p $work_dir
pip install --upgrade pip
pip install virtualenv==15.2.0
cd $work_dir
/usr/bin/virtualenv --no-site-packages venv
source $work_dir/venv/bin/activate
pip install requests==2.11.1
pip install psutil==5.2.2
pip install schedule==0.4.3

echo "####config adminset agent####"
if (echo $os|grep centos) || (echo $os|grep 'Red Hat')
then
    scp $cur_dir/adminset_agent.py $work_dir
    scp $cur_dir/adminsetd.service /usr/lib/systemd/system/
    dos2unix $work_dir/adminset_agent.py
    dos2unix /usr/lib/systemd/system/adminsetd.service
elif (echo $os|grep Ubuntu)
then
    scp $cur_dir/adminset_agent.py /usr/local/bin/
    scp $cur_dir/adminsetd.service /etc/systemd/system/
    fromdos $work_dir/adminset_agent.py
    fromdos /etc/systemd/system/adminsetd.service
else
    echo "your os version is not supported!"
fi
echo "####client prepare finished!###"
systemctl daemon-reload
chkconfig adminsetd on
service adminsetd start
echo "####client install finished!###"
echo "please using <service adminsetd start|restart|stop> manage adminset agent"
