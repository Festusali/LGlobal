from django.urls import path
from django.views.generic.base import TemplateView

from coin import views

app_name = 'coin'

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), 
        name='privacy'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), 
        name='faq'),
    path('tos/', TemplateView.as_view(template_name='tos.html'), name='tos'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/u/<int:pk>/level/', views.LevelView.as_view(), name='level'),
    path('users/u/level_upgrade/', views.upgrade_level, name='upgrade_level'), 
    path('referrals/', views.ReferralList.as_view(), name='referrals'),

    path('invoices/', views.InvoiceList.as_view(), name='invoices'),
    path('invoices/invoiced/', views.InvoicedToList.as_view(), 
        name='invoiced'),
    path('invoices/issued/', views.IssuedInvoiceList.as_view(), name='issued'),
    path('invoice/<int:pk>/', views.InvoiceDetail.as_view(), 
        name='invoice-detail'),
    path('invoice/<int:pk>/pay/', views.PayInvoice.as_view(), 
        name='pay-invoice'),
    path('invoice/<int:pk>/confirm_pay/', views.ConfirmInvoicePaid.as_view(), 
        name='confirm-invoice-paid'),

    path('receipts/', views.ReceiptList.as_view(), name='receipts'),
    path('receipt/<int:pk>/', views.ReceiptDetail.as_view(), 
        name='receipt-detail'),
]