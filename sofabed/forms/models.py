from django.db import models
from django.contrib.auth.models import *
from sofabed.forms.exceptions import InvalidMetaBlockException,\
    InvalidFormUpdateException
from couchdbkit.ext.django.schema import Document, IntegerProperty

class Checkpoint(Document):
    """
    Saves the current state of the sync.
    """
    seq = IntegerProperty()
    
    @classmethod
    def set_checkpoint(cls, id, seq):
        if cls.get_db().doc_exist(id):
            doc = cls.get(id)
        else:
            doc = cls()
            doc._id = id
        doc.seq = seq
        doc.save()
    
    @classmethod
    def get_last_checkpoint(cls, id):
        if cls.get_db().doc_exist(id):
            return cls.get(id).seq
        else:
            return 0
        
class FormDataBase(models.Model):
    """
    Data about a form submission.
    
    This class can be extended for application specific properties.
    """
    
    # meta properties
    instanceID = models.CharField(unique=True, primary_key=True, max_length=255)
    timeStart = models.DateTimeField()
    timeEnd= models.DateTimeField()
    deviceID = models.CharField(max_length=255, blank=True)
    userID = models.CharField(max_length=255, blank=True)
    
    # form properties
    xmlns = models.CharField(max_length=1000, blank=True)
    version = models.CharField(max_length=100, blank=True)
    uiversion = models.CharField(max_length=100, blank=True)

    # submission properties
    received_on = models.DateTimeField()
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return "FormData: %s" % self.instanceID
        
    def update(self, instance):
        """
        Update this object based on an XFormInstance doc
        """
        if not instance.metadata:
            raise InvalidMetaBlockException("Instance %s didn't have a meta block!" % instance.get_id)
        
        if instance.metadata.instanceID and instance.metadata.instanceID != instance.get_id:
            # we never want to differentiate between these two ids
            raise InvalidMetaBlockException("Instance had doc id (%s) different from meta instanceID (%s)!" %\
                                            instance.get_id, instance.metadata.instanceID)
        
        if self.instanceID and self.instanceID != instance.get_id:
            # we never allow updates to change the instance ID
            raise InvalidFormUpdateException("Tried to update formdata %s with different instance id %s!" %\
                                             (self.instanceID, instance.get_id))
        
        if not instance.metadata.timeStart or not instance.metadata.timeStart:
            # we don't allow these fields to be empty
            raise InvalidFormUpdateException("No timeStart or timeEnd found in instance %s!" %\
                                             (instance.get_id))
        
        if not instance.received_on:
            # we don't allow this field to be empty
            raise InvalidFormUpdateException("No received_on date found in instance %s!" %\
                                             (instance.get_id))
        
        
        self.instanceID = instance.get_id
        self.timeStart = instance.metadata.timeStart
        self.timeEnd = instance.metadata.timeEnd   
        self.deviceID = instance.metadata.deviceID or ""
        self.userID = instance.metadata.userID or ""
        self.xmlns = instance.xmlns or ""
        self.version = instance.version or ""
        self.uiversion = instance.uiversion or ""
        self.received_on = instance.received_on
        
    def matches_exact(self, instance):
        return  self.instanceID == instance.get_id and \
                self.timeStart == instance.metadata.timeStart and \
                self.timeEnd == instance.metadata.timeEnd and \
                self.deviceID == instance.metadata.deviceID and \
                self.userID == instance.metadata.userID and \
                self.xmlns == instance.xmlns and \
                self.version == instance.version and \
                self.uiversion == instance.version and \
                self.received_on == instance.received_on
        
    @classmethod
    def from_xforminstance(cls, instance):
        """
        Factory method for creating these objects from XFormInstance docs
        """
        ret = cls()
        ret.update(instance)
        return ret
    
    @classmethod
    def create_or_update_from_xforminstance(cls, instance):
        """
        Create or update an object in the database from an XFormInstance
        """
        try:
            val = cls.objects.get(instanceID=instance.get_id)
        except cls.DoesNotExist:
            val = cls()
        
        if not val.matches_exact(instance):
            val.update(instance)
            val.save()
        
        return val
    

class FormData(FormDataBase):
    """
    Data about a form submission.
    """
    
    pass