# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cmdb/', include('cmdb.urls')),
    url(r'^navi/', include('navi.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^setup/', include('setup.urls')),
    url(r'^monitor/', include('monitor.urls')),
    url(r'^config/', include('config.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^appconf/', include('appconf.urls')),
    url(r'^delivery/', include('delivery.urls')),
    url(r'^webterminal/', include('webterminal.urls')),
    url(r'^elfinder/', include('elfinder.urls')),
    url(r'^guacamole/', include('guacamole.urls')),
]

if settings.DEBUG:#实现media文件访问
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, }),
    ]