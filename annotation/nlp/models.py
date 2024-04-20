from django.db import models

# models.py
from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploaded_files/')

from django.db import models

class ModelName(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    button_color = models.CharField(max_length=20, default='lightgray')

class TrainedModel(models.Model):
    model_name = models.ForeignKey(ModelName, on_delete=models.CASCADE)
    model_file = models.FileField(upload_to='trained_models/')
    created_at = models.DateTimeField(auto_now_add=True)