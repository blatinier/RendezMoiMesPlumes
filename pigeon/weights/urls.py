# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Copyright (c) 2017 Benoit Latinier, Fabien Bourrel
#  This file is part of project: RendezMoiMesPlumes
#
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^overview$', views.overview, name='overview'),
    url(r'^about$', views.about, name='about'),
    url(r'^account$', views.user_account, name='user_account'),
    url(r'^privacy$', views.privacy, name='privacy'),
    url(r'^contact$', views.contact, name='contact'),
    url(r'^delete_account$', views.delete_account, name='delete_account'),
    url(r'^contribute$', views.contribute, name='contribute'),
    url(r'^my_measures$', views.my_measures, name='my_measures'),
    url(r'^add_measure$', views.add_measure, name='add_measure'),
    url(r'^edit_measure/(?P<measure_id>[0-9]+)$', views.edit_measure,
        name='edit_measure'),
    url(r'^delete_measure/(?P<measure_id>[0-9]+)$', views.delete_measure,
        name='delete_measure'),
    url(r'^list_measures$', views.list_measures, name='list_measures'),

    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<user>[0-9]+)/(?P<user_slug>[a-z0-9_-]+)$', views.user_page,
        name='user_page'),
    url(r'^product/(?P<code>[0-9]+)$', views.product_page,
        name='product_page'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^social/', include('social_django.urls', namespace='social')),
]
