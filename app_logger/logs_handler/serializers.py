from rest_framework import serializers
from .models import LogHandlerModel


class LogHandlerSerializer(serializers.ModelSerializer):
	class Meta:
		model = LogHandlerModel
		fields = ['timestamp', 'context', 'level', 'message']