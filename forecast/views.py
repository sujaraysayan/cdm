# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, \
                        HttpResponseRedirect
from .models import *
from django.core.files.storage import FileSystemStorage
import arrow
from django.contrib import messages
from django.core.files import File
import csv
from io import StringIO
import os
import threading
import json
from collections import OrderedDict
from operator import itemgetter
import hashlib
import pandas as pd
from pandas import ExcelFile
import datetime
from django.core.mail import EmailMessage
#SAP 
from pyrfc import Connection

# Create your views here.
def home(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	user_forecast = User_Forecast.objects.get(userid=username)
	if user_forecast.customer_list.split(',')[0] == "" :
		return HttpResponseRedirect('/upload/') 
	else:
		cus = []
		param = home_month(request,user_forecast.customer_list.split(',')[0],6,"Month")
		_customer = user_forecast.customer_list.split(",")
		if len(_customer) > 0 :
			for i in _customer : 
				if i != "":
					customer = Customer.objects.get(customer_id=i)
					cus.append(customer)

		param["customer"] = cus
		param["current_customer"] = user_forecast.customer_list.split(',')[0]
		param['period'] = 6

		try:
			upload_status = request.session['upload']
		except Exception as e:
			upload_status = "False"
		# print upload_status
		param['upload_status'] = upload_status




	return render(request, 'home.html',param) 

def homeFilter(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	customer = request.POST.get("customer","")
	period = request.POST.get("period","")
	unit = request.POST.get("unit","")
	print period
	if unit == "Week":
		param = home_week(request,customer,period,unit)

 	if unit == "Month":
		param = home_month(request,customer,period,unit)

	if unit == "Year":
		param = home_year(request,customer,period,unit)

	if unit == "Quarter":
		param = home_quarter(request,customer,period,unit)
	
	cus = []
	user_forecast = User_Forecast.objects.get(userid=username)
	_customer = user_forecast.customer_list.split(",")
	if len(_customer) > 0 :
		for i in _customer : 
			if i != "":
				customer_list = Customer.objects.get(customer_id=i)
				cus.append(customer_list)
					
	param["customer"] = cus
	param['current_customer'] = customer
	param['period'] = period
	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"
	param['upload_status'] = upload_status

	return render(request, 'home.html',param) 

def upload(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login') 

	user_forecast = User_Forecast.objects.get(userid=username)
	upload_file = File_Upload.objects.filter(upload_by=user_forecast).order_by('-id')[:5]
	for i in upload_file:
		if len(i.file_name) > 60 :
			i.full_name = i.file_name
			i.file_name = i.file_name[0:60]+"..."
		i.upload_date = arrow.get(i.upload_date,"YYYY-MM-DD").format("DD.MM.YYYY")
	
	cus = []
	customer_list = {}
	_customer = user_forecast.customer_list.split(",")
	if len(_customer) > 0 :
		for i in _customer : 
			if i != "":
				customer = Customer.objects.get(customer_id=i)
				cus.append(customer)
				customer_list[customer.customer_id] = {
					"file_type" : customer.customer_type_file
				}

	file_type = json.dumps(customer_list)
	try:
		current_customer = request.session['last_customer']
		del request.session['last_customer']
	except Exception as e:
		current_customer = ""
	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"

	param = {'user':userlogin,'recent_file':upload_file,"customer":cus,
						'upload_status':upload_status,'file_type': file_type ,'current_customer':current_customer} 
	return render(request, 'upload.html',param) 

def upload_file(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	cus = request.POST.get("customer","")
	customer = Customer.objects.get(customer_id=cus) 	
	user_forecast = User_Forecast.objects.get(userid=username)
	uploaded_file_url = ""
	try:
		if request.FILES['file_upload']:
			myfile = request.FILES['file_upload']
			namefile = request.FILES['file_upload'].name
			file_type = namefile.split('.')[1]

			# if file_type != 'csv' and cus == '1100017':
			# 	messages.error(request, "Error")
			# 	return HttpResponseRedirect('/upload/') 
			

			file = File_Upload.objects.create(upload_by=user_forecast)
			fs = FileSystemStorage()
			filename = fs.save(myfile.name.decode('utf-8'), myfile)
			uploaded_file_url = fs.url(filename)
			file.file_path = uploaded_file_url
			file.file_name = myfile
			file.upload_date = arrow.now().format('YYYY-MM-DD HH:mm:ss')
			# file.upload_date = "2019-01-01 01:00:00"
			wk = arrow.now().isocalendar()[1]
			file.upload_week = str("WK"+str(wk))
			# file.upload_week = str("WK16")
			file.customer = customer
			file.save()

			temp = Upload_file_temp.objects.create(file_upload=file,user=user_forecast)
			temp.is_done = False
			temp.save()

			if cus == '1100017':
				t = threading.Thread(target=readFileAXC,args=[request,username,file.id])
				t.setDaemon(True)
				t.start()

			if cus == '1200301':
				t = threading.Thread(target=readFileLGP,args=[request,username,file.id])
				t.setDaemon(True)
				t.start()

			if cus == '1100189':
				t = threading.Thread(target=readFileMTN,args=[request,username,file.id])
				t.setDaemon(True)
				t.start()

			if cus == '1200854' or cus == '1300193' or cus == '1100206' or cus == '1300205':
				t = threading.Thread(target=readFileLNK,args=[request,username,file.id])
				t.setDaemon(True)
				t.start()


			if str(customer.customer_wk_upload) != "": 
				list_customer_wk = customer.customer_wk_upload.split(',')
				str_list = customer.customer_wk_upload
				if len(list_customer_wk) >= 24:
					list_customer_wk.pop(0)
					str_list = ""
					count = 0
					for l in 	list_customer_wk:
						if count == len(list_customer_wk) - 1:
							str_list += l  
						else:
							str_list += l + "," 
						count += 1

				new_str = arrow.now().format("YYYY")+"."+str("WK"+str(wk))
				if new_str not in  str_list:
					customer.customer_wk_upload = str_list+","+new_str
				# customer.customer_wk_upload = str_list+","+"2019.WK16"
			else:
				customer.customer_wk_upload = arrow.now().format("YYYY")+"."+str("WK"+str(wk))
				# customer.customer_wk_upload = "2018.WK22"
			customer.save()
			# save_DB = saveDB(username,file.id)
			# print save_DB
			# if save_DB:
			request.session['upload'] = "True"
			request.session['last_customer'] = cus
			messages.success(request, 'Complete')
			# else:
			# 	raise ValueError('test')
	except Exception as e:
		messages.error(request, "Error")
		file.delete()
		if uploaded_file_url != "":
			os.remove("."+uploaded_file_url.replace("%20", " "))
	# except ValueError	 as v:
	# 	messages.error(request, "Error")
	# 	file.delete()
	# 	os.remove("."+uploaded_file_url.replace("%20", " "))

	return HttpResponseRedirect('/upload/') 

def upload_svi(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login') 

	user_forecast = User_Forecast.objects.get(userid=username)
	upload_file = File_Upload_Svi.objects.filter(upload_by=user_forecast).order_by('-id')[:5]
	for i in upload_file:
		if len(i.file_name) > 60 :
			i.full_name = i.file_name
			i.file_name = i.file_name[0:60]+"..."
		i.upload_date = arrow.get(i.upload_date,"YYYY-MM-DD").format("DD.MM.YYYY")
	
	cus = []
	customer_list = {}
	_customer = user_forecast.customer_list.split(",")
	if len(_customer) > 0 :
		for i in _customer : 
			if i != "":
				customer = Customer.objects.get(customer_id=i)
				cus.append(customer)
				customer_list[customer.customer_id] = {
					"file_type" : customer.customer_type_file
				}

	file_type = json.dumps(customer_list)
	try:
		current_customer = request.session['last_customer']
		del request.session['last_customer']
	except Exception as e:
		current_customer = user_forecast.customer_list.split(",")[0]

	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"

	version_list = []
	for i in cus:
		customer_version = File_Upload.objects.filter(customer=i).order_by('-id')[:5]
		for k in customer_version:
			version_list.append({
					'id':k.id,
					'name':k.file_name,
					'customer':i.customer_id
				})

	param = {'user':userlogin,'recent_file':upload_file,"customer":cus,
						'upload_status':upload_status,'file_type': file_type ,
						'current_customer':current_customer,'customer_version':version_list,
						'customer_ver_json':json.dumps(version_list)} 
	return render(request, 'upload_svi.html',param) 

def upload_file_svi(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	customer = request.POST.get('customer',"")
	customer_version = request.POST.get('customer_version',"")
	user_forecast = User_Forecast.objects.get(userid=username)
	customer = Customer.objects.get(customer_id=customer) 	
	if request.FILES['file_upload']:
		myfile = request.FILES['file_upload']
		namefile = request.FILES['file_upload'].name
		file_type = namefile.split('.')[1]

		file = File_Upload_Svi.objects.create(upload_by=user_forecast)
		fs = FileSystemStorage()
		filename = fs.save(myfile.name.decode('utf-8'), myfile)
		uploaded_file_url = fs.url(filename)
		file.file_path = uploaded_file_url
		file.file_name = myfile
		file.upload_date = arrow.now().format('YYYY-MM-DD HH:mm:ss')
		# file.upload_date = "2019-01-01 01:00:00"
		wk = arrow.now().isocalendar()[1]
		file.upload_week = str("WK"+str(wk))
		# file.upload_week = str("WK1")
		file.customer = customer
		file.save()

		temp = Upload_file_temp_svi.objects.create(file_upload=file,user=user_forecast)
		temp.is_done = False
		temp.save()

		# t = threading.Thread(target=readSVIFile,args=[request,username,file.id,customer_version])
		# t.setDaemon(True)
		# t.start()

		user = User_Forecast.objects.get(userid=username)
		file = File_Upload_Svi.objects.get(id=file.id)
		path = "."+str(file.file_path).replace("%20", " ")
		print path
		with open(path) as content:
			line = content.readlines()
			for l in line:
				print l 

		temp = Upload_file_temp_svi.objects.get(file_upload=file)
		temp.is_done = True
		temp.save()

		request.session['upload'] = "True"

		messages.success(request, 'Complete')

	return HttpResponseRedirect('/upload-svi/') 

def report(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login') 
	# c = Customer.objects.get(customer_initial='MTN')
	# f = Forecast.objects.filter(customer=c)
	# for i in f:
	# 	fd = Forecast_Detail.objects.filter(forecast=i)
	# 	for j in fd :
	# 		print j.date , j.work_week


	param = {}
	# current_year = "2018"
	user_forecast = User_Forecast.objects.get(userid=username)
	if user_forecast.customer_list.split(',')[0] == "" :
		return HttpResponseRedirect('/upload/') 

	current_year = arrow.now().format("YYYY")
	param = home_quarter(request,user_forecast.customer_list.split(',')[0],"2","quarter")
	quarter = ["/Q1","/Q2","/Q3","/Q4"]
	new_list = []
	data = []
	_temp = []
	for q in quarter:
		for i in param['forecast']:
			if current_year+q in i['date']:
				new_list.append(i)

		high = sorted(new_list, key=itemgetter('diff_qty'))[:5]
		high = sorted(high, key=itemgetter('diff_qty'),reverse=True)
		low = sorted(new_list, key=itemgetter('diff_qty'),reverse=True)[:5]


		_tempQTY = []
		_tempname = []
		for i in low:
			_tempQTY.append(i['diff_qty'])
			_tempname.append(str(i['product_id']))

		for i in high:
			_tempQTY.append(i['diff_qty'])
			_tempname.append(str(i['product_id']))

		data.append({
			"name" : _tempname,
			"qty" : _tempQTY,
			"period" : q.replace("/" , '_'),
			"year" : current_year+q,
		})
		
		new_list = []
		

	user_forecast = User_Forecast.objects.get(userid=username)
	cus = []
	if user_forecast.customer_list.split(',')[0] == "" :
		return HttpResponseRedirect('/upload/') 
	else:
		_customer = user_forecast.customer_list.split(",")
		if len(_customer) > 0 :
			for i in _customer : 
				if i != "":
					customer = Customer.objects.get(customer_id=i)
					cus.append(customer)

	param["customer"] = cus
	param["current_customer"] = user_forecast.customer_list.split(',')[0]
	param["data"] = data
	param['year'] = current_year

	return render(request, 'report.html',param) 

def approve1(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login') 
	param = {}
	user_forecast = User_Forecast.objects.get(userid=username)
	
	cus = []
	_customer = user_forecast.customer_list.split(",")
	if len(_customer) > 0 :
		for i in _customer : 
			if i != "":
				customer = Customer.objects.get(customer_id=i)
				cus.append(customer)

	year = []
	cur_customer = Customer.objects.get(customer_id=user_forecast.customer_list.split(',')[0])
	forecast = Forecast.objects.filter(customer=cur_customer)
	for f in forecast:
		f_year = arrow.get(f.last_version,'YYYY-MM-DD').format('YYYY')
		if f_year not in year:
			year.append(f_year) 
			
	param['forecast'] = forecast 
	param["customer"] = cus
	param["year"] = year
	param["current_year"] =  arrow.now().format('YYYY')
	param["current_customer"] = user_forecast.customer_list.split(',')[0]

	return render(request, 'approve.html',param) 

def approve(request):
	param ={}
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/')

	svi_version_list = []
	
	forecast_svi = Forecast_svi.objects.filter(Q(status='Publish'))
	
	for fsvi in forecast_svi:
		if len(fsvi.file_upload.file_name) > 22:
			filename = fsvi.file_upload.file_name[:23]+"..."
		else:
			filename = fsvi.file_upload.file_name

		svi_version_list.append({
			'customer_name': fsvi.customer.customer_name,
			'file_name' : filename, 
			'file_full_name' : fsvi.file_upload.file_name, 
			'file_path' : fsvi.file_upload.file_path, 
			'version' : arrow.get(fsvi.create_date,'YYYY/MM/DD HH:mm:ss').format("YYYYMMDDHHmm"), 
			'last_update' : arrow.get(fsvi.last_update,'YYYY/MM/DD HH:mm:ss').format("DD.MM.YYYY HH:mm"), 
			'id':fsvi.id,
			'owner':fsvi.user.firstname,
			'status' : fsvi.status
		})
	param = {'forecast_svi' : svi_version_list,'user':user_forecast}

	return render(request, 'approve.html',param) 

def reportFilter(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login') 


	customer = request.POST.get("customer","")
	year = request.POST.get("year","")
	unit = request.POST.get("unit","")

	current_year = year
	param = home_quarter(request,customer,"2","quarter")
	quarter = ["/Q1","/Q2","/Q3","/Q4"]
	new_list = []
	data = []
	_temp = []
	for q in quarter:
		for i in param['forecast']:
			if current_year+q in i['date']:
				new_list.append(i)

		high = sorted(new_list, key=itemgetter('diff_qty'))[:5]
		high = sorted(high, key=itemgetter('diff_qty'),reverse=True)
		low = sorted(new_list, key=itemgetter('diff_qty'),reverse=True)[:5]

		_tempQTY = []
		_tempname = []
		for i in low:
			_tempQTY.append(i['diff_qty'])
			_tempname.append(str(i['product_id']))

		for i in high:
			_tempQTY.append(i['diff_qty'])
			_tempname.append(str(i['product_id']))

		data.append({
			"name" : _tempname,
			"qty" : _tempQTY,
			"period" : q.replace("/" , '_'),
			"year" : current_year+q,
		})
		
		new_list = []

	user_forecast = User_Forecast.objects.get(userid=username)
	cus = []
	if user_forecast.customer_list.split(',')[0] == "" :
		return HttpResponseRedirect('/upload/') 
	else:
		_customer = user_forecast.customer_list.split(",")
		if len(_customer) > 0 :
			for i in _customer : 
				if i != "":
					customer_ = Customer.objects.get(customer_id=i)
					cus.append(customer_)

	param["customer"] = cus
	param['current_customer'] = customer
	param["data"] = data
	param['year'] = current_year

	return render(request, 'report.html',param) 
	
def login(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		return HttpResponseRedirect('/home/') 
	except Exception as e:
		userlogin = 'notlogin'

	param = {'user':userlogin} 
	return render(request, 'login.html',param) 

def logout(request):
	try:
		del request.session['username']
	except Exception as e:
		print e
	return HttpResponseRedirect('/') 

def check_login(request):
	username = request.POST.get('username',"")
	password = request.POST.get('password',"")
	try:
		user = Tblusers.objects.using("user").filter(userid=username)
		if user.count() > 0 :
			pwd_encrypt = hashlib.md5( password ).hexdigest()
			if user[0].password == pwd_encrypt:
				user_forecast = User_Forecast.objects.filter(userid=username)
				if user_forecast.count() > 0 :
					user_forecast = User_Forecast.objects.get(userid=username)
					user_forecast.lastlogin = arrow.now().format('YYYY-MM-DD HH:mm:ss')
					user_forecast.save()
				else:
					user_forecast = User_Forecast.objects.create(userid=username)
					user_forecast.firstname = user[0].firstnamee
					user_forecast.lastname = user[0].lastnamee
					user_forecast.lastlogin = arrow.now().format('YYYY-MM-DD HH:mm:ss')
					user_forecast.save()
				
				request.session['username'] = username 
				return HttpResponseRedirect('/home/') 
			else:
				error = "Your password is invalid !"
				messages.error(request, error)
				return HttpResponseRedirect('/login/') 
		else:
			error = "Your username is invalid !"
			messages.error(request, error)
			return HttpResponseRedirect('/login/') 
	except Exception as e:
		error = "Your account is invalid !"
		messages.error(request, error)
		return HttpResponseRedirect('/login/')
	
def checkUpload(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	user_forecast = User_Forecast.objects.get(userid=username)
	task = Upload_file_temp.objects.filter(user=user_forecast)
	count = 0
	if task.count() > 0:
		t = "True"
		for i in task:
			if i.is_done == False:
				t = "False"
				count += 1
			else:
				if i.remark != '':
					t = i.remark
					# print t
					temp = Upload_file_temp.objects.get(id=i.id)
					File_Upload.objects.get(id=temp.file_upload.id).delete()
				else:
					Upload_file_temp.objects.get(id=i.id).delete()
		if t == "True":
			del request.session['upload']
	else:
		t = "True"
		del request.session['upload']

	return HttpResponse(json.dumps({'is_done':t,'count':count}), content_type="application/json")

def home_week(request,customer,period,unit):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	customer = Customer.objects.get(customer_id=customer)
	# wk = arrow.now().isocalendar()[1]
	# # wk = 4
	# list_week = []
	# forecast = File_Upload.objects.filter(customer=customer,upload_week="WK"+str(wk))
	# if forecast.count() > 0:
	# 	list_week.append(str("WK"+str(wk)))
	# else:
	# 	period = int(period) + 1

	# for i in range(int(period)-1):
	# 	wk -= 1
	# 	if wk == 0 :
	# 		wk = 52
	# 	list_week.append(str("WK"+str(wk)))

	list_week = []
	list_year = []
	yk = customer.customer_wk_upload.split(",")
	yk = list(reversed(yk))
	wk = ""
	for i in yk :
		if i != "":
			list_week.append(str(i.split(".")[1]))
			list_year.append(str(i.split(".")[0]))
			wk = int(i.split(".")[1][2:])

	if wk == "":
		wk = arrow.now().isocalendar()[1]
	if len(list_week) < int(period):
		period = int(period) - len(list_week)
		for i in range(int(period)):
			wk -= 1
			if wk == 0 :
				wk = 52
			list_week.append(str("WK"+str(wk)))
	else:
		list_week = list_week[:int(period)]

	list_week = list(reversed(list_week))

	original_lk = []
	for i in list_week :
		original_lk.append(0)

	forecast_list = []
	forecast = Forecast.objects.filter(customer=customer)
	if forecast.count() > 0:
		for f in forecast :
			lk = []
			for i in list_week :
				lk.append(0)

			old_date = ""
			forecast_detail = Forecast_Detail.objects.filter(forecast=f,status='available').order_by("date","id")
			if forecast_detail.count() > 0:
				count_loop = 0
				for fd in forecast_detail:
					if old_date == str(fd.date) :
						if fd.work_week in list_week:
 							lk[list_week.index(fd.work_week)] = fd.qty

 						if forecast_detail.count()-1 == count_loop :
							if lk != original_lk:
	 							diff_qty = lk[-1] - lk[-2]
								if lk[-2] == 0:
									diff_percent = 0
								else:
									diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"

	 							forecast_list_detail = {
									"product_id" : f.product_id,
									# "fulldescription" : f.description,
									# "description" : f.description[:25],
									"date" : arrow.get(old_date,"YYYY-MM-DD").format("DD/MM/YYYY"),
									"work_week" : lk ,
									"diff_qty": diff_qty,
									"diff_percent": diff_percent	
								}
								forecast_list.append(forecast_list_detail)

					else:
						if old_date == "":
							if fd.work_week in list_week:
								lk[list_week.index(fd.work_week)] = fd.qty
								old_date = str(fd.date)

						elif old_date != str(fd.date):
							if lk != original_lk:
								diff_qty = lk[-1] - lk[-2]
								if lk[-2] == 0:
									diff_percent = 0
								else:
									diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"

								forecast_list_detail = {
									"product_id" : f.product_id,
									"fulldescription" : f.description,
									# "description" : f.description[:25],
									"date" : arrow.get(old_date,"YYYY-MM-DD").format("DD/MM/YYYY"),
									"work_week" : lk,
									"diff_qty": diff_qty,
									"diff_percent": diff_percent
								}

								forecast_list.append(forecast_list_detail)

							lk = []
							for i in list_week :
								lk.append(0)
							if fd.work_week in list_week:
								lk[list_week.index(fd.work_week)] = fd.qty
								old_date = str(fd.date)

							if forecast_detail.count()-1 == count_loop :
								if lk != original_lk:
		 							diff_qty = lk[-1] - lk[-2]
									if lk[-2] == 0:
										diff_percent = 0
									else:
										diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"

		 							forecast_list_detail = {
										"product_id" : f.product_id,
										"fulldescription" : f.description,
										# "description" : f.description[:25],
										"date" : arrow.get(old_date,"YYYY-MM-DD").format("DD/MM/YYYY"),
										"work_week" : lk ,
										"diff_qty": diff_qty,
										"diff_percent": diff_percent	
									}
									forecast_list.append(forecast_list_detail)
					count_loop += 1

	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"


	param = {'user':userlogin,'upload_status':upload_status,
						'forecast':forecast_list,'work_week' : list_week,
						'unit':unit,'period':period} 

	return param

def home_month(request,customer,period,unit):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	customer = Customer.objects.get(customer_id=customer)
	list_week = []
	list_year = []
	yk = customer.customer_wk_upload.split(",")
	yk_re = list(reversed(yk))
	wk = ""
	yyear = ""
	for i in yk_re :
		if i != "":
			list_week.append(str(i.split(".")[1]))
			list_year.append(i)
			wk = int(i.split(".")[1][2:])
			yyear = int(i.split(".")[0])

	if wk == "":
		wk = arrow.now().isocalendar()[1]
	if len(list_week) < int(period):
		period = int(period) - len(list_week)

		for i in range(int(period)):
			wk -= 1
			if wk == 0 :
				wk = 52
				yyear -= 1

			list_week.append(str("WK"+str(wk)))
			list_year.append(str(yyear) +"."+str("WK"+str(wk)))
	else:
		list_week = list_week[:int(period)]
		list_year = list_year[:int(period)]


	list_week = list(reversed(list_week))
	list_year = list(reversed(list_year))
	forecast_list = []
	forecast = Forecast.objects.filter(customer=customer)
	if forecast.count() > 0:
		for f in forecast :
			lk = []
			for i in list_week :
				lk.append(0)

			old_month = ""
			old_version = ""
			old_date = ""
			old_work_week = ""
			forecast_detail = Forecast_Detail.objects.filter(forecast=f,status='available').order_by("date",'-id')
			if forecast_detail.count() > 0:
				count_loop = 0
				for fd in  forecast_detail:
					new_version = fd.version
					new_date = str(fd.date)
					new_work_week = str(fd.work_week)
					new_month = arrow.get(str(fd.date),"YYYY-MM-DD").format("MM/YYYY")
					if old_month == new_month:
						if fd.year+"."+fd.work_week in list_year:
							if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
 								pass
 							else:
 								lk[list_week.index(fd.work_week)] += fd.qty
 								old_version = new_version
								old_date = new_date
								old_work_week = new_work_week 

 						if forecast_detail.count()-1 == count_loop :
 							diff_qty = lk[-1] - lk[-2]
							if lk[-2] == 0:
								diff_percent = 0
							else:
								diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"
 							forecast_list_detail = {
								"product_id" : f.product_id,
								# "fulldescription" : f.description,
								# "description" : f.description[:25],
								"date" : "01/"+str(old_month),
								"work_week" : lk ,
								"diff_qty": diff_qty,
								"diff_percent": diff_percent	
							}
							forecast_list.append(forecast_list_detail)

					else:
						if old_month == "":
							if fd.year+"."+fd.work_week in list_year:
								if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
	 								pass
	 							else:
									lk[list_week.index(fd.work_week)] += fd.qty
									old_month = new_month
									old_version = new_version
									old_date = new_date
									old_work_week = new_work_week 


						elif old_month != new_month:
							diff_qty = lk[-1] - lk[-2]
							if lk[-2] == 0:
								diff_percent = 0
							else:
								diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"

							forecast_list_detail = {
								"product_id" : f.product_id,
								# "fulldescription" : f.description,
								# "description" : f.description[:25],
								"date" : "01/"+str(old_month),
								"work_week" : lk,
								"diff_qty": diff_qty,
								"diff_percent": diff_percent
							}

							forecast_list.append(forecast_list_detail)

							lk = []
							for i in list_week :
								lk.append(0)
							if fd.year+"."+fd.work_week in list_year:
								if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
	 								pass
	 							else:
									lk[list_week.index(fd.work_week)] += fd.qty
									old_month = new_month
									old_version = new_version
									old_date = new_date
									old_work_week = new_work_week 


							if forecast_detail.count()-1 == count_loop :
	 							diff_qty = lk[-1] - lk[-2]
								if lk[-2] == 0:
									diff_percent = 0
								else:
									diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"
	 							forecast_list_detail = {
									"product_id" : f.product_id,
									# "fulldescription" : f.description,
									# "description" : f.description[:25],
									"date" : "01/"+str(old_month),
									"work_week" : lk ,
									"diff_qty": diff_qty,
									"diff_percent": diff_percent	
								}
								forecast_list.append(forecast_list_detail)

					count_loop += 1

	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"

	param = {'user':userlogin,'upload_status':upload_status,
						'forecast':forecast_list,'work_week' : list_week,
						'unit':unit,'period':period} 

	return param

def home_year(request,customer,period,unit):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	customer = Customer.objects.get(customer_id=customer)
	# wk = arrow.now().isocalendar()[1]
	# # wk = 4
	# list_week = []
	# forecast = File_Upload.objects.filter(customer=customer,upload_week="WK"+str(wk))
	# if forecast.count() > 0:
	# 	list_week.append(str("WK"+str(wk)))
	# else:
	# 	period = int(period) + 1

	# for i in range(int(period)-1):
	# 	wk -= 1
	# 	if wk == 0 :
	# 		wk = 52
	# 	list_week.append(str("WK"+str(wk)))
	list_week = []
	list_year = []
	yk = customer.customer_wk_upload.split(",")
	yk = list(reversed(yk))
	wk = ""
	for i in yk :
		if i != "":
			list_week.append(str(i.split(".")[1]))
			list_year.append(str(i.split(".")[0]))
			wk = int(i.split(".")[1][2:])

	if wk == "":
		wk = arrow.now().isocalendar()[1]
	if len(list_week) < int(period):
		period = int(period) - len(list_week)

		for i in range(int(period)):
			wk -= 1
			if wk == 0 :
				wk = 52
			list_week.append(str("WK"+str(wk)))
	else:
		list_week = list_week[:int(period)]

	list_week = list(reversed(list_week))

	forecast_list = []
	forecast = Forecast.objects.filter(customer=customer)
	if forecast.count() > 0:
		for f in forecast :
			lk = []
			for i in list_week :
				lk.append(0)

			old_year = ""
			old_version = ""
			old_date = ""
			old_work_week = ""

			forecast_detail = Forecast_Detail.objects.filter(forecast=f,status='available').order_by("date",'-id')
			if forecast_detail.count() > 0:
				count_loop = 0
				for fd in forecast_detail:
					new_version = fd.version
					new_date = str(fd.date)
					new_work_week = str(fd.work_week)
					new_year = arrow.get(str(fd.date),"YYYY-MM-DD").format("YYYY")
					if old_year == new_year :
						if fd.work_week in list_week:
							if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
 								pass
 							else:
 								lk[list_week.index(fd.work_week)] += fd.qty
 								old_version = new_version
								old_date = new_date
								old_work_week = new_work_week 

 						if forecast_detail.count()-1 == count_loop :
 							diff_qty = lk[-1] - lk[-2]
							if lk[-2] == 0:
								diff_percent = 0
							else:
								diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"
 							forecast_list_detail = {
								"product_id" : f.product_id,
								# "fulldescription" : f.description,
								# "description" : f.description[:25],
								"date" : old_year,
								"work_week" : lk ,
								"diff_qty": diff_qty,
								"diff_percent": diff_percent	
							}
							forecast_list.append(forecast_list_detail)

					else:
						if old_year == "":
							if fd.work_week in list_week:
								if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
	 								pass
	 							else:
									lk[list_week.index(fd.work_week)] += fd.qty
									old_year = new_year
									old_version = new_version
									old_date = new_date
									old_work_week = new_work_week 

						elif old_year != new_year:
							diff_qty = lk[-1] - lk[-2]
							if lk[-2] == 0:
								diff_percent = 0
							else:
								diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"

							forecast_list_detail = {
								"product_id" : f.product_id,
								# "fulldescription" : f.description,
								# "description" : f.description[:25],
								"date" : old_year,
								"work_week" : lk,
								"diff_qty": diff_qty,
								"diff_percent": diff_percent
							}

							forecast_list.append(forecast_list_detail)

							lk = []
							for i in list_week :
								lk.append(0)
							if fd.work_week in list_week:
								if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
	 								pass
	 							else:
									lk[list_week.index(fd.work_week)] += fd.qty
									old_year = new_year
									old_version = new_version
									old_date = new_date
									old_work_week = new_work_week 

					count_loop += 1

	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"

	param = {'user':userlogin,'upload_status':upload_status,
						'forecast':forecast_list,'work_week' : list_week,
						'unit':unit,'period':period} 

	return param

def home_quarter(request,customer,period,unit):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'

	customer = Customer.objects.get(customer_id=customer)
	# wk = arrow.now().isocalendar()[1]
	# # wk = 4
	# list_week = []
	# forecast = File_Upload.objects.filter(customer=customer,upload_week="WK"+str(wk))
	# if forecast.count() > 0:
	# 	list_week.append(str("WK"+str(wk)))
	# else:
	# 	period = int(period) + 1

	# for i in range(int(period)-1):
	# 	wk -= 1
	# 	if wk == 0 :
	# 		wk = 52
	# 	list_week.append(str("WK"+str(wk)))
	list_week = []
	list_year = []
	yk = customer.customer_wk_upload.split(",")
	yk = list(reversed(yk))
	wk = ""
	for i in yk :
		if i != "":
			list_week.append(str(i.split(".")[1]))
			list_year.append(str(i.split(".")[0]))
			wk = int(i.split(".")[1][2:])

	if wk == "":
		wk = arrow.now().isocalendar()[1]
	if len(list_week) < int(period):
		period = int(period) - len(list_week)

		for i in range(int(period)):
			wk -= 1
			if wk == 0 :
				wk = 52
			list_week.append(str("WK"+str(wk)))
	else:
		list_week = list_week[:int(period)]

	list_week = list(reversed(list_week))

	forecast_list = []
	forecast = Forecast.objects.filter(customer=customer)
	if forecast.count() > 0:
		for f in forecast :
			lk = []
			for i in list_week :
				lk.append(0)

			old_quarter = ""
			old_version = ""
			old_date = ""
			old_work_week = ""

			forecast_detail = Forecast_Detail.objects.filter(forecast=f,status='available').order_by("date",'-id')
			if forecast_detail.count() > 0:
				count_loop = 0
				for fd in forecast_detail:
					new_version = fd.version
					new_date = str(fd.date)
					new_work_week = str(fd.work_week)
					month = arrow.get(str(fd.date),"YYYY-MM-DD").format("MM")
					if  1 <= int(month) and   3 >= int(month):
						year = arrow.get(str(fd.date),"YYYY-MM-DD").format("YYYY")
						new_quarter = year+"/Q1"
					if  4 <= int(month) and   6 >= int(month):
						year = arrow.get(str(fd.date),"YYYY-MM-DD").format("YYYY")
						new_quarter = year+"/Q2"
					if  7 <= int(month) and   9 >= int(month):
						year = arrow.get(str(fd.date),"YYYY-MM-DD").format("YYYY")
						new_quarter = year+"/Q3"
					if  10 <= int(month) and   12 >= int(month):
						year = arrow.get(str(fd.date),"YYYY-MM-DD").format("YYYY")
						new_quarter = year+"/Q4" 

					if old_quarter == new_quarter :
						if fd.work_week in list_week:
							if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
 								pass
 							else:
 								lk[list_week.index(fd.work_week)] += fd.qty
 								old_version = new_version
								old_date = new_date
								old_work_week = new_work_week 

 						if forecast_detail.count()-1 == count_loop :
 							diff_qty = lk[-1] - lk[-2]
							if lk[-2] == 0:
								diff_percent = 0
							else:
								diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"
 							forecast_list_detail = {
								"product_id" : f.product_id,
								# "fulldescription" : f.description,
								# "description" : f.description[:25],
								"date" : old_quarter,
								"work_week" : lk ,
								"diff_qty": int(diff_qty),
								"diff_percent": diff_percent	
							}
							forecast_list.append(forecast_list_detail)

					else:
						if old_quarter == "":
							if fd.work_week in list_week:
								if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
	 								pass
	 							else:
									lk[list_week.index(fd.work_week)] += fd.qty
									old_quarter = new_quarter
									old_version = new_version
									old_date = new_date
									old_work_week = new_work_week 

						elif old_quarter != new_quarter:
							diff_qty = lk[-1] - lk[-2]
							if lk[-2] == 0:
								diff_percent = 0
							else:
								diff_percent = str((lk[-1] - lk[-2])*100 / lk[-2]) + " %"

							forecast_list_detail = {
								"product_id" : f.product_id,
								# "fulldescription" : f.description,
								# "description" : f.description[:25],
								"date" : old_quarter,
								"work_week" : lk,
								"diff_qty": int(diff_qty),
								"diff_percent": diff_percent
							}

							forecast_list.append(forecast_list_detail)

							lk = []
							for i in list_week :
								lk.append(0)
							if fd.work_week in list_week:
								if new_version == old_version and new_date == old_date and new_work_week == old_work_week:
	 								pass
	 							else:
									lk[list_week.index(fd.work_week)] += fd.qty
									old_quarter = new_quarter
									old_version = new_version
									old_date = new_date
									old_work_week = new_work_week 

					count_loop += 1

	try:
		upload_status = request.session['upload']
	except Exception as e:
		upload_status = "False"

	param = {'user':userlogin,'upload_status':upload_status,
						'forecast':forecast_list,'work_week' : list_week,
						'unit':unit,'period':period} 

	return param

def removefile(request):
	fileid = request.POST.get("fileid",'')
	File_Upload.objects.get(id=fileid).delete()
	return HttpResponseRedirect('/upload')

# def readFileAXC(request,username,file_id):
	# 	user = User_Forecast.objects.get(userid=username)
	# 	file = File_Upload.objects.get(id=file_id)

	# 	path = "."+str(file.file_path).replace("%20", " ")
	# 	df = pd.read_excel(path, sheet_name=0 )
	# 	df.to_csv('./media/csvfile.csv', encoding='utf-8', index=False)

	# 	with open('./media/csvfile.csv') as csvfile:
	# 		reader = csv.reader(csvfile)
	# 		row_data = 0
	# 		for row in reader:
	# 			if len(row) >= 15 :
	# 				if row_data == 1 :
	# 					product = Forecast.objects.filter(product_id=row[7],customer=file.customer)
	# 					if product.count() > 0 :
	# 						product_DB = Forecast.objects.get(product_id=row[7],customer=file.customer)
	# 						product_DB.user = user
	# 						product_DB.last_version = arrow.now().format("YYYY-MM-DD")
	# 						product_DB.save()
	# 					else:
	# 						product_new = Forecast.objects.create(product_id=row[7],user=user)
	# 						product_new.description = ""
	# 						product_new.first_demand_date = row[10]
	# 						product_new.last_version = arrow.now().format("YYYY-MM-DD")
	# 						product_new.customer = file.customer
	# 						product_new.save()

	# 					wk = arrow.now().isocalendar()[1]
	# 					forcast = Forecast.objects.get(product_id=row[4],customer=file.customer)
	# 					for date in header[11:]:
	# 						forcast_detail_new = Forecast_Detail.objects.create(forecast=forcast,file_upload=file)
	# 						try:
	# 							forcast_detail_new.date = arrow.get(date,'YYYY-M-D HH:mm').format("YYYY-MM-DD")
	# 							forcast_detail_new.version = arrow.now().format("YYYY-MM-DD")
	# 						except Exception as e:
	# 							print e
	# 						forcast_detail_new.qty = int(row[header.index(date)])
	# 						forcast_detail_new.status = "not available"
	# 						forcast_detail_new.work_week = "WK"+str(wk)
	# 						forcast_detail_new.year = arrow.now().format("YYYY")

	# 						# forcast_detail_new.work_week = "WK5"
	# 						forcast_detail_new.save()

	# 				if row[0] == "Row" :
	# 					header = row
	# 					row_data = 1

	# 	Forecast_Detail.objects.filter(file_upload=file).update(status="available")
	# 	temp = Upload_file_temp.objects.get(file_upload=file)
	# 	temp.is_done = True
	# 	temp.save()

	# 	request.session['upload'] = "False"

	# 	return True

# def readFileAXC(request,username,file_id):
	# 	user = User_Forecast.objects.get(userid=username)
	# 	file = File_Upload.objects.get(id=file_id)

	# 	path = "."+str(file.file_path).replace("%20", " ")
	# 	df = pd.read_excel(path, sheet_name=0 )
	# 	df.to_csv('./media/csvfile.csv', encoding='utf-8', index=False)

	# 	with open('./media/csvfile.csv') as csvfile:
	# 		reader = csv.reader(csvfile)
	# 		row_data = 0
	# 		for row in reader:
	# 			if len(row) >= 15 :
	# 				if row_data == 1 :
	# 					product = Forecast.objects.filter(product_id=row[7],customer=file.customer)
	# 					if product.count() > 0 :
	# 						product_DB = Forecast.objects.get(product_id=row[7],customer=file.customer)
	# 						product_DB.user = user
	# 						product_DB.last_version = arrow.now().format("YYYY-MM-DD")
	# 						product_DB.save()
	# 					else:
	# 						product_new = Forecast.objects.create(product_id=row[7],user=user)
	# 						product_new.description = ""
	# 						product_new.first_demand_date = row[13]
	# 						product_new.last_version = arrow.now().format("YYYY-MM-DD")
	# 						product_new.customer = file.customer
	# 						product_new.save()

	# 					wk = arrow.now().isocalendar()[1]
	# 					forcast = Forecast.objects.get(product_id=row[7],customer=file.customer)
	# 					for date in header[14:]:
	# 						forcast_detail_new = Forecast_Detail.objects.create(forecast=forcast,file_upload=file)
	# 						forcast_detail_new.date = arrow.get(date,'YYYY-M-D HH:mm:ss').format("YYYY-MM-DD")
	# 						forcast_detail_new.version = arrow.now().format("YYYY-MM-DD")
	# 						forcast_detail_new.qty = int(row[header.index(date)])
	# 						forcast_detail_new.status = "not available"
	# 						forcast_detail_new.work_week = "WK"+str(wk)
	# 						forcast_detail_new.year = arrow.now().format("YYYY")

	# 						# forcast_detail_new.work_week = "WK5"
	# 						forcast_detail_new.save()

	# 				if row[0] == "Row" :
	# 					header = row
	# 					row_data = 1

	# 	Forecast_Detail.objects.filter(file_upload=file).update(status="available")
	# 	temp = Upload_file_temp.objects.get(file_upload=file)
	# 	temp.is_done = True
	# 	temp.save()

	# 	request.session['upload'] = "False"

	# 	return True

#	def readFileAXC(request,username,file_id): #2019w20
	user = User_Forecast.objects.get(userid=username)
	file = File_Upload.objects.get(id=file_id)

	path = "."+str(file.file_path).replace("%20", " ")
	df = pd.read_excel(path, sheet_name=0 )
	df.to_csv('./media/csvfile.csv', encoding='utf-8', index=False)

	with open('./media/csvfile.csv') as csvfile:
		reader = csv.reader(csvfile)
		row_data = 0
		for row in reader:
			if len(row) >= 15 :
				if row_data == 1 :
					product = Forecast.objects.filter(product_id=row[4],customer=file.customer)
					if product.count() > 0 :
						product_DB = Forecast.objects.get(product_id=row[4],customer=file.customer)
						product_DB.user = user
						product_DB.last_version = arrow.now().format("YYYY-MM-DD")
						product_DB.save()
					else:
						product_new = Forecast.objects.create(product_id=row[4],user=user)
						product_new.description = ""
						product_new.first_demand_date = row[11]
						product_new.last_version = arrow.now().format("YYYY-MM-DD")
						product_new.customer = file.customer
						product_new.save()

					wk = arrow.now().isocalendar()[1]
					forcast = Forecast.objects.get(product_id=row[4],customer=file.customer)
					for date in header[12:]:
						print header.index(date)
						new_date = datetime.datetime.strptime(date + '-1', "%Yw%W-%w").strftime('%Y-%m-%d')
						forcast_detail_new = Forecast_Detail.objects.create(forecast=forcast,file_upload=file)
						forcast_detail_new.date = new_date
						forcast_detail_new.version = arrow.now().format("YYYY-MM-DD")
						if  row[header.index(date)] == "":
							forcast_detail_new.qty = 0
						else:
							forcast_detail_new.qty = int(float(row[header.index(date)].replace(',','')))
						forcast_detail_new.status = "not available"
						forcast_detail_new.work_week = "WK"+str(wk)
						forcast_detail_new.year = arrow.now().format("YYYY")
						# forcast_detail_new.work_week = "WK5"
						forcast_detail_new.save()

				if row[0] == "Row" :
					header = row
					row_data = 1

	Forecast_Detail.objects.filter(file_upload=file).update(status="available")
	temp = Upload_file_temp.objects.get(file_upload=file)
	temp.is_done = True
	temp.save()

	request.session['upload'] = "False"

	return True

def readFileAXC(request,username,file_id):
	user = User_Forecast.objects.get(userid=username)
	file = File_Upload.objects.get(id=file_id)
	try:

		path = "."+str(file.file_path).replace("%20", " ")
		df = pd.read_excel(path, sheet_name=0 )
		df.to_csv('./media/csvfile.csv', encoding='utf-8', index=False)

		with open('./media/csvfile.csv') as csvfile:
			reader = csv.reader(csvfile)
			row_data = 0
			for row in reader:
				if len(row) >= 12 :
					if row_data == 1 :
						product = Forecast.objects.filter(product_id=row[4],customer=file.customer)
						if product.count() > 0 :
							product_DB = Forecast.objects.get(product_id=row[4],customer=file.customer)
							product_DB.user = user
							product_DB.last_version = arrow.now().format("YYYY-MM-DD")
							product_DB.save()
						else:
							product_new = Forecast.objects.create(product_id=row[4],user=user)
							product_new.description = ""
							product_new.first_demand_date = row[11]
							product_new.last_version = arrow.now().format("YYYY-MM-DD")
							product_new.customer = file.customer
							product_new.save()

						wk = arrow.now().isocalendar()[1]
						forcast = Forecast.objects.get(product_id=row[4],customer=file.customer)
						for date in header[12:]:
							forcast_detail_new = Forecast_Detail.objects.create(forecast=forcast,file_upload=file)
							forcast_detail_new.date = arrow.get(date,'YYYY-M-D HH:mm:ss').format("YYYY-MM-DD")
							forcast_detail_new.version = arrow.now().format("YYYY-MM-DD")
							forcast_detail_new.qty = int(float(row[header.index(date)].replace(',',''))) if row[header.index(date)] != '' else 0
							forcast_detail_new.status = "not available"
							forcast_detail_new.work_week = "WK"+str(wk)
							forcast_detail_new.year = arrow.now().format("YYYY")
							# forcast_detail_new.work_week = "WK16"
							forcast_detail_new.save()
					if row[0] == "Row" :
						header = row
						row_data = 1
		Forecast_Detail.objects.filter(file_upload=file).update(status="available")
		temp = Upload_file_temp.objects.get(file_upload=file)
		temp.is_done = True
		temp.save()
		request.session['upload'] = "False"
		return True
	except Exception as e:
		print e
		# import traceback
		# details = traceback.format_exc()
		temp = Upload_file_temp.objects.get(file_upload=file)
		temp.is_done = True
		temp.remark = str(e)
		temp.save()
		# send_email('CDM Background exception happened', details)

def readFileMTN(request,username,file_id):
	user = User_Forecast.objects.get(userid=username)
	file = File_Upload.objects.get(id=file_id)

	path = "."+str(file.file_path).replace("%20", " ")
	year = arrow.now().format('YYYY')
	token_year = 0 
	header = []
	with open(path , 'r') as content:
		line = content.readlines()
		count = 0
		for l in line:
			row = l.split('\t')
			if count == 0: 
				for k in row[:4]:
					header.append(k)
				for k in row[4:] :
					# print k
					month = arrow.get(k.split('(')[0], 'MMM').format("01/MM")
					if token_year != 0:
						year = str(int(year)+1)
						token_year = 0
					if month == '01/12':
						token_year = 1
					date = arrow.get(k.split('(')[0], 'MMM').format("01/MM")+"/"+year
					header.append(date)
			else:
				product = Forecast.objects.filter(product_id=row[2],customer=file.customer)
				if product.count() > 0 :
					product_DB = Forecast.objects.get(product_id=row[2],customer=file.customer)
					product_DB.user = user
					product_DB.last_version = arrow.now().format("YYYY-MM-DD")
					product_DB.save()
				else:
					product_new = Forecast.objects.create(product_id=row[2],user=user)
					product_new.description = ""
					product_new.first_demand_date = ""
					product_new.last_version = arrow.now().format("YYYY-MM-DD")
					product_new.customer = file.customer
					product_new.save()

				wk = arrow.now().isocalendar()[1]
				forcast = Forecast.objects.get(product_id=row[2],customer=file.customer)
				for date in header[4:]:
					# print date
					forcast_detail_new = Forecast_Detail.objects.create(forecast=forcast,file_upload=file)
					forcast_detail_new.date = arrow.get(date,'DD/MM/YYYY').format("YYYY-MM-DD")
					forcast_detail_new.version = arrow.now().format("YYYY-MM-DD")
					forcast_detail_new.qty = int(row[header.index(date)])
					forcast_detail_new.status = "not available"
					forcast_detail_new.work_week = "WK"+str(wk)
					forcast_detail_new.year = arrow.now().format("YYYY")
					# forcast_detail_new.year = '2018'
					# forcast_detail_new.work_week = "WK44"
					forcast_detail_new.save()
			count +=1 

	Forecast_Detail.objects.filter(file_upload=file).update(status="available")
	temp = Upload_file_temp.objects.get(file_upload=file)
	temp.is_done = True
	temp.save()

	request.session['upload'] = "False"

	return True	

def readFileLNK(request,username,file_id):
	user = User_Forecast.objects.get(userid=username)
	file = File_Upload.objects.get(id=file_id)

	path = "."+str(file.file_path).replace("%20", " ")
	df = pd.read_excel(path, sheet_name=0 )
	df.to_csv('./media/csvfile.csv', encoding='utf-8', index=False )

	with open('./media/csvfile.csv') as csvfile:
		reader = csv.reader(csvfile)
		row_data = 0
		for row in reader:
			yyear = int(arrow.now().format("YYYY"))
			old_month = ""
			print row
			row[2] = row[2].replace("'","")
			if row_data == 1:
				product = Forecast.objects.filter(product_id=row[2].decode("ascii", errors="ignore").encode(),customer=file.customer)
				if product.count() > 0 :
					product_DB = Forecast.objects.get(product_id=row[2].decode("ascii", errors="ignore").encode(),customer=file.customer)
					product_DB.user = user
					product_DB.last_version = arrow.now().format("YYYY-MM-DD")
					# product_DB.last_version = "2019-01-01"

					product_DB.save()
				else:
					product_new = Forecast.objects.create(product_id=row[2].decode("ascii", errors="ignore").encode(),user=user)
					product_new.description = row[3].decode("ascii", errors="ignore").encode()
					product_new.first_demand_date = ""
					product_new.last_version = arrow.now().format("YYYY-MM-DD")
					# product_new.last_version = "2019-01-01"
					product_new.customer = file.customer
					product_new.save()

				wk = arrow.now().isocalendar()[1]
				forcast = Forecast.objects.get(product_id=row[2].decode("ascii", errors="ignore").encode(),customer=file.customer)
				for date in header[6:18]:
					if "FM" in date :
						if int(date.split("FM")[1]) == 1 and old_month == 12:
							yyear += 1

						new_date = "01/"+date.split("FM")[1]+"/" + str(yyear)
						old_month = int(date.split("FM")[1])

						# print row[2], date , row[header.index(date)]
						forcast_detail_new = Forecast_Detail.objects.create(forecast=forcast,file_upload=file)
						forcast_detail_new.date = arrow.get(new_date,'DD/M/YYYY').format("YYYY-MM-DD")
						forcast_detail_new.version = arrow.now().format("YYYY-MM-DD")
						# forcast_detail_new.version = "2019-01-01"
						forcast_detail_new.qty = int(row[header.index(date)])
						forcast_detail_new.status = "not available"
						forcast_detail_new.work_week = "WK"+str(wk)
						forcast_detail_new.year = arrow.now().format("YYYY")
						# forcast_detail_new.year = "2019"
						# forcast_detail_new.work_week = "WK1"
						forcast_detail_new.save()

			if row_data == 0 :
				header = row
				row_data = 1

	Forecast_Detail.objects.filter(file_upload=file).update(status="available")
	temp = Upload_file_temp.objects.get(file_upload=file)
	temp.is_done = True
	temp.save()
	return True	

def readSVIFile(request,username,file_id,customer_version):
	user = User_Forecast.objects.get(userid=username)
	file = File_Upload_Svi.objects.get(id=file_id)
	path = "."+str(file.file_path).replace("%20", " ")
	print customer_version
	with open(path) as file:
		line = file.readlines()
		for l in line:
			print l 

	# Forecast_Detail_.objects.filter(file_upload=file).update(status="available")
	temp = Upload_file_temp_svi.objects.get(file_upload=file)
	temp.is_done = True
	temp.save()

	return True

def approve_pn(request):
	pn = request.GET.get("pn","")
	date = request.GET.get("date","")
	#lotus900
	conn = Connection(user='sapconnect', passwd='svi1234*', ashost='192.168.2.7', sysnr='00', client='302')
	# conn = Connection(user='sapconnect', passwd='lotus900', ashost='192.168.0.29', sysnr='00', client='100')
	result = conn.call('ZFCO_GETFORECAST', WERKS='SVI2', MATNR=pn, VERSB='00', KUNNR='1100017')
	data = []
	mat = pn
	print result['FORECAST']
	for i in result['FORECAST']:
		customer_date = arrow.get(i['PDATU'],'YYYYMMDD').format("YYYY-MM-DD")
		customer_date = arrow.get(i['PDATU'],'YYYYMMDD').format("YYYY-MM-DD")
		# forecast = Forecast.objects.get(product_id=pn)
		# fd = Forecast_Detail.objects.filter(forecast=forecast,version=date)
		# for j in fd :
		# 	if str(j.date) == str(sap_date):
		# 		print j.date , sap_date
		# print int(i['PLNMG']) ,"----------------"
		data.append({
			'date':sap_date,
			'customer_qty': int(i['PLNMG']),
			'svi_qty': int(i['PLNMG']),
			'newqty' : fd.qty
		})

	param = {'pn':pn,'mat':mat,'data':data}
	return render(request, 'approve_pn.html',param) 

def svi_version(request):
	param ={}
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/')

	svi_version_list = []
	list_customer = user_forecast.customer_list.split(',')
	
	for i in list_customer:
		cus = Customer.objects.get(customer_id=i)
		forecast_svi = Forecast_svi.objects.filter(Q(customer=cus),Q(user=user_forecast)|Q(status='Publish'))
		
		for fsvi in forecast_svi:
			if len(fsvi.file_upload.file_name) > 22:
				filename = fsvi.file_upload.file_name[:23]+"..."
			else:
				filename = fsvi.file_upload.file_name

			svi_version_list.append({
				'customer_name': fsvi.customer.customer_name,
				'file_name' : filename, 
				'file_full_name' : fsvi.file_upload.file_name, 
				'file_path' : fsvi.file_upload.file_path, 
				'version' : arrow.get(fsvi.create_date,'YYYY/MM/DD HH:mm:ss').format("YYYYMMDDHHmm"), 
				'last_update' : arrow.get(fsvi.last_update,'YYYY/MM/DD HH:mm:ss').format("DD.MM.YYYY HH:mm"), 
				'id':fsvi.id,
				'owner':fsvi.user.firstname,
				'status' : fsvi.status
			})
	param = {'forecast_svi' : svi_version_list,'user':user_forecast}

	return render(request, 'svi_version.html',param) 

def create_svi(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	user_forecast = User_Forecast.objects.get(userid=username)
	cus_list = user_forecast.customer_list.split(',')
	customer_list = []
	file_list = []
	for i in cus_list:
		cus = Customer.objects.get(customer_id=i)
		customer_list.append({
			'customer_id' : cus.customer_id,
			'customer_name' :cus.customer_name
			})
		file = File_Upload.objects.filter(customer=cus).order_by('-id')
		for f in file :
			file_list.append({
				'customer' :  cus.customer_id,
				'file_id' :	f.id,
				'file_name' :f.file_name
			})

	param ={'customer':customer_list,'file':file_list,'current_customer':cus_list[0],
					'customer_json':json.dumps(customer_list),'file_json':json.dumps(file_list)}

	return render(request, 'create_svi.html',param) 

def api_get_forecast(request):
	results = []
	customer = request.GET.get('customer','')
	file_id = request.GET.get('file','')
	file_upload = File_Upload.objects.get(id=file_id)
	forecast = Forecast_Detail.objects.filter(file_upload=file_upload)
	for i in forecast:
		results.append({
			'product_id':i.forecast.product_id.split(" ",1)[0],
			'date':str(i.date),
			'qty':i.qty,
		})
		
	return HttpResponse(json.dumps(results), content_type="application/json")

def create_svi_version(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	customer = request.POST.get('customer_select','')
	file_id = request.POST.get('file_select','')
	product_id = request.POST.getlist('product_id[]','')
	date = request.POST.getlist('date[]','')
	old_date = request.POST.getlist('old_date[]','')
	qty = request.POST.getlist('qty[]','')
	old_qty = request.POST.getlist('old_qty[]','')

	print old_date

	cus = Customer.objects.get(customer_id=customer)
	file = File_Upload.objects.get(id=file_id)
	forecast_svi = Forecast_svi.objects.create(user=user_forecast,customer=cus,file_upload=file)
	forecast_svi.create_date = arrow.now().format("YYYY/MM/DD HH:mm:ss")
	forecast_svi.last_update = arrow.now().format("YYYY/MM/DD HH:mm:ss")
	forecast_svi.save()


	dataFrame = pd.DataFrame({'product_id':product_id, 'date':date, 'qty':qty, 
										'old_date':old_date, 'old_qty':old_qty})
	for i, r in dataFrame.iterrows():
		fd = Forecast_Detail_svi.objects.create(forecast=forecast_svi)
		fd.product_id = r['product_id']
		fd.qty = r['qty']
		fd.old_qty = r['old_qty']
		fd.date = arrow.get(r['date'],'YYYY-MM-DD').format("YYYY-MM-DD")
		fd.old_date = arrow.get(r['old_date'],'YYYY-MM-DD').format("YYYY-MM-DD")
		fd.save()

	return HttpResponseRedirect('/svi-version')

def delete_svi_version(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	version_id = request.GET.get('id','')
	print version_id
	Forecast_svi.objects.get(id=version_id).delete()

	return HttpResponseRedirect('/svi-version')

def changeStatus(request):
	status = request.GET.get('status')
	forecast_id = request.GET.get('id')

	forecast = Forecast_svi.objects.get(id=forecast_id)
	forecast.status = status
	forecast.save()

	return HttpResponseRedirect('/svi-version')
	
def view_svi(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	forecast_id = request.GET.get('id')
	forecast = Forecast_svi.objects.get(id=forecast_id)
	forecast.create_date = arrow.get(forecast.create_date,'YYYY/MM/DD HH:mm:ss').format("YYYYMMDDHHmm")
	forecast_detail = Forecast_Detail_svi.objects.filter(forecast=forecast)
	for i in forecast_detail:
		i.date = str(i.date)
		i.old_qty = int(i.old_qty)
		i.qty = int(i.qty)
	param = {'forecast':forecast , 'forecast_detail':forecast_detail}

	return render(request, 'view_svi.html',param) 

def view_approve(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	forecast_id = request.GET.get('id')
	forecast = Forecast_svi.objects.get(id=forecast_id)
	forecast.create_date = arrow.get(forecast.create_date,'YYYY/MM/DD HH:mm:ss').format("YYYYMMDDHHmm")
	forecast_detail = Forecast_Detail_svi.objects.filter(forecast=forecast)

	old_product_id = ""
	forecast_detail_list = []
	list_product_id = []
	list_date = []
	for i in forecast_detail:
		if old_product_id != i.product_id:
			list_product_id.append(i.product_id)
		old_product_id = i.product_id
		forecast_detail_list.append({
			'product_id': str(i.product_id),
			'date': str(i.date),
			'qty' : int(i.qty),
			'sap_qty' : 0,
			'status': 'new'
			})
		list_date.append(str(i.date)+str(i.product_id))
	
	for i in list_product_id:
		# conn = Connection(user='sapconnect', passwd='svi1234*', ashost='192.168.2.7', sysnr='00', client='302')
		conn = Connection(user='sapconnect', passwd='lotus900', ashost='192.168.0.29', sysnr='00', client='100')
		result = conn.call('ZFCO_GETFORECAST', WERKS='SVI2', MATNR=i, VERSB='00', KUNNR=forecast.customer.customer_id)
		print result ,forecast.customer.customer_id
		for f in result['FORECAST']:
			customer_date = arrow.get(f['PDATU'],'YYYYMMDD').format("YYYY-MM-DD")
			if customer_date+i in list_date:
				key = list_date.index(customer_date+i)
				forecast_detail_list[key]['sap_qty'] = int(f['PLNMG'])
				forecast_detail_list[key]['status'] = "two"
			else:
				forecast_detail_list.append({
					'product_id': str(i),
					'date' : customer_date,
					'qty' : 0,
					'sap_qty': int(f['PLNMG']),
					'status': 'sap'
					})

	param = {'forecast':forecast , 'forecast_detail':forecast_detail_list}

	return render(request, 'view_approve.html',param) 

def update_svi_version(request):
	try:
		username = request.session['username'] 
		user = Tblusers.objects.using("user").filter(userid=username)
		userlogin = user[0]
		user_forecast = User_Forecast.objects.get(userid=username)
	except Exception as e:
		userlogin = 'notlogin'
		return HttpResponseRedirect('/login/') 

	forecast_id = request.POST.get('forecast_id','')
	product_id = request.POST.getlist('product_id[]','')
	date = request.POST.getlist('date[]','')
	qty = request.POST.getlist('qty[]','')
	old_date = request.POST.getlist('old_date[]','')
	old_qty = request.POST.getlist('old_qty[]','')

	forecast_svi = Forecast_svi.objects.get(id=forecast_id)
	forecast_svi.last_update = arrow.now().format("YYYY/MM/DD HH:mm:ss")
	forecast_svi.save()
	
	Forecast_Detail_svi.objects.filter(forecast=forecast_svi).delete()

	dataFrame = pd.DataFrame({'product_id':product_id, 'date':date, 'qty':qty,
												'old_date':old_date, 'old_qty':old_qty})
	for i, r in dataFrame.iterrows():
		fd = Forecast_Detail_svi.objects.create(forecast=forecast_svi)
		fd.product_id = r['product_id']
		fd.qty = r['qty']
		fd.date = arrow.get(r['date'],'YYYY-MM-DD').format("YYYY-MM-DD")
		fd.old_qty = r['old_qty']
		fd.old_date = arrow.get(r['old_date'],'YYYY-MM-DD').format("YYYY-MM-DD")
		fd.save()

	return HttpResponseRedirect('/svi-version')

def send_email(Subject,Details):
	try:
		mail_subject = Subject
		message += Details
		email = EmailMessage(mail_subject, message,to=['sujaray@svi.co.th'])
		email.send()
		msg = "Success"
	except Exception as e:
		msg = e
