from django.contrib import admin
from car import models
from .models import BookingModel

# Register your models here.
admin.site.register(models.CarModel)
admin.site.register(models.BrandModel)
admin.site.register(models.Location)
@admin.register(BookingModel)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("car", "user", "location", "pickup_datetime", "status")
    list_filter = ("status",)
    list_editable = ("status",)
