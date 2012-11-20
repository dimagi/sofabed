from couchforms.signals import xform_archived
from django.core.exceptions import ObjectDoesNotExist
from sofabed.forms.config import get_formdata_class

def delete_formref(sender, xform, *args, **kwargs):
    try:
        form = get_formdata_class().objects.get(instanceID=xform.get_id)
        form.delete()
    except ObjectDoesNotExist:
        pass

xform_archived.connect(delete_formref)