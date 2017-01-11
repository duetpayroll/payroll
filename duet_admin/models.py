from django.db import models
from django.contrib.auth.models import AbstractUser
from duet_admin.choices import DEPARTMENT_TYPE, GENDER
from django.core.urlresolvers import reverse

from autoslug import AutoSlugField


# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=10, verbose_name='Code', null=True)
    acronym = models.CharField(max_length = 10, null = True, verbose_name = 'Acronym')
    description = models.TextField(null=True, blank = True, verbose_name='Description')
    type = models.CharField(max_length=2, choices=DEPARTMENT_TYPE, verbose_name = 'Type')
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, default=None)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('duet_admin:department-list')


class User(AbstractUser):
    address = models.TextField(blank=True, null = True, verbose_name = 'Address')
    
    gender = models.CharField(max_length=1, choices=GENDER, default='m', verbose_name="Gender")
    dob = models.DateField(verbose_name= 'Date of Birth')
    image = models.FileField(upload_to='photos', null = True, blank= True)
    contact = models.CharField(verbose_name='Contact', max_length = 20, null= True, blank= True)

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    department = models.ForeignKey(Department, verbose_name='Department', on_delete=models.PROTECT)
    slug = AutoSlugField(populate_from='first_name', unique=True, always_update=True, default=None)

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('duet_admin:employee-list')


class Settings(models.Model):
    name = models.CharField(verbose_name='Name', max_length=50)
    code = models.CharField(verbose_name='Code', max_length=20, unique=True)
    value = models.IntegerField(verbose_name='Value')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('duet_admin:setting-list')

