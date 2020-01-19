# LOGGER - RESTful API

LOGGER is a Django REST API to Read and Write Logs from different sources in to Database or File Storage. Storage type is configurable in Django settings.

Supports basic Http operations GET and POST to Read and Write Logs.

### Installation
This REST API requires Python 3 and Django 2.1 to run.
Follow the below steps on a Linux Server to run this API.

```sh
$ python3 -m venv env
$ source env/bin/activate
$ pip install django==2.1
$ pip install djangorestframework
$ git clone https://github.com/irbasha/centralized_logger_api.git
$ cd centralized_logger_api
$ cd app_logger
$ python manage.py makemigraions
$ python manage.py migrate
```

### Tech
Logs to be recorded are sent in a json format with following fields,
- timestamp (unix time stamp)
- context (Source of the Log)
- level (Log severity level)
- message (Actual log message)

Example:
```
{"timestamp": "1234567890", "context": "Whatsapp", "level": "WARNING", "message": "Failed to send message"}
```

Logs can be sent to server and store it over a POST requet. Execute below curl command to test.
```
$ curl -H "Content-Type:application/json" -X POST http://localhost:8000/loggerapi/pushlog -d '{"timestamp": "1234567890", "context": "Whatsapp", "level": "WARNING", "message": "Failed to send message"}'
```


Logs are stored either in configured database or into Files as CSV Data. Stored Logs can also be read over a simple Http GET Request.

- Logs can be filtered for a particular time period provided time in unix time stamp in a request.
Example:
    ```
    curl http://localhost:8000/loggerapi/dump/time/1234567890/1234567892
    ```
- Logs can be filtered using the context (source application identifier), say example; whatsapp logs.
Example:
    ```
    curl http://localhost:8000/loggerapi/dump/context/Whatsapp
    ```
- Logs can be filtered based on the log severity level too.
Example:
    ```
    curl http://localhost:8000/loggerapi/dump/level/WARNING
    ```
- Lastly, logs can also be filtered using Log Messages but with a change. Log message is to be base64 encoded and added to the request. To query a log for message    `Failed to Send Message`. The encoded string of that message is `RmFpbGVkIFRvIFNlbmQgTWVzc2FnZQ==` and request to be sent is,
Example:
    ```
    $ curl http://localhost:8000/loggerapi/dump/message/RmFpbGVkIFRvIFNlbmQgTWVzc2FnZQ==
    ```



### Testing
LOGGER API comes with a set of unit tests to verify all the functionalities automatically.
After the Installation, Execute below command from Project directoy to initiate testing.

```
$ python manage.py test
```

Output:
```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
<Response status_code=200, "application/json">
.<Response status_code=200, "application/json">
.<Response status_code=200, "application/json">
.<Response status_code=200, "application/json">
.<Response status_code=200, "application/json">
.<Response status_code=400, "application/json">
.<Response status_code=400, "application/json">
.<Response status_code=200, "application/json">
.
----------------------------------------------------------------------
Ran 8 tests in 0.166s

OK
Destroying test database for alias 'default'...
```

This test module has all basic test scenarios including two negative testcases. You can also use Postman tool or execute above mentioned curl commands to test this API.

### KeyNotes
- This API uses sqlite as a default database for storing logs. To use MySQL, Change the database backend to MySQL in django settings, and provide database details such as database name, login id and password if any.
- By Default Logs storage type is configured to Database. To use File System, Change the Setting LOGS_STORAGE_DB from True to False in Django Settings. By default it is set to True. On False, Logs will be stored in a CSV File in a logs directory in Project's Base directory.
- Django test module contains all the basic tests need to check the API's functionality with sample input and output for each test.
