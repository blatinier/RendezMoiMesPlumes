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
#  Copyright (c) 2017 Benoît Latinier, Fabien Bourrel
#  This file is part of project: OnEstPasDesPigeons
#
import urllib.parse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils.translation import ugettext as _
from weights.forms import UserForm, ProfileForm, AddMeasureForm
from weights.models import Measure, MeasureFilter


def home(request):
    """
    Pretty home page.
    """
    return render(request, 'weights/home.html', {})


def about(request):
    """
    Everything about licensing/opensource/OpenFoodFacts...
    """
    return render(request, 'weights/about.html', {})


def register(request):
    """
    Register page.
    """
    if request.method == 'POST':
        user_form = UserForm(request.POST, prefix='user')
        profile_form = ProfileForm(request.POST, prefix='profile')
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()  # load the profile
            user.pigeonuser.language = profile_form.cleaned_data.get('language')
            user.pigeonuser.country = profile_form.cleaned_data.get('country')
            user.save()
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect(reverse(my_measures))
    else:
        user_form = UserForm(prefix='user')
        profile_form = ProfileForm(prefix='profile')
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'registration/register.html', context)


@login_required
def list_measures(request):
    """
    List of all measures with all possible manipulation
    we can imagine.
    """
    valid_sorts = {'user': 'user__user__username',
                   'product': 'product__product_name',
                   'pweight': 'package_weight',
                   'mweight': 'measured_weight'}
    default_sort_key = 'product'
    default_sort = 'product__product_name'
    sort_q = request.GET.get('order_by', default_sort_key)
    sort = valid_sorts.get(sort_q, default_sort)
    if request.GET.get('sort_order') == 'desc':
        sort = '-{}'.format(sort)

    page = request.GET.get('page', 1)
    items_per_page = request.GET.get('items_per_page', 2)
    measures_list = MeasureFilter(request.GET, queryset=Measure.objects.all())
    paginator = Paginator(measures_list.qs.order_by(sort), items_per_page)
    try:
        measures = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        measures = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        measures = paginator.page(paginator.num_pages)
    get_args = request.GET.dict()
    if 'order_by' in get_args:
        del get_args['order_by']
    if 'sort_order' in get_args:
        del get_args['sort_order']
    get_args = urllib.parse.urlencode(get_args)
    return render(request, 'weights/all_measures.html',
                  {'measures': measures,
                   'filter': measures_list,
                   'order_by': sort_q,
                   'sort_order': request.GET.get('sort_order'),
                   'get_args': get_args})


def overview(request):
    """
    Some global statistics with nice graphs.
    """
    # TODO #19
    return render(request, 'weights/overview.html', {})


@login_required
def user_account(request):
    """
    Everything about user managing his account.
    """
    # TODO #1
    return render(request, 'weights/user_account.html', {})


def contribute(request):
    """
    Page to explain how to crontibute.
    (e.g issu github, add measures, add products, ideas, ...)
    """
    return render(request, 'weights/contribute.html', {})


@login_required
def my_measures(request):
    """
    Page to list your own measurements.
    """
    measures = Measure.objects.filter(user=request.user.pigeonuser)
    return render(request, 'weights/my_measures.html',
                  {'measures': measures})


@login_required
def add_measure(request):
    """
    Page to add your own measurements.
    """
    if request.method == 'POST':
        measure_inst = Measure(user=request.user.pigeonuser)
        add_measure_form = AddMeasureForm(request.POST, request.FILES,
                                          instance=measure_inst)
        if add_measure_form.is_valid():
            add_measure_form.save()
            messages.success(request, _("Measure added!"))
            return redirect(reverse(my_measures))
        else:
            messages.error(request, _("Error in the form."))
    else:
        add_measure_form = AddMeasureForm()
    title = _('Add a measure')
    return render(request, 'weights/add_measure.html',
                  {'add_measure_form': add_measure_form,
                   'btn_text': _('Add!'),
                   'title': title})


@login_required
def edit_measure(request, measure_id):
    """
    Page to edit your own measurements.
    """
    measure = get_object_or_404(Measure, pk=measure_id)
    if measure.user != request.user.pigeonuser:
        return HttpResponseForbidden()
    if request.method == 'POST':
        add_measure_form = AddMeasureForm(request.POST, request.FILES,
                                          instance=measure)
        if add_measure_form.is_valid():
            add_measure_form.save()
            messages.success(request, _("Measure edited!"))
            return redirect(reverse(my_measures))
    add_measure_form = AddMeasureForm(instance=measure)
    title = _('Edit measure {measure_id}').format(measure_id=measure.id)
    return render(request, 'weights/add_measure.html',
                  {'add_measure_form': add_measure_form,
                   'btn_text': _('Edit'),
                   'title': title})


@login_required
def delete_measure(request, measure_id):
    """
    Page to delete your own measurements.
    """
    measure = get_object_or_404(Measure, pk=measure_id)
    if measure.user == request.user.pigeonuser:
        measure.delete()
        messages.success(request, _("Measure deleted!"))
    else:
        return HttpResponseForbidden()
    return redirect(reverse(my_measures))
