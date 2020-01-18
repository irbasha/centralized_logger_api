from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import LogHandlerModel
from .serializers import LogHandlerSerializer
import base64
import json
import csv
import os

csv_file = settings.LOG_FILE_NAME

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
		json_data = request.data
		if json_data is not None:
			csvdata = open(csv_file, 'a+')
			csvwriter = csv.writer(csvdata)
			if os.stat(csv_file).st_size == 0:
				header = json_data.keys()
				csvwriter.writerow(header)
			csvwriter.writerow(json_data.values())
			csvdata.close()
			return Response(json_data, status=status.HTTP_200_OK)
		return Response(status=status.HTTP_400_BAD_REQUEST)

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
		return query_logs_from_file_storage()

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
		return query_logs_from_file_storage(criteria='context', context=context)

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
		return query_logs_from_file_storage(criteria='timeperiod', timestart=timestart, timestop=timestop)

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
		return query_logs_from_file_storage(criteria='level', level=level)


@api_view(['GET'])
def query_message_filtered_logs(request, msg=None):
	"""
	query_message_filtered_logs function
	takes a single argument msg
	queries the log details matching the message passed in argument
	"""
	dec_msg = base64.b64decode(msg).decode('utf-8')
	if settings.LOGS_STORAGE_DB:
		logdata = LogHandlerModel.objects.filter(message__contains=dec_msg)
		return respond_to_request(logdata)
	else:
		return query_logs_from_file_storage(criteria='message', message=dec_msg)

def respond_to_request(logdata):
	"""
	respond_to_request function
	serializes the logdata and returns as a json response
	"""
	serializer = LogHandlerSerializer(logdata, many=True)
	return Response(serializer.data)

def query_logs_from_file_storage(criteria=None, context=None, level=None, message=None, timestart=None, timestop=None):
	if os.stat(csv_file).st_size == 0:
	    return Response({}, status=status.HTTP_400_BAD_REQUEST)
	else:
		header_field_names_row = []
		header_field_names_length = 0
		row_number = 0
		with open(csv_file, 'r') as f:
			reader = csv.reader(f)
			dict_list = []
			for row in reader:
				if row_number == 0:
					header_field_names_row = row
					header_field_names_length = len(row)
				else:
					if criteria == 'message':
						if message is not None and message not in row:
							continue
					elif criteria == 'level':
						if level is not None and level not in row:
							continue
					elif criteria == 'context':
						if context is not None and context not in row:
							continue
					elif criteria == 'timeperiod':
						if timestart and timestop:
							if not int(timestart) <= int(row[0]) <= int(timestop):
								continue
					else:
						pass

					row_data_dict = {}
					for i in range(header_field_names_length):
						fieldname = header_field_names_row[i]
						fieldvalue = row[i]
						row_data_dict[fieldname] = fieldvalue
					dict_list.append(row_data_dict)
				row_number += 1
			if len(dict_list) == 0:
				return Response(status=status.HTTP_404_NOT_FOUND)
		return Response(dict_list, status=status.HTTP_200_OK)



