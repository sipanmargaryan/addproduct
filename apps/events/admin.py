from django.conf import settings
from django.contrib import admin
from django.utils import translation

import events.models


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Media:
        if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
            css = {
                'all': ('admin/location_picker.css',),
            }
            js = (
                'https://maps.googleapis.com/maps/api/js?key={}&language={}'.format(
                    settings.GOOGLE_API_KEY, translation.get_language()
                ),
                'admin/location_picker.js',
            )


admin.site.register(events.models.Category)
admin.site.register(events.models.Event, EventAdmin)
