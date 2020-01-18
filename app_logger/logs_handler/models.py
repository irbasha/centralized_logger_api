from django.db import models

class LogHandlerModel(models.Model):
	timestamp = models.TextField()
	context = models.TextField()
	level = models.TextField()
	message = models.TextField()

