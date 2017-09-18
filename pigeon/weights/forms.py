# -*- coding: utf-8 -*-
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
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _
from django_select2.forms import ModelSelect2Widget
from weights.models import PigeonUser, Product, Measure


LANGUAGE_CHOICES = (('en', 'en'), ('fr', 'fr'))
COUNTRY_CHOICES = (('us', 'us'), ('fr', 'fr'))


def file_size(value): # add this to some file where you can import it from
    limit_mib = 5
    limit = limit_mib * 1024 * 1024
    if value.size > limit:
        raise ValidationError(_('File too large. Size should not exceed %d MiB.') % limit_mib)


class ProfileForm(forms.ModelForm):
    nickname = forms.CharField(required=False)
    avatar = forms.ImageField(required=False, validators=[file_size])
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        model = PigeonUser
        fields = ('nickname', 'language', 'country', 'avatar')


class RegisterForm(UserCreationForm):
    class Meta:
        model = PigeonUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1',
                  'password2') + ProfileForm.Meta.fields


class UpdateUserForm(forms.ModelForm):

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"), required=False,
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        required=False,
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = PigeonUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1',
                  'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UpdateUserForm, self).save(commit=False)
        raw_password = self.cleaned_data['password1']
        if raw_password:
            user.set_password(raw_password)
        if commit:
            user.save()
        return user


class AddMeasureForm(forms.ModelForm):
    product = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                model=Product,
                search_fields=['product_name__icontains',
                               'brands__icontains'],
                attrs={"data-ajax--delay": 500},
                max_results=10,
            ),
            queryset=Product.objects.all(),
            required=False,
        )
    unit = forms.ChoiceField(choices=Measure.UNIT_CHOICES, initial='g')
    package_weight = forms.DecimalField(min_value=0, decimal_places=3)
    measured_weight = forms.DecimalField(min_value=0, decimal_places=3)
    measure_image = forms.ImageField(required=False, validators=[file_size])

    class Meta:
        model = Measure
        fields = ('product', 'package_weight', 'measured_weight',
                  'measure_image', 'unit')


class AddProductForm(forms.ModelForm):
    code = forms.CharField(required=False)
    product_name = forms.CharField(required=False)
    brands = forms.CharField(required=False)
    class Meta:
        model = Product
        fields = ('code', 'product_name', 'brands')

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")
        product_name = cleaned_data.get("product_name")
        brands = cleaned_data.get("brands")

        if not (code and product_name and brands):
            raise forms.ValidationError(_("All product fields must be set"),
                                        code='invalid')


class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    subject = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)
