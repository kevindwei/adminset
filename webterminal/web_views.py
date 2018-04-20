# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.shortcuts import HttpResponse, render
from cmdb.models import HostGroup,Log,Credential
from webterminal.interactive import get_redis_instance
from adminset.settings import MEDIA_URL
from common.views import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
try:
    import simplejson as json
except ImportError:
    import json
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.generic.list import ListView



@login_required()
@permission_verify()
def tree_index(request):
    temp_name = "cmdb/cmdb-header.html"
    server_groups = HostGroup.objects.all()
    return render(request, 'webterminal/index.html', locals())

@login_required()
@permission_verify()
def CredentialCreate(request):
    temp_name = "cmdb/cmdb-header.html"
    if request.method == "POST":
        if request.is_ajax():
            try:
                data = json.loads(request.body)
                id = data.get('id', None)
                action = data.get('action', None)
                fields = [field.name for field in Credential._meta.get_fields()]
                [data.pop(field) for field in data.keys() if field not in fields]
                if action == 'create':
                    obj = Credential.objects.create(**data)
                    obj.save()
                    JsonResponse({'status': True, 'message': 'Credential %s was created!' % (obj.name)})
                elif action == 'update':
                    try:
                        obj = Credential.objects.get(id=id)
                        obj.__dict__.update(**data)
                        obj.save()
                        JsonResponse({'status': True, 'message': 'Credential %s update success!' % (
                            smart_str(data.get('name', None)))})
                    except ObjectDoesNotExist:
                        JsonResponse({'status': False, 'message': 'Request object not exist!'})
                elif action == 'delete':
                    try:
                        obj = Credential.objects.get(id=id)
                        obj.delete()
                        JsonResponse({'status': True, 'message': 'Delete credential %s success!' % (
                            smart_str(data.get('name', None)))})
                    except ObjectDoesNotExist:
                        JsonResponse({'status': False, 'message': 'Request object not exist!'})
                else:
                    JsonResponse({'status': False, 'message': 'Illegal action.'})
            except IntegrityError:
                JsonResponse({'status': False,
                                     'message': 'Credential %s already exist! Please use another name instead!' % (
                                         smart_str(json.loads(request.body).get('name', None)))})
            except Exception, e:
                import traceback
                print traceback.print_exc()
                JsonResponse({'status': False,
                                     'message': 'Error happend! Please report it to adminstrator! Error:%s' % (
                                         smart_str(e))})
            render(request,'webterminal/credentialcreate.html',locals())

@login_required()
@permission_verify()
def SshLogList(request):
    temp_name = "cmdb/cmdb-header.html"
    object_list = Log.objects.all().order_by("-start_time")
    return render(request, 'webterminal/sshlogslist.html', locals())



@login_required()
def SshLogPlay(request,**kwargs):
    # print "ssh",kwargs
    context={}
    temp_name = "cmdb/cmdb-header.html"
    pk = kwargs['pk']
    objects = Log.objects.get(id=pk)
    # print objects.__dict__
    context['logpath'] = '{0}{1}-{2}-{3}/{4}.json'.format(MEDIA_URL,objects.start_time.year,objects.start_time.month,objects.start_time.day,objects.log)
    # context = json.dumps(context)
    return render(request, 'webterminal/sshlogplay.html', locals())

@login_required()
@permission_verify()
def SshTerminalMonitor(request):
    temp_name = "cmdb/cmdb-header.html"
    object_list = Log.objects.all()
    return render(request, 'webterminal/sshlogmonitor.html', locals())

@login_required()
@permission_verify()
def SshTerminalKill(request):
    if request.method == "POST":
        if request.is_ajax():
            channel_name = request.POST.get('channel_name', None)
            print(channel_name)
            try:
                data = Log.objects.get(channel=channel_name)
                if data.is_finished:
                    return JsonResponse({'status': False, 'message': 'Ssh terminal does not exist!'})
                else:
                    data.end_time = now()
                    data.is_finished = True
                    data.save()

                    queue = get_redis_instance()
                    redis_channel = queue.pubsub()
                    queue.publish(channel_name, json.dumps(['close']))
                    return JsonResponse({'status': True, 'message': 'Terminal has been killed !'})
            except ObjectDoesNotExist:
                return JsonResponse({'status': False, 'message': 'Request object does not exist!'})