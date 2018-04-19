"""django_gateone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from webterminal import web_views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve


urlpatterns = [
    url(r'^tree/$',web_views.tree_index,name='tree_index'),
    # url(r'^credentialcreate/$',web_views.CredentialCreate,name='credentialcreate'),
    # url(r'^credentiallist/$',web_views.CredentialList,name='credentiallist'),
    # url(r'^credentialdetailapi/$',CredentialDetailApi,name='credentialdetailapi'),
    # url(r'^serverlist/$',ServerlList,name='serverlist'),
    # url(r'^groupcreate/$',GroupCreate,name='groupcreate'),
    # url(r'^grouplist/$',GroupList,name='grouplist'),
    url(r'^sshlogslist/$',web_views.SshLogList,name='sshlogslist'),
    url(r'^sshterminalkill/$',web_views.SshTerminalKill,name='sshterminalkill'),
    url(r'^sshlogplay/(?P<pk>[0-9]+)/',web_views.SshLogPlay,name='sshlogplay'),
    url(r'^sshterminalmonitor/(?P<pk>[0-9]+)/',web_views.SshTerminalMonitor,name='sshterminalmonitor'),
    url(r'^i18n/', include('django.conf.urls.i18n')), 
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, }),
    ]
