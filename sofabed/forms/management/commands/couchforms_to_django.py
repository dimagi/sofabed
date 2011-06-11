from django.core.management.base import LabelCommand
from dimagi.utils.couch.database import get_db
from couchdbkit.consumer import Consumer
import logging
import time
from dimagi.utils.couch.changes import Change
from couchforms.models import XFormInstance
from sofabed.forms.config import get_formdata_class

FILTER_FORMS_WITH_META = "forms/xforms_with_meta"

class Command(LabelCommand):
    help = "Listens for XFormInstance documents and create django models for them."
    args = ""
    label = ""
     
    def handle(self, *args, **options):
        db = get_db()
        c = Consumer(db)
        
        def update_from_form(line):
            try:
                change = Change(line)
                # don't bother with deleted or old documents
                if change.deleted or not change.is_current(db):
                    return 
                
                form = XFormInstance.get(change.id)
                get_formdata_class().create_or_update_from_xforminstance(form)
            except Exception, e:
                logging.exception("problem in form listener for line: %s\n%s" % (line, e))
        
        # Go into receive loop waiting for any conflicting patients to
        # come in.
        while True:
            try:
                c.wait(heartbeat=5000, filter=FILTER_FORMS_WITH_META, cb=update_from_form)
            except Exception, e:
                time.sleep(10)
                logging.exception("caught exception in form listener: %s, sleeping and restarting" % e)

    def __del__(self):
        pass
    
