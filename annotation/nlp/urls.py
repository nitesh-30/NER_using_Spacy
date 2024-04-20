from django.urls import path
from . import views

urlpatterns = [
    path('',views.showmodel,name='showmodel'),
    path('file_upload/', views.file_upload, name='file_upload'),
    path('file_upload2/', views.file_upload2, name='file_upload2'),
    path('file_upload3/', views.file_upload3, name='file_upload3'),
    path('file_list', views.file_list, name='file_list'),
    path('display_last_file/', views.display_last_file, name='display_last_file'),
    path('process_data/', views.process_data, name='process_data'),
    path('delete_file/', views.delete_file, name='delete_file'),
    path('showtext/',views.showtagstext,name='showtext'),
    path('trainmodel/',views.trainmodel,name='trainmodel'),
    # path('showmodel/',views.showmodel,name='showmodel'),
    path('storemodelname/',views.storemodelname,name='storemodelname'),
    path('check_training_status/', views.check_training_status, name='check_training_status'),
    path('fileuploadtoseeresult/', views.fileuploadtoseeresult, name='fileuploadtoseeresult'),

]