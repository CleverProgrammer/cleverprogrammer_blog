"""mysite URL Configuration

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
import notifications.urls
from django.conf.urls import include, url
from django.contrib import admin

from django.contrib.auth.views import login
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(regex=r'^accounts/login/$', view=login, kwargs={'template_name': 'login.html'}, name='login'),
    url(regex=r'^accounts/logout/$', view=logout, kwargs={'template_name': 'logout.html', 'next_page': '/'},
        name='logout'),
    url(r'', include('blog.urls')),
    url(r'^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^avatar/', include('avatar.urls'))
]
