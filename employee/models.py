from django.db import models
from django.core.urlresolvers import reverse

from duet_account.models import EmployeeAllowanceDeduction, ProvidentFundProfile
from duet_admin.models import User

from autoslug import AutoSlugField

from duet_admin.choices import EMPLOYEE_CATEGORY


class Designation(models.Model):
    name = models.CharField(max_length=200, verbose_name = 'Name')
    description = models.TextField(null=True, blank = True, verbose_name = 'Description')

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, default=None)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('duet_admin:designation-list')


class Employee(User):
    tax_id_number = models.CharField(max_length=20, null= True, verbose_name= 'Tax ID')
    account_number = models.CharField(max_length=20, null= True, verbose_name= 'Account Number')
    joining_date = models.DateField(null= True, verbose_name="Joining Date")
    designation = models.ForeignKey(Designation, verbose_name='Designation', on_delete=models.PROTECT)
    grade = models.ForeignKey('duet_account.Grade', null=True, verbose_name='Grade', on_delete=models.PROTECT)
    category = models.CharField(max_length= 1, choices= EMPLOYEE_CATEGORY, verbose_name='Category', default = 't')
    allowance_deductions = models.ManyToManyField('duet_account.AllowanceDeduction', through='duet_account.EmployeeAllowanceDeduction')

    def _get_employee_class(self):
        return self.grade.employee_class;

    def _get_provident_fund_profile(self):
        try :
            provident_fund_profile = ProvidentFundProfile.objects.get(employee = self)
            return provident_fund_profile
        except ProvidentFundProfile.DoesNotExist:
            return None

    employee_class = property(_get_employee_class)

    def get_absolute_url(self):
        return reverse('duet_admin:employee-list')

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not ProvidentFundProfile.objects.filter(employee=self).exists():
            profile = ProvidentFundProfile(employee=self)
            profile.save()
