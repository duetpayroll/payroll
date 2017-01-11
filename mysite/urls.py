from django.conf.urls import url,include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^duet_admin/', include('duet_admin.urls', namespace = 'duet_admin')),
    url(r'^duet_account/', include('duet_account.urls', namespace = 'duet_account')),
    url(r'^', include('employee.urls')),
    url(r'^accounts/', include('allauth.urls')),
]

