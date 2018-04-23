#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from accounts.models import UserInfo
import uuid

ASSET_STATUS = (
    (str(1), u"使用中"),
    (str(2), u"未使用"),
    (str(3), u"故障"),
    (str(4), u"其它"),
    )

ASSET_TYPE = (
    (str(1), u"物理机"),
    (str(2), u"虚拟机"),
    (str(3), u"容器"),
    (str(4), u"网络设备"),
    (str(5), u"安全设备"),
    (str(6), u"其他")
    )



class Credential(models.Model):
    """认证协议，帐号密码"""
    protocol_choices = (
        ('ssh-password', _('ssh-password')),
        ('ssh-key', _('ssh-key')),
        ('vnc', _('vnc')),
        ('rdp', _('rdp')),
        ('telnet', _('telnet'))
    )

    dis_name = models.CharField(max_length=40, verbose_name=_('Credential name'), blank=False, unique=True)
    username = models.CharField(max_length=40, verbose_name=_('Auth user name'), blank=False)
    port = models.PositiveIntegerField(default=22, blank=False, verbose_name=_('Port'),help_text="默认端口提示: rdp:3389,ssh:22,vnc:5901,telnet:23")
    method = models.CharField(max_length=40, choices=(('password', _('password')), ('key', _('key'))), blank=False,
                              default='password', verbose_name=_('Method'))
    key = models.TextField(blank=True, verbose_name=_('Key'))
    password = models.CharField(max_length=40, blank=True, verbose_name=_('Password'))
    proxy = models.BooleanField(default=False, verbose_name=_('Proxy'))
    proxyserverip = models.GenericIPAddressField(protocol='ipv4', null=True, blank=True, verbose_name=_('Proxy ip'))
    proxyport = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Proxy port'))
    proxypassword = models.CharField(max_length=40, verbose_name=_('Proxy password'), blank=True)
    protocol = models.CharField(max_length=40, default='ssh-password', choices=protocol_choices,
                                verbose_name=_('Protocol'))
    width = models.PositiveIntegerField(verbose_name=_('width'), default=1024,help_text="rdp:960")
    height = models.PositiveIntegerField(verbose_name=_('height'), default=768,help_text="rdp:575")
    dpi = models.PositiveIntegerField(verbose_name=_('dpi'), default=96)

    def __unicode__(self):
        return self.dis_name

    def clean(self):
        if self.protocol == 'ssh-password' or self.protocol == 'ssh-key':
            if self.method == 'password' and len(self.password) == 0:
                raise ValidationError(_('If you choose password auth method,You must set password!'))
            if self.method == 'password' and len(self.key) > 0:
                raise ValidationError(_('If you choose password auth method,You must make key field for blank!'))
            if self.method == 'key' and len(self.key) == 0:
                raise ValidationError(_('If you choose key auth method,You must fill in key field!'))
            if self.method == 'key' and len(self.password) > 0:
                raise ValidationError(_('If you choose key auth method,You must make password field for blank!'))
            if self.proxy:
                if self.proxyserverip is None or self.proxyport is None:
                    raise ValidationError(
                        _('If you choose auth proxy,You must fill in proxyserverip and proxyport field !'))




class Idc(models.Model):
    ids = models.CharField(u"机房标识", max_length=255, unique=True)
    name = models.CharField(u"机房名称", max_length=255, unique=True)
    address = models.CharField(u"机房地址", max_length=100, blank=True)
    tel = models.CharField(u"机房电话", max_length=30, blank=True)
    contact = models.CharField(u"客户经理", max_length=30, blank=True)
    contact_phone = models.CharField(u"移动电话", max_length=30, blank=True)
    jigui = models.CharField(u"机柜信息", max_length=30, blank=True)
    ip_range = models.CharField(u"IP范围", max_length=30, blank=True)
    bandwidth = models.CharField(u"接入带宽", max_length=30, blank=True)
    memo = models.TextField(u"备注信息", max_length=200, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'数据中心'
        verbose_name_plural = verbose_name


class Host(models.Model):
    hostname = models.CharField(max_length=50, verbose_name=u"主机名", unique=True)
    ip = models.GenericIPAddressField(u"管理IP", max_length=15)
    idc = models.ForeignKey(Idc, verbose_name=u"所在机房", on_delete=models.SET_NULL, null=True, blank=True)
    other_ip = models.CharField(u"其它IP", max_length=100, blank=True)
    asset_no = models.CharField(u"资产编号", max_length=50, blank=True)
    asset_type = models.CharField(u"设备类型", choices=ASSET_TYPE, max_length=30, null=True, blank=True)
    status = models.CharField(u"设备状态", choices=ASSET_STATUS, max_length=30, null=True, blank=True)
    os = models.CharField(u"操作系统", max_length=100, blank=True)
    vendor = models.CharField(u"设备厂商", max_length=50, blank=True)
    up_time = models.CharField(u"上架时间", max_length=50, blank=True)
    cpu_model = models.CharField(u"CPU型号", max_length=100, blank=True)
    cpu_num = models.CharField(u"CPU数量", max_length=100, blank=True)
    memory = models.CharField(u"内存大小", max_length=30, blank=True)
    disk = models.CharField(u"硬盘信息", max_length=255, blank=True)
    sn = models.CharField(u"SN号 码", max_length=60, blank=True)
    position = models.CharField(u"所在位置", max_length=100, blank=True)
    memo = models.TextField(u"备注信息", max_length=200, blank=True)
    credential = models.ForeignKey('Credential',null=True, blank=True)#一台主机有多个认证信息

    def __unicode__(self):
        return self.hostname


class Cabinet(models.Model):
    """机柜"""
    idc = models.ForeignKey(Idc, verbose_name=u"所在机房", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(u"机柜", max_length=100)
    desc = models.CharField(u"描述", max_length=100, blank=True)

    serverList = models.ManyToManyField(
            Host,
            blank=True,
            verbose_name=u"所在服务器"
    )

    def __unicode__(self):
        return self.name


class HostGroup(models.Model):
    name = models.CharField(u"服务器组名", max_length=30, unique=True)
    desc = models.CharField(u"描述", max_length=100, blank=True)

    serverList = models.ManyToManyField(
            Host,
            blank=True,
            verbose_name=u"所在服务器"
    )

    def __unicode__(self):
        return self.name



class IpSource(models.Model):
    net = models.CharField(max_length=30)
    subnet = models.CharField(max_length=30,null=True)
    describe = models.CharField(max_length=30,null=True)

    def __unicode__(self):
        return self.net


class InterFace(models.Model):
    name = models.CharField(max_length=30)
    vendor = models.CharField(max_length=30,null=True)
    bandwidth = models.CharField(max_length=30,null=True)
    tel = models.CharField(max_length=30,null=True)
    contact = models.CharField(max_length=30,null=True)
    startdate = models.DateField()
    enddate = models.DateField()
    price = models.IntegerField(verbose_name=u'价格')

    def __unicode__(self):
        return self.name


class Log(models.Model):
    server = models.ForeignKey(Host, verbose_name=_('Server'))
    channel = models.CharField(max_length=100, verbose_name=_('Channel name'), blank=False, unique=True, editable=False)
    log = models.UUIDField(max_length=100, default=uuid.uuid4, verbose_name=_('Log name'), blank=False, unique=True,
                           editable=False)
    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Start time'))
    end_time = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_('End time'))
    is_finished = models.BooleanField(default=False, verbose_name=_('Is finished'))
    user = models.ForeignKey(UserInfo, verbose_name=_('User'))
    width = models.PositiveIntegerField(default=90, verbose_name=_('Width'))
    height = models.PositiveIntegerField(default=40, verbose_name=_('Height'))

    def __unicode__(self):
        return self.server.hostname