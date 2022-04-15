from django.db import models


# Create your models here.

# class ContainerStatus(object):
#     ContainerRun = "run"
#     ContainerStop = "stop"
#
#
# class ContainerInfo(models.Model):
#     container_name = models.CharField(max_length=50, primary_key=True)
#     container_status = models.CharField(max_length=10, default=ContainerStatus.ContainerStop)
#     volumes_path = models.CharField(max_length=50, default='')
