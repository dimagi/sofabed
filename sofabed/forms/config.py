from django.conf import settings
from django.db import models

def get_formdata_class():
    """
    Gets the class used for storing formdata. Defaults to FormData, but can
    be overridden by defining:
     
        FORMDATA_MODEL = myapp.ModelName 
    
    in your settings file
    """
    formdata_model = getattr(settings, "FORMDATA_MODEL", "forms.FormData")
    app_label, model_name = formdata_model .split('.')
    return models.get_model(app_label, model_name)
