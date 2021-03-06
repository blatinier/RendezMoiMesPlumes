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
import os
import re
from functools import wraps

import django_filters
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext as _
import PIL.ExifTags
import PIL.Image

from utils.units import CONVERSIONS, convert_to_grams


def disable_for_loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw', False):
            return
        signal_handler(*args, **kwargs)
    return wrapper


def get_avatar_path(user, filename):
    return os.path.join('upload', 'avatar',
                        str(user.username), filename)


from django.contrib.auth.models import AbstractUser
class PigeonUser(AbstractUser):
    nickname = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True,
                               null=True)
    score = models.IntegerField(default=1)
    language = models.CharField(max_length=3, default="en")
    country = models.CharField(max_length=3, default="us")

    @property
    def avatar_or_anon(self):
        if self.avatar:
            return "/" + self.avatar.url
        else:
            return static('images/pigeon-anon.svg')

    @property
    def slug(self):
        return slugify(self.username)

    @property
    def pseudo(self):
        if self.nickname:
            return self.nickname
        else:
            return self.username



class Product(models.Model):
    """
    https://world.openfoodfacts.org/data/data-fields.txt
    """
    # models which source is from OFF and should be updated accordingly
    sourced_OFF_fields = ["url_OFF", "product_name", "generic_name",
                          "quantity", "packaging", "packaging_tags",
                          "brands", "brands_tags", "categories",
                          "categories_tags", "categories_fr", "labels",
                          "labels_tags", "labels_fr", "purchase_places",
                          "image_url"]

    # barcode, if it starts with "200" it's a OFF custom code provided
    # and barcode is not known yet
    code = models.CharField(max_length=64, db_index=True, primary_key=True)
    url_OFF = models.CharField(max_length=1024)
    product_name = models.CharField(max_length=512, db_index=True)
    generic_name = models.CharField(max_length=1024, db_index=True)
    quantity = models.CharField(max_length=512, blank=True, null=True)

    # shape, material
    packaging = models.CharField(max_length=512, blank=True, null=True)
    packaging_tags = models.CharField(max_length=512, blank=True, null=True)
    brands = models.CharField(max_length=512, blank=True, null=True)
    brands_tags = models.CharField(max_length=512, blank=True, null=True)
    categories = models.CharField(max_length=1024, blank=True, null=True)
    categories_tags = models.CharField(max_length=1024, blank=True, null=True)
    categories_fr = models.CharField(max_length=1024, blank=True, null=True)
    labels = models.CharField(max_length=1024, blank=True, null=True)
    labels_tags = models.CharField(max_length=1024, blank=True, null=True)
    labels_fr = models.CharField(max_length=1024, blank=True, null=True)
    purchase_places = models.CharField(max_length=256, blank=True, null=True)
    image_url = models.CharField(max_length=256, blank=True, null=True)

    # Is it OFF, ours, other?
    source = models.CharField(max_length=32, default="OpenFoodFacts")

    def __str__(self):
        if self.brands:
            return "{product_name} ({brands})".format(product_name=self.product_name,
                                                      brands=self.brands)
        return self.product_name

    def copy(self):
        """
        Dump all models
        """
        dump = {}
        for attr in self._data:
            dump[attr] = getattr(self, attr)
        return self.__class__(**dump)

    def update_with_OFF_product(self, product_off):
        """
        Parse OFF product (which is the same model) and update current
        product with
        """
        for field in self.sourced_OFF_fields:
            off_field = getattr(product_off, field)
            if off_field != getattr(self, field):
                setattr(self, field, off_field)

    @property
    def quantity_grams(self):
        return convert_to_grams(self.quantity)


def get_image_path(instance, filename):
    return os.path.join('upload', 'measures',
                        str(instance.user.username), filename)


class Measure(models.Model):
    user = models.ForeignKey(PigeonUser)
    product = models.ForeignKey(Product)
    package_weight = models.DecimalField(decimal_places=3, max_digits=12)
    measured_weight = models.DecimalField(decimal_places=3, max_digits=12)
    UNIT_CHOICES = (
        ('g', 'g'),
        ('oz', 'oz'),
    )
    unit = models.CharField(max_length=6, choices=UNIT_CHOICES, default='g')
    measure_image = models.ImageField(upload_to=get_image_path, blank=True,
                                      null=True)
    thumbnail = models.CharField(max_length=1024, blank=True,
                                 null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def weight(self, unit, weight_type="measured"):
        if weight_type == "measured":
            w = self.measured_weight
        else:
            w = self.package_weight
        if unit == self.unit:
            return w
        elif unit == 'g' and self.unit == 'oz':
            # Convert oz to g
            return w * CONVERSIONS["oz__g"]
        elif unit == 'oz' and self.unit == 'g':
            # Convert g to oz
            return w / CONVERSIONS["oz__g"]
        elif unit == 'kg':
            # return kg by requiring g conversion
            return self.weight('g', weight_type=weight_type) \
                    / CONVERSIONS["kg__g"]
        elif unit == 'lb':
            # return pounds by requiring oz conversion
            return self.weight('oz', weight_type=weight_type) \
                    / CONVERSIONS["lb__oz"]

    @property
    def percent_diff(self):
        return self.diff / self.package_weight * 100

    @property
    def diff(self):
        return self.measured_weight - self.package_weight

    @property
    def image_orientation(self):
        img = PIL.Image.open(os.path.join(settings.BASE_DIR,
                                          self.measure_image.url))
        if img.height > img.width:
            return "portrait"
        return "landscape"


class MeasureFilter(django_filters.FilterSet):

    class Meta:
        model = Measure
        fields = {
            'product__product_name': ['icontains'],
            'product__brands': ['icontains'],
            'user__username': ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        super(MeasureFilter, self).__init__(*args, **kwargs)
        self.filters['user__username__icontains'].label = _('Username')
        self.filters['product__product_name__icontains'].label = _('Product')
        self.filters['product__brands__icontains'].label = _('Brand')
