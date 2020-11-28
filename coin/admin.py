from django.contrib import admin

from .models import (
    Wallet, Referral, Invoice, InvoiceArchive, History, DownLine
)

admin.site.register(Invoice)
admin.site.register(Referral)
admin.site.register(DownLine)
admin.site.register(InvoiceArchive)
admin.site.register(Wallet)
admin.site.register(History)
