
from django.contrib import admin
from django.urls import path, re_path
from logs_handler import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('loggerapi/pushlog', views.push_log_to_storage, name='push_log_to_storage'),
    path('loggerapi/dumpall', views.query_all_log_entries, name='query_all_log_entries'),
    path('loggerapi/dump/time/<slug:timestart>/<slug:timestop>', views.query_timeperiod_logs, name='query_timeperiod_logs'),
    path('loggerapi/dump/context/<slug:context>', views.query_context_only_logs, name='query_context_only_logs'),
    path('loggerapi/dump/level/<slug:level>', views.query_level_filtered_logs, name='query_level_filtered_logs'),
    re_path(r'^loggerapi/dump/message/(?P<msg>[-A-Za-z0-9+=]{1,50}|=[^=]|={3,})$', views.query_message_filtered_logs, name='query_message_filtered_logs'),
]
