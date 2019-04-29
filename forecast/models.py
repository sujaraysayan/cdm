# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from datetime import date

# Create your models here.
class Tblusers(models.Model):
	userid = models.CharField(db_column='UserID', primary_key=True, max_length=50)  # Field name made lowercase.
	password = models.CharField(db_column='Password', max_length=50, blank=True, null=True)  # Field name made lowercase.
	usergroup = models.CharField(db_column='UserGroup', max_length=1, blank=True, null=True)  # Field name made lowercase.
	plant = models.CharField(db_column='Plant', max_length=10, blank=True, null=True)  # Field name made lowercase.
	plantdetails = models.CharField(db_column='PlantDetails', max_length=100, blank=True, null=True)  # Field name made lowercase.
	employeeid = models.CharField(db_column='EmployeeID', max_length=50, blank=True, null=True)  # Field name made lowercase.
	prefixt = models.CharField(db_column='PrefixT', max_length=20, blank=True, null=True)  # Field name made lowercase.
	firstnamet = models.CharField(db_column='FirstNameT', max_length=20, blank=True, null=True)  # Field name made lowercase.
	lastnamet = models.CharField(db_column='LastNameT', max_length=30, blank=True, null=True)  # Field name made lowercase.
	prefixe = models.CharField(db_column='PrefixE', max_length=20, blank=True, null=True)  # Field name made lowercase.
	firstnamee = models.CharField(db_column='FirstNameE', max_length=20, blank=True, null=True)  # Field name made lowercase.
	lastnamee = models.CharField(db_column='LastNameE', max_length=30, blank=True, null=True)  # Field name made lowercase.
	hiredate = models.DateTimeField(db_column='HireDate', blank=True, null=True)  # Field name made lowercase.
	positions = models.CharField(db_column='Positions', max_length=50, blank=True, null=True)  # Field name made lowercase.
	userlevel = models.CharField(db_column='UserLevel', max_length=50, blank=True, null=True)  # Field name made lowercase.
	usergrade = models.CharField(db_column='UserGrade', max_length=50, blank=True, null=True)  # Field name made lowercase.
	worktype = models.CharField(db_column='WorkType', max_length=1, blank=True, null=True)  # Field name made lowercase.
	opstype = models.CharField(db_column='OPSType', max_length=2, blank=True, null=True)  # Field name made lowercase.
	department = models.CharField(db_column='Department', max_length=200, blank=True, null=True)  # Field name made lowercase.
	sex = models.CharField(db_column='Sex', max_length=1, blank=True, null=True)  # Field name made lowercase.
	maritalstatus = models.CharField(db_column='MaritalStatus', max_length=1, blank=True, null=True)  # Field name made lowercase.
	probativedate = models.DateTimeField(db_column='ProbativeDate', blank=True, null=True)  # Field name made lowercase.
	vacationdate = models.DateTimeField(db_column='VacationDate', blank=True, null=True)  # Field name made lowercase.
	vocation = models.FloatField(db_column='Vocation', blank=True, null=True)  # Field name made lowercase.
	vocationplus = models.FloatField(db_column='VocationPlus', blank=True, null=True)  # Field name made lowercase.
	vocationuse = models.FloatField(db_column='VocationUse', blank=True, null=True)  # Field name made lowercase.
	approver1 = models.CharField(db_column='Approver1', max_length=50, blank=True, null=True)  # Field name made lowercase.
	approver2 = models.CharField(db_column='Approver2', max_length=50, blank=True, null=True)  # Field name made lowercase.
	email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
	telphone = models.CharField(db_column='Telphone', max_length=50, blank=True, null=True)  # Field name made lowercase.
	loginflag = models.CharField(db_column='LoginFlag', max_length=1, blank=True, null=True)  # Field name made lowercase.
	logindate = models.DateTimeField(db_column='LoginDate', blank=True, null=True)  # Field name made lowercase.
	logoutdate = models.DateTimeField(db_column='LogoutDate', blank=True, null=True)  # Field name made lowercase.
	createuser = models.CharField(db_column='CreateUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
	createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
	lastedituser = models.CharField(db_column='LastEditUser', max_length=20, blank=True, null=True)  # Field name made lowercase.
	lasteditdate = models.DateTimeField(db_column='LastEditDate', blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'tblUsers'

class Customer(models.Model):
	customer_id = models.CharField(max_length=20, blank=True, null=True)  # Field name made lowercase.
	customer_name = models.CharField(max_length=125, blank=True, null=True)  # Field name made lowercase.
	customer_initial = models.CharField(max_length=10, blank=True, null=True)
	customer_type_file = models.CharField(max_length=100, blank=True, null=True)
	customer_wk_upload = models.CharField(max_length=200, blank=True,default="")
	def __str__(self):
		return '%s' % (self.customer_initial)   	

class User_Forecast(models.Model):
	userid = models.CharField(max_length=10, blank=True , null=True)
	firstname = models.CharField(max_length=20, blank=True, null=True)  # Field name made lowercase.
	lastname = models.CharField(max_length=30, blank=True, null=True)  # Field name made lowercase.
	customer_list = models.CharField(max_length=1024, blank=True, null=True,default="")
	lastlogin = models.CharField(max_length=25, blank=True, null=True)

	def __str__(self):
		return '%s' % (self.userid)   

class File_Upload(models.Model):
	upload_by = models.ForeignKey(User_Forecast,related_name='User_Forecast_File', max_length=10, blank=True,null=True) 
	customer = models.ForeignKey(Customer,related_name='Customer_upload', max_length=10, blank=True,null=True) 
	file_name = models.CharField(max_length=255, blank=True, null=True)  # Field name made lowercase.
	file_path = models.FileField(blank=True,null=True)  # Field name made lowercase.
	upload_date = models.CharField(max_length=25, blank=True, null=True)
	upload_week = models.CharField(max_length=5, blank=True, null=True)

	def __str__(self):
		return '%s' % (self.upload_by)   

class Forecast(models.Model):
	user = models.ForeignKey(User_Forecast,related_name='User_Forecast_Forecast', max_length=10, blank=True,null=True) 
	customer = models.ForeignKey(Customer,related_name='Customer_forcast', max_length=10, blank=True,null=True) 
	product_id = models.CharField(max_length=20, blank=True, null=True)  # Field name made lowercase.
	description = models.CharField(max_length=1024, blank=True, null=True)  # Field name made lowercase.
	first_demand_date = models.CharField(max_length=25, blank=True, null=True)
	last_version = models.CharField(max_length=25, blank=True, null=True)

	def __str__(self):
		return '%s' % (self.product_id)   

class Forecast_Detail(models.Model):
	forecast = models.ForeignKey(Forecast,related_name='Forecast_detail', max_length=10, blank=True,null=True) 
	file_upload = models.ForeignKey(File_Upload,related_name='File_Upload_forecast', max_length=10, blank=True,null=True) 
	# date = models.CharField(max_length=20, blank=True, null=True)  # Field name made lowercase.
	date = models.DateField(default=date.today)
	version = models.CharField(max_length=25, blank=True, null=True)  # Field name made lowercase.
	qty = models.IntegerField(blank=True, null=True)
	status = models.CharField(max_length=20, blank=True, null=True)
	work_week = models.CharField(max_length=20, blank=True, null=True)
	year = models.CharField(max_length=4, blank=True, null=True)
	def __str__(self):
		return '%s' % (self.date)   	

class Upload_file_temp(models.Model):
	user = models.ForeignKey(User_Forecast,related_name='User_Forecast_temp', max_length=10, blank=True,null=True) 
	file_upload = models.ForeignKey(File_Upload,related_name='File_Upload_temp', max_length=10, blank=True,null=True) 
	remark = models.CharField(max_length=1024, blank=True,default='')
	is_done = models.BooleanField(default=False)

	def __str__(self):
		return '%s' % (self.user)   	

# class File_Upload_Svi(models.Model):
# 	upload_by = models.ForeignKey(User_Forecast,related_name='User_Forecast_File_svi', max_length=10, blank=True,null=True) 
# 	customer = models.ForeignKey(Customer,related_name='Customer_upload_svi', max_length=10, blank=True,null=True) 
# 	file_name = models.CharField(max_length=255, blank=True, null=True)  # Field name made lowercase.
# 	file_path = models.FileField(blank=True,null=True)  # Field name made lowercase.
# 	upload_date = models.CharField(max_length=25, blank=True, null=True)
# 	upload_week = models.CharField(max_length=5, blank=True, null=True)

# 	def __str__(self):
# 		return '%s' % (self.upload_by)   

class Forecast_svi(models.Model):
	user = models.ForeignKey(User_Forecast,related_name='User_Forecast_Forecast_svi', max_length=10, blank=True,null=True) 
	customer = models.ForeignKey(Customer,related_name='Customer_forcast_svi', max_length=10, blank=True,null=True) 
	file_upload = models.ForeignKey(File_Upload,related_name='File_Upload_forecast_svi', max_length=10, blank=True,null=True) 
	# customer_version = models.ForeignKey(File_Upload,related_name='file_upload', max_length=10, blank=True,null=True) 
	last_update = models.CharField(max_length=25, blank=True, null=True)
	create_date = models.CharField(max_length=25, blank=True, null=True)
	status = models.CharField(max_length=10, blank=True, null=True,default='Private')
	def __str__(self):
		return '%s' % (self.create_date)   

class Forecast_Detail_svi(models.Model):
	forecast = models.ForeignKey(Forecast_svi,related_name='Forecast_detail_svi', max_length=10, blank=True,null=True) 
	product_id = models.CharField(max_length=20, blank=True, null=True)  # Field name made lowercase.
	date = models.CharField(max_length=25, blank=True, null=True)
	old_date = models.CharField(max_length=25, blank=True, null=True)
	qty = models.IntegerField(blank=True, null=True)
	old_qty = models.IntegerField(blank=True, null=True)
	def __str__(self):
		return '%s' % (self.product_id)   	

# class Upload_file_temp_svi(models.Model):
# 	user = models.ForeignKey(User_Forecast,related_name='User_Forecast_temp_svi', max_length=10, blank=True,null=True) 
# 	file_upload = models.ForeignKey(File_Upload_Svi,related_name='File_Upload_temp_svi', max_length=10, blank=True,null=True) 
# 	is_done = models.BooleanField(default=False)

# 	def __str__(self):
# 		return '%s' % (self.user) 

class Last_upload(models.Model):
	work_week = models.CharField(max_length=25, blank=True, null=True)  # Field name made lowercase.
	
	def __str__(self):
		return '%s' % (self.work_week)   	


