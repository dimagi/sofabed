from django.test import TestCase
from django.conf import settings
from couchforms.models import XFormInstance
from couchforms.util import post_xform_to_couch
import os
from sofabed.forms.models import FormData
from datetime import date
from sofabed.forms.config import get_formdata_class

class FormDataTestCase(TestCase):
    
    def setUp(self):
        
        for item in XFormInstance.view("couchforms/by_xmlns", include_docs=True, reduce=False).all():
            item.delete()
        
        file_path = os.path.join(os.path.dirname(__file__), "data", "meta.xml")
        with open(file_path, "rb") as f:
            xml_data = f.read()
        
        self.instance = post_xform_to_couch(xml_data)
        
    def testFromInstance(self):
        formdata = FormData.from_xforminstance(self.instance)
        self.assertEqual(date(2010,07,22), formdata.timeStart.date())
        self.assertEqual(date(2010,07,23), formdata.timeEnd.date())
        self.assertEqual("THIS_IS_THE_INSTANCEID", formdata.instanceID)
        self.assertEqual("THIS_IS_THE_DEVICEID", formdata.deviceID)
        self.assertEqual("THIS_IS_THE_USERID", formdata.userID)
        
    def testMatches(self):
        formdata = FormData.from_xforminstance(self.instance)
        self.assertTrue(formdata.matches_exact(self.instance))
        
        formdata.deviceID = "UPDATED_DEVICEID"
        self.assertFalse(formdata.matches_exact(self.instance))
        
        
    def testUpdate(self):
        formdata = FormData.from_xforminstance(self.instance)
        self.instance["form"]["meta"]["deviceID"] = "UPDATED_DEVICEID"
        formdata.update(self.instance)
        self.assertEqual("UPDATED_DEVICEID", formdata.deviceID)
        self.assertTrue(formdata.matches_exact(self.instance))
    
    def testCreateOrUpdate(self):
        self.assertEqual(0, FormData.objects.count())
        
        FormData.create_or_update_from_xforminstance(self.instance)
        self.assertEqual(1, FormData.objects.count())
        self.assertTrue(FormData.objects.all()[0].matches_exact(self.instance))
        
        FormData.create_or_update_from_xforminstance(self.instance)
        self.assertEqual(1, FormData.objects.count())
        self.assertTrue(FormData.objects.all()[0].matches_exact(self.instance))
        
        self.instance["form"]["meta"]["deviceID"] = "UPDATED_DEVICEID"
        FormData.create_or_update_from_xforminstance(self.instance)
        self.assertEqual(1, FormData.objects.count())
        self.assertTrue(FormData.objects.all()[0].matches_exact(self.instance))
        
        self.instance["form"]["meta"]["instanceID"] = "UPDATED_INSTANCEID"
        self.instance._id = "UPDATED_INSTANCEID"
        FormData.create_or_update_from_xforminstance(self.instance)
        self.assertEqual(2, FormData.objects.count())
        self.assertTrue(FormData.objects.get(instanceID="UPDATED_INSTANCEID").matches_exact(self.instance))
        
    def testExtend(self):
        settings.FORMDATA_MODEL = "forms.FormData"
        self.assertEqual(FormData, get_formdata_class())
        