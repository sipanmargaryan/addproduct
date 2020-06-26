from django.contrib import admin

import messaging.models

admin.site.register(messaging.models.Thread)
admin.site.register(messaging.models.Message)
