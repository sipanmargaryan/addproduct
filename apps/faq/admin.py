from django.contrib import admin

import faq.models

admin.site.register(faq.models.Question)
admin.site.register(faq.models.Answer)
admin.site.register(faq.models.Category)
