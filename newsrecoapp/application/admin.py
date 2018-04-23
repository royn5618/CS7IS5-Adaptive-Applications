# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import UserModel, UserProfileModel, NewsModel, NewsProfileModel, UserStaticPrefs

# Register your models here.
admin.site.register(UserModel)
admin.site.register(UserProfileModel)
admin.site.register(NewsModel)
admin.site.register(NewsProfileModel)
admin.site.register(UserStaticPrefs)