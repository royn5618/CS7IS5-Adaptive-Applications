# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core import serializers

from application import dbops
from application import forms
from application import models
from application.models import NewsModel, NewsProfileModel,UserStaticPrefs

import json
from itertools import chain
from django.db.models import Q
import re

# Create your views here.

class HomePageView(TemplateView):
	def get(self, request, **kwargs):
		return render(request, 'index.html', context=None)

class BrowseView(TemplateView):
	def get(request):
		# default dictionary to be overwritten when ranking logic is implemented
		percentages = ranking(request.user)
		# percentages = {'economy': 5, 'politics': 5, 'science': 5, 'sport': 5, 'art': 5, 'misc':5 }
		Latest_news_list = NewsModel.objects.order_by('-published_at')
		total_length = len(Latest_news_list)
		for key, value in percentages.items():
			percentages[key] = (total_length * value) / 100
		# sort
		sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
		# print(sorted_percentages)
		all_news = []
		temp0 = NewsModel.objects.filter(categories__contains=sorted_percentages[0][0]).order_by('-published_at')[
				:sorted_percentages[0][1]]
		temp1 = NewsModel.objects.filter(categories__contains=sorted_percentages[1][0]).filter(
			~Q(categories__contains=sorted_percentages[0][0])).order_by('-published_at')[
				:sorted_percentages[1][1]]
		temp2 = NewsModel.objects.filter(categories__contains=sorted_percentages[2][0]).filter(
			~Q(categories__contains=sorted_percentages[0][0])).filter(
			~Q(categories__contains=sorted_percentages[1][0])).order_by('-published_at')[
				:sorted_percentages[2][1]]
		temp3 = NewsModel.objects.filter(categories__contains=sorted_percentages[3][0]).filter(
			~Q(categories__contains=sorted_percentages[0][0])).filter(
			~Q(categories__contains=sorted_percentages[1][0])).filter(
			~Q(categories__contains=sorted_percentages[2][0])).order_by('-published_at')[
				:sorted_percentages[3][1]]
		temp4 = NewsModel.objects.filter(categories__contains=sorted_percentages[4][0]).filter(
			~Q(categories__contains=sorted_percentages[0][0])).filter(
			~Q(categories__contains=sorted_percentages[1][0])).filter(
			~Q(categories__contains=sorted_percentages[2][0])).filter(
			~Q(categories__contains=sorted_percentages[3][0])).order_by('-published_at')[
				:sorted_percentages[4][1]]
		misc_news = NewsModel.objects.filter(categories__contains=sorted_percentages[5][0]).order_by('-published_at')[
					:sorted_percentages[5][1]]
		all_news = list(chain(temp0, temp1, temp2, temp3, temp4, misc_news))
		# pdb.set_trace()
		seen={}
		corrected_news=[]
		for news in all_news:
			if news.title not in seen.keys():
				seen[news.title]=1
				corrected_news.append(news)
		for news in corrected_news:
			news.categories = re.sub(r'^{', '', news.categories)
			news.categories = re.sub(r'\}$', '', news.categories)
			news.categories = news.categories.split('\',\'')
			news.categories = [cat.replace('\'', '') for cat in news.categories]
		return render(request, 'mainpage.html', {'all_news': corrected_news})

class UserRegView(TemplateView):
	def get(self, request, **kwargs):
		return render(request, 'userSignup.html', context=None)

	def return_data(request):
		#Add DB operations here
		dbops.UserOperations.register(request.POST['username'], request.POST['email'], request.POST['password'])
		return render(request, 'index.html', context=None)

	def signup(request):
		if request.method == 'POST':
			form = UserCreationForm(request.POST)
			if form.is_valid() and request.POST['email'] != "":
				username = form.cleaned_data.get('username')
				raw_password = form.cleaned_data.get('password1')
				email =  request.POST['email']

				#Also save to SQLite DB
				dbops.UserOperations.register(username, email, raw_password)

				is_admin = request.POST.get('admin')
				if is_admin is not None:
					user = User.objects.create_superuser(username=username, email=email, password=raw_password)
					userstaticprefs = models.UserStaticPrefs.objects.create(profileof_user=user)
					return redirect('../admin')

				newuser = form.save()
				userstaticprefs = models.UserStaticPrefs.objects.create(profileof_user=newuser)

				user = authenticate(username=username, password=raw_password)
				login(request, user)
				return redirect('../registration/profile')
		else:
			form = UserCreationForm()
		return render(request, 'registration/signup.html', {'form': form})

	def success(request):
		return redirect('../browse') #render(request, 'index.html', context=None)

@login_required
@transaction.atomic
def update_profile(request):
	if request.method == 'POST':
		prefs_form = forms.UserStaticPrefsForm(request.POST)
		if prefs_form.is_valid():
			userstaticprefs = prefs_form.save(commit=False)
			userstaticprefs.profileof_user = request.user
			models.UserStaticPrefs.objects.filter(profileof_user = request.user.id).delete()
			userstaticprefs.save()
			update_static_user_prefs(request.user)
			return redirect("/browse") #render(request, 'index.html', context=None)
		else:
			messages.error(request, _('Please correct the error below.'))
	else:
		userPrefs = models.UserStaticPrefs.objects.filter(profileof_user = request.user.id).get()
		prefs_form = forms.UserStaticPrefsForm(initial={'economy': userPrefs.economy, 'politics' : userPrefs.politics, 'science' : userPrefs.science, 'arts' : userPrefs.arts, 'sports' : userPrefs.sports, 'misc' : userPrefs.misc})
	return render(request, 'profile.html', {
		'prefs_form': prefs_form
	})

class AjaxPosts(TemplateView):
	def render_to_json_response(context):
		data = json.dumps(context)
		response_kwargs['content_type'] = 'application/json'
		return HttpResponse(data, **response_kwargs)

	def testpost(request):
		if(request.is_ajax):
			Latest_news_list=NewsModel.objects.order_by('-title')[:2]
			context =  {'Latest_news_list': Latest_news_list}
			data = serializers.serialize('json', Latest_news_list)
			return HttpResponse(data, content_type='application/json')
		else:
			message = "fail"
			return HttpResponse(message)

	def updateNewsShowMore(request):
		if(request.is_ajax):
			#Exists?
			newsObject = NewsProfileModel.objects.filter(user=request.user.id, news = request.POST['newsId']).first()
			if newsObject is None:
				news = NewsModel.objects.filter(id=request.POST['newsId']).first()
				user = User.objects.filter(id=request.user.id).first()

				newsObject = NewsProfileModel(user=user, news=news, show_more=request.POST['showMore'])
				print(newsObject.user, " : ", newsObject.news)
				newsObject.save()
				print(newsObject.show_more)
				print(newsObject.relevance)
				update_user_prefs(request.user, newsObject.show_more, newsObject.relevance, newsObject.news.categories)

				return HttpResponse("new NewsProfileModel created")
			else:
				newsObject.show_more = request.POST['showMore']
				newsObject.save()
				print(newsObject.show_more)
				print(newsObject.relevance)
				update_user_prefs(request.user, newsObject.show_more, newsObject.relevance, newsObject.news.categories)
				return HttpResponse("Existing NewsProfileModel updated")

		else:
			message = "fail"
			return HttpResponse(message)

	def update_relevance(request):
		if (request.is_ajax):
			print(request.user)
			message = "success"
			news_id = request.POST.get('news_id')
			relevance = request.POST.get('relevance')
			news_profile_object = NewsProfileModel.objects.filter(user=request.user,news=news_id).first()
			if news_profile_object is None:
				news_model_object = NewsModel.objects.get(id=news_id)
				news_profile_object = NewsProfileModel.objects.create(user=request.user, news=news_model_object,
																	  relevance=relevance)
			else:
				news_profile_object.relevance = relevance
			news_profile_object.save()
			# updating score
			print(news_profile_object.show_more)
			print(news_profile_object.relevance)
			update_user_prefs(request.user,news_profile_object.show_more,news_profile_object.relevance,news_profile_object.news.categories)

		else:
			message = "fail"
		return HttpResponse(message)

def update_user_prefs(user, show_more, relevance, category):
	user_prefs_object = UserStaticPrefs.objects.filter(profileof_user=user).first()
	weight_TT = 0.9
	weight_TF = 0.5
	weight_FF = 0.1
	if int(show_more) == 1 and int(relevance) == 1:
		print("inside if")
		user_prefs_object = select_category(user_prefs_object, category, weight_TT)
	elif int(show_more) == 0 and int(relevance) == 0:
		print("inside elif")
		user_prefs_object = select_category(user_prefs_object, category, weight_FF)
	else:
		print("inside else")
		user_prefs_object = select_category(user_prefs_object, category, weight_TF)
	user_prefs_object.save()

def update_static_user_prefs(user):
	user_prefs_object = UserStaticPrefs.objects.filter(profileof_user=user).first()
	weight_cat = 0.5
	if int(user_prefs_object.economy) == 1:
		user_prefs_object = select_category(user_prefs_object, "economy", weight_cat)
	if int(user_prefs_object.politics) == 1:
		user_prefs_object = select_category(user_prefs_object, "politics", weight_cat)
	if int(user_prefs_object.science) == 1:
		user_prefs_object = select_category(user_prefs_object, "science", weight_cat)
	if int(user_prefs_object.arts) == 1:
		user_prefs_object = select_category(user_prefs_object, "arts", weight_cat)
	if int(user_prefs_object.sports) == 1:
		user_prefs_object = select_category(user_prefs_object, "sport", weight_cat)

	user_prefs_object.save()

def select_category(user_prefs_object, category, weight):
	if user_prefs_object is None:
		if "economy" in category:
			user_prefs_object = UserStaticPrefs.objects.create(profileof_user=user, dy_economy=weight)
		if "politics" in category:
			user_prefs_object = UserStaticPrefs.objects.create(profileof_user=user, dy_politics=weight)
		if "science" in category:
			user_prefs_object = UserStaticPrefs.objects.create(profileof_user=user, dy_science=weight)
		if "arts" in category:
			user_prefs_object = UserStaticPrefs.objects.create(profileof_user=user, dy_arts=weight)
		if "sport" in category:
			user_prefs_object = UserStaticPrefs.objects.create(profileof_user=user, dy_sports=weight)
	else:
		if "economy" in category:
			user_prefs_object.dy_economy = user_prefs_object.dy_economy + weight
		if "politics" in category:
			user_prefs_object.dy_politics = user_prefs_object.dy_politics + weight
		if "science" in category:
			user_prefs_object.dy_science = user_prefs_object.dy_science + weight
		if "arts" in category:
			user_prefs_object.dy_arts = user_prefs_object.dy_arts + weight
		if "sport" in category:
			user_prefs_object.dy_sports = user_prefs_object.dy_sports + weight
	return user_prefs_object

def ranking(user):
	print(user)
	user_prefs_object = UserStaticPrefs.objects.filter(profileof_user=user).first()
	user_cat_prefs = {}

	if user_prefs_object is None:
		value = 100/6
		ranking = {"economy": value, "arts": value, "politics": value, "science": value, "sport": value, "misc": value}
	else:
		user_cat_prefs["economy"] = user_prefs_object.dy_economy
		user_cat_prefs["arts"] = user_prefs_object.dy_arts
		user_cat_prefs["politics"] = user_prefs_object.dy_politics
		user_cat_prefs["science"] = user_prefs_object.dy_science
		user_cat_prefs["sport"] = user_prefs_object.dy_sports

		ranking = {"economy": 5, "arts": 5, "politics": 5, "science": 5, "sport": 5, "misc": 5}
		user_cat_prefs_100 = {}
		user_cat_prefs_70 = {}

		total_prefs = 0
		for key, value in user_cat_prefs.items():
			total_prefs = total_prefs + value

		if total_prefs == 0:
			for key, value in ranking.items():
				ranking[key] = 100 / len(ranking)

		else:
			for key, value in user_cat_prefs.items():
				user_cat_prefs_100[key] = (value / total_prefs) * 100

			# mapping to 70%
			for key, value in user_cat_prefs_100.items():
				user_cat_prefs_70[key] = (value / 100) * 70

			for key, value in user_cat_prefs_70.items():
				ranking[key] = ranking[key] + value

		# print(user_cat_prefs_100)
		# print(user_cat_prefs_70)

	print(ranking)
	return ranking




