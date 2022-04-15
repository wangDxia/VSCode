# """codeserver URL Configuration
#
# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/3.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
from django.urls import path
from CodeserverDocker import views
# from apscheduler.scheduler import Scheduler

# from apscheduler.schedulers.background import BackgroundScheduler
# scheduler = BackgroundScheduler()
# scheduler.add_job(DeleteContainer, 'interval', seconds=60, id='remove_docker')
# scheduler.start()
#
import sys, socket
# from CodeserverDocker.views import DeleteContainer
# try:
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.bind(("127.0.0.1", 47200))
# except socket.error:
#     print('!!!scheduler already started, DO NOTHING')
#
# else:
#     from apscheduler.schedulers.background import BackgroundScheduler
#
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(DeleteContainer, 'interval', seconds=60, id='remove_docker')
#     scheduler.start()
#     print("scheduler started")

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('OpenDockerAPI/', views.OpenDockerAPI.as_view()),
    path('test/', views.testpage),
]
