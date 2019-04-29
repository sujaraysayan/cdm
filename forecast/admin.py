# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.
class user(admin.ModelAdmin):
	list_display = ('userid', 'firstname', 'lastlogin')

class FileUpload(admin.ModelAdmin):
	list_display = ('upload_by', 'file_name', 'customer')

class ForeCast(admin.ModelAdmin):
	list_display = ('user', 'product_id', 'last_version')

class ForecastDetail(admin.ModelAdmin):
	list_display = ('forecast','date', 'version', 'qty')

# class FileUploadSVI(admin.ModelAdmin):
# 	list_display = ('upload_by', 'file_name', 'customer')

class ForeCastSVI(admin.ModelAdmin):
	list_display = ('user','create_date','customer', 'last_update')

class ForecastDetailSVI(admin.ModelAdmin):
	list_display = ('forecast','date', 'product_id', 'qty')

class Customers(admin.ModelAdmin):
	list_display = ('customer_id', 'customer_name', 'customer_initial')

class TempUpload(admin.ModelAdmin):
	list_display = ('user', 'file_upload', 'is_done')

# class TempUploadSVI(admin.ModelAdmin):
# 	list_display = ('user', 'file_upload', 'is_done')

admin.site.register(User_Forecast, user)
admin.site.register(File_Upload, FileUpload)
admin.site.register(Forecast, ForeCast)
admin.site.register(Forecast_Detail, ForecastDetail)
# admin.site.register(File_Upload_Svi, FileUploadSVI)
admin.site.register(Forecast_svi, ForeCastSVI)
admin.site.register(Forecast_Detail_svi, ForecastDetailSVI)
admin.site.register(Customer, Customers)
admin.site.register(Upload_file_temp, TempUpload)
# admin.site.register(Upload_file_temp_svi, TempUploadSVI)