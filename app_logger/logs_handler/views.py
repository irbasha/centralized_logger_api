from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import LogHandlerModel
from .serializers import LogHandlerSerializer
import base64

@api_view(['POST'])
def push_log_to_storage(request):
	"""
	push_log_to_storage function
	takes no arguments
	1. Reads the body content 
	2. Serializes the body content with the model
	3. Saves the data into database and returns success status code
	4. Return 400 Bad request if request body is empty or incorrect
	"""
	if settings.LOGS_STORAGE_DB:
		serializer = LogHandlerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	else:
		print(settings.LOG_FILE_NAME)
		return Response({})

@api_view(['GET'])
def query_all_log_entries(request):
	"""
	query_all_log_entries function
	takes no arguments
	queries all the available log entries and returns as a list. each log entry is json formatted.
	"""
	if settings.LOGS_STORAGE_DB:
		logdata = LogHandlerModel.objects.all()
		return respond_to_request(logdata)
	else:
		return Response({})

@api_view(['GET'])
def query_context_only_logs(request, context=None):
	"""
	query_context_only_logs function
	takes single argument context which is an application identifier for the logs' source
	queries the logs from database filtered by context 
	"""
	if settings.LOGS_STORAGE_DB:
		logdata = LogHandlerModel.objects.filter(context__contains=context)
		return respond_to_request(logdata)
	else:
		return Response({})

@api_view(['GET'])
def query_timeperiod_logs(request, timestart=None, timestop=None):
	"""
	query_timeperiod_logs function
	takes two arguments (timestart, timestop)
	queries the logs from databse for a particular time period
	"""
	if settings.LOGS_STORAGE_DB:
		logdata = LogHandlerModel.objects.filter(timestamp__range=(timestart, timestop))
		return respond_to_request(logdata)
	else:
		return Response({})

@api_view(['GET'])
def query_level_filtered_logs(request, level=None):
	"""
	query_level_filtered_logs function
	takes a single argument level
	queries all the logs from database matching the loglevel passed as argument
	"""
	if settings.LOGS_STORAGE_DB:
		logdata = LogHandlerModel.objects.filter(level__contains=level)
		return respond_to_request(logdata)
	else:
		return Response({})

@api_view(['GET'])
def query_message_filtered_logs(request, msg=None):
	"""
	query_message_filtered_logs function
	takes a single argument msg
	queries the log details matching the message passed in argument
	"""
	if settings.LOGS_STORAGE_DB:
		dec_msg = base64.b64decode(msg).decode('utf-8')
		logdata = LogHandlerModel.objects.filter(message__contains=dec_msg)
		return respond_to_request(logdata)
	else:
		return Response({})

def respond_to_request(logdata):
	"""
	respond_to_request function
	serializes the logdata and returns as a json response
	"""
	serializer = LogHandlerSerializer(logdata, many=True)
	return Response(serializer.data)




