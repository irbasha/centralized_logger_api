from django.test import TestCase, Client
from django.urls import reverse
from .models import LogHandlerModel
from .serializers import LogHandlerSerializer
from rest_framework import status
from django.conf import settings
import json
import base64

client = Client()

class TestLogHandler(TestCase):
	def setUp(self):
		"""
		Test Function - setUp
		Initializes all the data required for testcases
		"""
		LogHandlerModel.objects.create(
			timestamp="1234567891", context="Facebook", level="DEBUG", message="Requested page does not exist"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567892", context="Youtube", level="WARNING", message="Video not found"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567893", context="WhatsApp", level="WARNING", message="Delivery of a message failed"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567894", context="Instagram", level="ERROR", message="Connection to internet failed"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567895", context="WhatsApp", level="WARNING", message="Contact does not exist"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567896", context="WhatsApp", level="WARNING", message="Message content limit exceeded"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567897", context="Youtube", level="INFO", message="Slow network connection"
			)
		LogHandlerModel.objects.create(
			timestamp="1234567898", context="Youtube", level="DEBUG", message="Subscription failed"
			)

		self.strmsg = "Subscription Failed"
		self.str_enc = base64.b64encode(self.strmsg.encode()).decode()

		self.valid_message_log = {
			"timestamp": "1234567899", 
			"context": "Instagram", 
			"level": "WARNING", 
			"message": "Post deletion unsuccessful"
		}
		self.invalid_message_log = {
			"time": "1234567830", 
			"con": "Instagram", 
			"message": "Post deletion unsuccessful"
		}

	def test_log_reader_dump_all_logs(self):
		"""
		test function - test_log_reader_dump_all_logs
		tests api function query_all_log_entries and validates the response
		"""
		response = client.get(reverse('query_all_log_entries'))
		print(response)
		if settings.LOGS_STORAGE_DB:
			alllogs = LogHandlerModel.objects.all()
			self.raise_assert(alllogs, response)
		else:
			self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_reader_filter_with_context_only(self):
		"""
		test function - test_log_reader_filter_with_context_only
		tests api function query_context_only_logs and validates the response
		"""
		response = client.get(reverse('query_context_only_logs', kwargs={'context': 'WhatsApp'}))
		print(response)
		if settings.LOGS_STORAGE_DB:
			contextlogs = LogHandlerModel.objects.filter(context__contains='WhatsApp')
			self.raise_assert(contextlogs, response)
		else:
			self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_reader_filter_with_time_period(self):
		"""
		test function - test_log_reader_filter_with_time_period
		tests api function query_timeperiod_logs and validates the response
		raises assertion error on failure
		"""
		response = client.get(reverse('query_timeperiod_logs', kwargs={'timestart': '1234567891', 'timestop': '1234567894'}))
		print(response)
		if settings.LOGS_STORAGE_DB:
			timeperiodlogs = LogHandlerModel.objects.filter(timestamp__range=('1234567891', '1234567894'))
			self.raise_assert(timeperiodlogs, response)
		else:
			self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_reader_filter_with_log_level(self):
		"""
		test function - test_log_reader_filter_with_log_level
		tests api function query_level_filtered_logs and validates the response
		raises assertion error on failure
		"""
		response = client.get(reverse('query_level_filtered_logs', kwargs={'level': 'WARNING'}))
		print(response)

		if settings.LOGS_STORAGE_DB:
			contextlogs = LogHandlerModel.objects.filter(level__contains='WARNING')
			self.raise_assert(contextlogs, response)
		else:
			self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_reader_filter_with_message(self):
		"""
		test function - test_log_reader_filter_with_message
		tests api function query_message_filtered_logs and validates the response
		"""
		response = client.get(reverse('query_message_filtered_logs', kwargs={'msg': self.str_enc}))
		print(response)

		if settings.LOGS_STORAGE_DB:
			messagelogs = LogHandlerModel.objects.filter(message__contains=self.strmsg)
			self.raise_assert(messagelogs, response)
		else:
			self.assertEqual(response.status_code, status.HTTP_200_OK)

	def raise_assert(self, logdata, response):
		"""
		raise_assert function 
		common function to raise assertion error for all the test cases
		"""
		serializer = LogHandlerSerializer(logdata, many=True)
		self.assertEqual(response.data, serializer.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_writer_push_valid_log(self):
		"""
		test function - test_log_writer_push_valid_log
		tests api function push_log_to_storage and validates the response for a valid post data
		"""
		response = client.post(
			reverse('push_log_to_storage'),
			data = json.dumps(self.valid_message_log),
			content_type='application/json'
			)
		print(response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_log_writer_push_invalid_log(self):
		"""
		test function - test_log_writer_push_invalid_log
		tests api function push_log_to_storage and validates the response for an invalid post data
		"""
		response = client.post(
			reverse('push_log_to_storage'),
			data = json.dumps(self.invalid_message_log),
			content_type='application/json'
			)
		print(response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_log_writer_push_empty_log(self):
		"""
		test function - test_log_writer_push_empty_log
		tests api function push_log_to_storage and validates the response for empty post data
		"""
		response = client.post(
			reverse('push_log_to_storage'),
			data = json.dumps({}),
			content_type='application/json'
			)
		print(response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

