from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^overview$', views.overview, name='overview'),
    url(r'^about$', views.about, name='about'),
    url(r'^account$', views.user_account, name='user_account'),
    url(r'^contribute$', views.contribute, name='contribute'),
    url(r'^my_measures$', views.my_measures, name='my_measures'),
    url(r'^list_measures$', views.list_measures, name='list_measures'),
    url(r'^password_reset$', views.password_reset, name='password_reset'),
    url(r'^register$', views.register, name='register'),
]