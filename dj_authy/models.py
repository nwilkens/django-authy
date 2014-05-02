# -*- coding: utf-8 -*-
from django.db import models
from django.db import IntegrityError
from django.contrib.auth.models import User

from jsonfield import JSONField
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from .services import AuthyService

import logging
logger = logging.getLogger('django.request')


class AuthyProfile(models.Model):
    user = models.OneToOneField('auth.User')
    authy_id = models.CharField(max_length=64, null=True, db_index=True)
    cellphone = PhoneNumberField(db_index=True, null=True)
    country = CountryField(null=True)
    is_smartphone = models.BooleanField(default=True)
    data = JSONField(default={})

    @property
    def service(self):
        return AuthyService(user=self.user, authy_profile=self)


def _get_or_create_authy_profile(user):
    # set the profile
    try:
        profile, is_new = AuthyProfile.objects.get_or_create(user=user)  # added like this so django noobs can see the result of get_or_create
        return (profile, is_new,)
    except IntegrityError as e:
        logger.critical('transaction.atomic() integrity error: %s' % e)
    return (None, None,)


# used to trigger profile creation by accidental reference. Rather use the _create_authy_profile def above
User.authy_profile = property(lambda u: _get_or_create_authy_profile(user=u)[0])