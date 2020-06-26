from django.contrib import admin

import common.models

admin.site.register(common.models.Article)
admin.site.register(common.models.Category)
admin.site.register(common.models.Service)
