"""wobeissues URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
import views
urlpatterns = [
    url(r'^refresh/(?P<boardid>[0-9]+)/', views.issues_refresh),
    url(r'^update/(?P<issueid>[0-9]+)/', views.issues_update),
    url(r'^show/(?P<owner>[a-z_0-9]+)/(?P<board>[a-z_0-9]+)/$', views.issues_show),
    url(r'^repos/(?P<board>[a-z_0-9]+)/$', views.issues_repos),
    url(r'^repos/delete/(?P<board>[a-z_0-9]+)/(?P<repoid>[0-9]+)/$', views.issues_repo_delete),
    url(r'^board/show/$', views.show_board),
    url(r'^board/del/(?P<boardid>[0-9]+)/$', views.del_board),
    url(r'^board/edit/(?P<boardid>[0-9]+)/$', views.edit_board),
    url(r'^users/(?P<boardid>[0-9]+)/del/(?P<userid>[0-9]+)/$', views.user_del),
    url(r'^users/(?P<boardid>[0-9]+)/add/$', views.user_add)
]
