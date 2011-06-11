SofaBed lets you "pull out" data from couchforms for reporting (Get it??).

If you want to add properties to forms subclass FormDataBase and add

    FORMDATA_MODEL = 'myapp.Foo'  

to your settings.py file.

Just run ./manage.py couchforms_to_django to setup a feed to listen for changes
and save them in your django database.