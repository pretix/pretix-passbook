all: localecompile
LNGS:=`find pretix_passbook/locale/ -mindepth 1 -maxdepth 1 -type d -printf "-l %f "`

localecompile:
	django-admin compilemessages

localegen:
	django-admin makemessages --keep-pot -i build -i dist -i "*egg*" $(LNGS)
	django-admin makemessages -d djangojs --keep-pot -i build -i dist -i "*egg*" $(LNGS)

