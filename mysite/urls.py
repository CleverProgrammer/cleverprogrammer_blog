"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.urls import include, path
from django.contrib import admin

from django.contrib.auth.views import login
from django.contrib.auth.views import logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', view=login, kwargs={'template_name': 'login.html'}, name='login'),
    path('accounts/logout/', view=logout, kwargs={'template_name': 'logout.html', 'next_page': '/'},
        name='logout'),
    path('', include('blog.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
]
