from django.db import models
from django.utils import timezone


class KeyTable(models.Model):
    api_key = models.CharField(max_length=32, primary_key=True)
    usage_limit = models.IntegerField(default=0)
    total_usage = models.IntegerField(default=0)


class TrackingInfo(models.Model):
    api_key = models.ForeignKey(KeyTable, on_delete=models.CASCADE, null=True)
    request_ip = models.CharField(max_length=50, blank=False, null=False)
    request_id = models.CharField(max_length=32, blank=False, null=False, default="request_id")
    endpoint_name = models.TextField(null=True, blank=True)
    request_url = models.TextField()
    request_received_time = models.DateTimeField(default=timezone.now)
    response_code = models.IntegerField(null=False, blank=False)
    response_json = models.TextField(null=False, blank=False)
    response_sent_time = models.DateTimeField(default=timezone.now)