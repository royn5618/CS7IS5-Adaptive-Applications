from django.conf.urls import url
from application import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),

    #User Reg
    url(r'^signup/$', views.UserRegView.signup, name='registration/signup'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^registration/success/$', views.UserRegView.success, name="browse"),
    url(r'^mainpage/$', views.BrowseView.get, name="browse"),
    url(r'^registration/profile$', views.update_profile, name="registration/profile"),

    url(r'^browse$', views.BrowseView.get, name="browse"),

    url(r'^testAjax/$', views.AjaxPosts.testpost, name="testAjax"),
    url(r'^updateShowMore/$', views.AjaxPosts.updateNewsShowMore, name="updateShowMore"),
    url(r'^relevance/$', views.AjaxPosts.update_relevance, name="updateRelevance")
]