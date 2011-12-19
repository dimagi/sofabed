from django.core.management.base import LabelCommand
from dimagi.utils.couch.database import get_db
from couchdbkit.consumer import Consumer
import logging
import time
from dimagi.utils.couch.changes import Change
from couchforms.models import XFormInstance
from sofabed.forms.config import get_formdata_class
from django.db import transaction
from sofabed.forms.models import Checkpoint
from django.db.utils import DatabaseError
from sofabed.forms.exceptions import InvalidDataException

FILTER_FORMS_WITH_META = "forms/xforms_with_meta"
CHECKPOINT_FREQUENCY = 100
CHECKPOINT_ID = "sofabed_checkpoint"
sofabed_counter = 0

class Command(LabelCommand):
    help = "Listens for XFormInstance documents and create django models for them."
    args = ""
    label = ""
     
    def handle(self, *args, **options):
        db = get_db()
        c = Consumer(db)
        
        @transaction.commit_on_success
        def update_from_form(line):
            try:
                change = Change(line)
                # don't bother with deleted or old documents
                if change.deleted or not change.is_current(db):
                    return 
                
                form = XFormInstance.get(change.id)
                get_formdata_class().create_or_update_from_xforminstance(form)
                
                # update the checkpoint, somewhat arbitrarily
                global sofabed_counter
                sofabed_counter = sofabed_counter + 1
                if sofabed_counter % CHECKPOINT_FREQUENCY == 0:
                    Checkpoint.set_checkpoint(CHECKPOINT_ID, change.seq)
            
            except InvalidDataException, e:
                # this is a less severe class of errors
                logging.info("bad update in form listener for line: %s\n%s" % (line, e))
            
            except Exception, e:
                logging.exception("problem in form listener for line: %s\n%s" % (line, e))
                if isinstance(e, DatabaseError):
                    # we have to do this manually to avoid issues with 
                    # open transactions
                    transaction.rollback()
                
        # Go into receive loop waiting for any conflicting patients to
        # come in.
        last_checkpoint = Checkpoint.get_last_checkpoint(CHECKPOINT_ID)
        
        while True:
            try:
                c.wait(heartbeat=5000, filter=FILTER_FORMS_WITH_META, 
                       since=last_checkpoint, cb=update_from_form)
                       
            except Exception, e:
                time.sleep(10)
                logging.exception("caught exception in form listener: %s, sleeping and restarting" % e)

    def __del__(self):
        pass
    
