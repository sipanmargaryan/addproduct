from django.contrib import admin

import ads.models


class AdImageInline(admin.TabularInline):
    model = ads.models.AdImage


class AdAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'price', 'premium_until', 'user', 'is_seller_private', 'category', 'city')

    inlines = [
        AdImageInline
    ]


admin.site.register(ads.models.Category)
admin.site.register(ads.models.CarMakeCategory)
admin.site.register(ads.models.CarModelCategory)
admin.site.register(ads.models.MobileModelCategory)
admin.site.register(ads.models.MobileBrandCategory)
admin.site.register(ads.models.Ad, AdAdmin)
admin.site.register(ads.models.FavoriteAd)
