"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.contrib import admin
from forecast.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', login, name='login'),
    url(r'^home/', home, name='home'),
    url(r'^home-filter/', homeFilter, name='home'),
    url(r'^upload/', upload, name='home'),
    url(r'^upload_file/', upload_file, name='upload_file'),
    url(r'^upload_file_svi/', upload_file_svi, name='upload_file_svi'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^check_login/', check_login, name='check_login'),
    url(r'^checkUpload/', checkUpload, name='checkUpload'),
    url(r'^report/', report, name='home'),
    url(r'^reportFilter/', reportFilter, name='home'),
    url(r'^removefile/', removefile, name='removefile'),
    url(r'^approve/', approve, name='svi'),
    url(r'^approve_pn/', approve_pn, name='approve_pn'),
    url(r'^svi-version/', svi_version, name='svi'),
    url(r'^create-svi/', create_svi, name='svi'),
    url(r'^view-svi/', view_svi, name='svi'),
    url(r'^api_get_forecast/', api_get_forecast, name='api_get_forecast'),
    url(r'^create_svi_version/', create_svi_version, name='create_svi_version'),
    url(r'^update_svi_version/', update_svi_version, name='update_svi_version'),
    url(r'^delete_svi/', delete_svi_version, name='svi'),
    url(r'^change_status_svi/', changeStatus, name='svi'),
    url(r'^view-approve/', view_approve, name='svi'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
