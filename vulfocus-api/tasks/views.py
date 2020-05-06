from django.shortcuts import render

from rest_framework import viewsets
from .serializers import TaskSetSerializer
from django.http import JsonResponse
from rest_framework.decorators import action
from .models import TaskInfo
from dockerapi.common import R
import json

# Create your views here.


class TaskSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskSetSerializer
    queryset = TaskInfo.objects.all().order_by('-create_date')

    @action(methods=["get"], detail=True, url_path='get')
    def get_task(self, request, pk=None):
        task_info = self.get_object()
        task_msg = task_info.task_msg
        if task_info.task_status == 1:
            return JsonResponse(R.running(msg="执行中", data=str(task_info.task_id)))
        task_info.is_show = True
        task_info.save()
        if task_msg:
            msg = json.loads(task_msg)
            if msg["status"] == 200:
                return JsonResponse(msg, status=200)
            else:
                return JsonResponse(msg, status=msg["status"])
        return JsonResponse(R.ok())

    @action(methods=["post"], detail=True, url_path='batch')
    def get_batch_task(self, request, pk=None):
        task_id_str = request.POST.get("task_ids", "")
        task_id_list = task_id_str.split(",")
        task_list = TaskInfo.objects.filter(task_id__in=task_id_list)
        result = {}
        for task_info in task_list:
            result[str(task_info.task_id)] = {
                "status": task_info.task_status,
                "data": json.loads(task_info.task_msg)
            }
        return JsonResponse(R.ok(data=result))
