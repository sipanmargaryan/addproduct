from django.contrib import admin

import payments.models


class PaymentAdmin(admin.ModelAdmin):
    exclude = ('knet_charge_id', )


admin.site.register(payments.models.Payment, PaymentAdmin)
