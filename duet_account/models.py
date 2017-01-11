from django.db import models
from django.db.models import Sum
from django.core.urlresolvers import reverse

from duet_admin.choices import PAYMENT_TYPE, ALLOWANCE_DEDUCTION_TYPE, EMPLOYEE_CLASS, ADVANCE_CATEGORY

from autoslug import AutoSlugField


class AllowanceDeduction(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    description = models.TextField(null=True, blank = True, verbose_name="Description")
    code = models.CharField(max_length = 10, verbose_name = "Code", unique=True, )
  
    category = models.CharField(max_length=2, choices=ALLOWANCE_DEDUCTION_TYPE, verbose_name="Type")
    value = models.ManyToManyField('EmployeeClass', through='AllowanceDeductionEmployeeClassValue')
    is_percentage = models.BooleanField(verbose_name="Percentage")
    is_applicable = models.BooleanField(verbose_name="Applicable")
    payment_type = models.CharField(max_length=2, choices=PAYMENT_TYPE, default='m', verbose_name="Payment Type")
    order = models.IntegerField(null= True, blank = True, verbose_name='Order')

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, default=None)

    class Meta:
    	ordering = ['order']
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('duet_admin:allowancededuction-list')


class EmployeeAllowanceDeduction(models.Model):
    value = models.DecimalField(verbose_name='Value', null=True, blank=True, decimal_places=2, max_digits=10)
    is_applicable = models.BooleanField(verbose_name='Applicable')
    employee = models.ForeignKey('employee.Employee', on_delete=models.PROTECT)
    allowance_deduction = models.ForeignKey( AllowanceDeduction, verbose_name='Name', on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    def __str__(self):
        return self.allowance_deduction.name

    class Meta:
        unique_together = ("employee", "allowance_deduction")
        ordering = ['allowance_deduction__order']
            

class SalarySheet(models.Model):
    employee = models.ForeignKey('employee.Employee', verbose_name= 'Employee')
    date = models.DateField(verbose_name = 'Month Ending')
    is_freezed = models.BooleanField(default=False, verbose_name= 'Freezed')
    is_withdrawn = models.BooleanField(default = True, verbose_name='Withdrawn')

    allowance_deductions = models.ManyToManyField(AllowanceDeduction, through='SalarySheetDetails')
    
    comment = models.TextField(null = True, blank = True)
    grade = models.ForeignKey('Grade', verbose_name='Grade', null=True)
    account_number = models.CharField(max_length=20, null= True, verbose_name= 'Account Number')
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    class Meta:
        ordering = ['-modified_at']
    
    def get_net_allowance(self):
        allowance = SalarySheetDetails.objects.filter(salary_sheet = self).exclude(allowance_deduction__category = 'd').aggregate(total=Sum("amount"))['total']
        if allowance is None:
            allowance = 0
        return allowance
    
    def get_net_deduction(self):
        deduction = SalarySheetDetails.objects.filter(salary_sheet = self, allowance_deduction__category = 'd').aggregate(total=Sum("amount"))['total']
        if deduction is None:
             deduction = 0
        try:
            gpf_subscription_deduction = MonthlyLogForGPF.objects.get(salary_sheet = self)
            deduction = deduction + gpf_subscription_deduction.deduction
        except MonthlyLogForGPF.DoesNotExist:
            pass

        gpf_advances_deduction = GPFAdvanceInstallment.objects.filter(salary_sheet=self).aggregate(total = Sum(
            "deduction"))['total']
        if gpf_advances_deduction is not None:
            deduction = deduction + gpf_advances_deduction

        try:
            home_loan_installment = HomeLoanInstallment.objects.get(salary_sheet= self)
            deduction += home_loan_installment.deduction
        except HomeLoanInstallment.DoesNotExist:
            pass

        return deduction

    def get_total_payment(self):
        return self.get_net_allowance() - self.get_net_deduction()

    def get_date(self):
        return self.date.strftime("%b") + ',' + str(self.date.year)

    net_allowance= property(get_net_allowance)
    net_deduction = property(get_net_deduction)
    total_payment = property(get_total_payment)

    def __str__(self):
        return 'Salary Sheet-' + str(self.id) + "-" + self.date.strftime("%b") + ',' + str(self.date.year)


class SalarySheetDetails(models.Model):
    salary_sheet = models.ForeignKey(SalarySheet, on_delete=models.CASCADE)
    allowance_deduction = models.ForeignKey(AllowanceDeduction, on_delete=models.PROTECT)
    amount = models.DecimalField(default = 0, decimal_places=2, max_digits=10)

    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    class Meta:
        ordering = ['allowance_deduction__order']


class EmployeeClass(models.Model):
    name = models.CharField(max_length= 50, verbose_name= 'Title')
    description = models.TextField(verbose_name = 'Description', null = True, blank = 'True')

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, default=None)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('duet_admin:employee-class-list')


class AllowanceDeductionEmployeeClassValue(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=10)
    allowance_deduction = models.ForeignKey(AllowanceDeduction)
    employee_class = models.ForeignKey(EmployeeClass)

    class Meta:
        unique_together = ("employee_class", "allowance_deduction")


class SalaryScale(models.Model):
    name = models.CharField(verbose_name='Name', max_length=50)
    date = models.DateField(verbose_name='Activated Date')
    is_active = models.BooleanField(verbose_name='Active', default=False)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, default=None)

    def __str__(self):
        return  self.name

    def get_absolute_url(self):
        return reverse('duet_admin:salary-scale-list')
    

class Grade(models.Model):
    salary_scale = models.ForeignKey('SalaryScale', on_delete=models.PROTECT)
    grade_no = models.IntegerField(verbose_name= 'Grade')
    description = models.TextField(verbose_name = 'Description', null = True, blank = 'True')
    employee_class = models.ForeignKey(EmployeeClass, verbose_name= 'Class')

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    slug = AutoSlugField(populate_from='grade_no', unique=True, always_update=True, default=None)

    def __str__(self):
        return 'Grade-' + str(self.grade_no)


class ProvidentFundProfile(models.Model):
    employee = models.OneToOneField('employee.Employee', on_delete=models.CASCADE, verbose_name='Employee')
    has_interest = models.BooleanField(verbose_name="Interest Taken", default=True)
    percentage = models.IntegerField(verbose_name='Percentage', default=0)

    def __str__(self):
        return 'GPF Profile of ' + self.employee.get_full_name()


class MonthlyLogForGPF(models.Model):
    salary_sheet = models.ForeignKey('duet_account.SalarySheet', verbose_name='Salary Sheet', on_delete= models.CASCADE)
    deduction = models.DecimalField(verbose_name= 'Deduction', default=0, decimal_places=2, max_digits=10)
    interest = models.DecimalField(verbose_name='Interest', default=0, decimal_places=2, max_digits=10)

    provident_fund_profile = models.ForeignKey(ProvidentFundProfile, verbose_name='Employee', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('duet_account:provident-fund-monthly-logs')

    class Meta:
        ordering = ['salary_sheet__date']


class YearlyLogForGPF(models.Model):
    date = models.DateField(verbose_name='Year Ending')
    net_deduction = models.DecimalField(verbose_name='Net Deduction', decimal_places= 2, default=0, max_digits=10)
    net_interest = models.DecimalField(verbose_name='Net Interest', default=0, decimal_places=2, max_digits=10)
    total_credit = models.DecimalField(verbose_name='Total', default=0, decimal_places=2, max_digits=10)
    is_freezed = models.BooleanField(verbose_name='Freezed', default=False)

    provident_fund_profile = models.ForeignKey(ProvidentFundProfile, verbose_name='Employee', on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    def __str__(self):
        return 'GPF Yearly Log - ' + str(self.id)


class GPFAdvance(models.Model):
    provident_fund_profile = models.ForeignKey(ProvidentFundProfile, verbose_name='Employee', on_delete=models.PROTECT)
    amount = models.DecimalField('Amount', decimal_places=2, default=0, max_digits=10)
    no_of_installments = models.IntegerField(verbose_name= 'No of Installments')
    monthly_payment = models.DecimalField(verbose_name='Monthly Payment', decimal_places=0, default=0, max_digits=10)
    date = models.DateField(verbose_name= 'Date')
    is_freezed = models.BooleanField(verbose_name='Freezed', default=False)
    is_closed = models.BooleanField(verbose_name='Closed', default= False)
    closing_date = models.DateField(verbose_name='Closing Date', null = True, blank = True)

    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now = True, verbose_name="Modified At")

    def _get_last_installment_number(self):
        last_installment = GPFAdvanceInstallment.objects.filter(gpf_advance = self).last()
        if last_installment is None:
            return 0
        return last_installment.installment_no

    def get_absolute_url(self):
        return reverse('duet_account:gpf-advance-list')

    def __str__(self):
        return 'GPF Advance - ' + str(self.id)


class GPFAdvanceInstallment(models.Model):
    gpf_advance = models.ForeignKey(GPFAdvance, verbose_name='GPF Advance', on_delete=models.PROTECT)
    installment_no = models.IntegerField(verbose_name='Install No.')
    deduction = models.DecimalField(verbose_name='Deduction', default=0, decimal_places=2, max_digits=10)
    interest = models.DecimalField(verbose_name='Interest', default=0, decimal_places=2, max_digits=10)

    salary_sheet = models.ForeignKey('duet_account.SalarySheet', verbose_name='Salary Sheet', on_delete= models.CASCADE)

    class Meta:
        ordering = ['installment_no']


class HomeLoan(models.Model):
    employee = models.ForeignKey('employee.Employee', verbose_name='Employee', on_delete=models.PROTECT)
    date = models.DateField(verbose_name='Date')
    amount = models.DecimalField('Amount', decimal_places=2, default=0, max_digits=10)
    no_of_installments = models.IntegerField(verbose_name='No of Installments')
    monthly_payment = models.DecimalField(verbose_name='Monthly Payment', decimal_places=0, default=0, max_digits=10)
    is_closed = models.BooleanField(verbose_name='Closed', default=False)
    is_freezed = models.BooleanField(verbose_name='Freezed', default=False)
    closing_date = models.DateField(verbose_name='Closing Date', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified At")

    def _get_last_installment_number(self):
        last_installment = HomeLoanInstallment.objects.filter(home_loan=self).last()
        if last_installment is None:
            return 0
        return last_installment.installment_no

    def get_absolute_url(self):
        return reverse('duet_account:home-loan-list')

    def __str__(self):
        return 'Home Loan - ' + str(self.id)


class HomeLoanInstallment(models.Model):
    home_loan = models.ForeignKey(HomeLoan, verbose_name='Home Loan', on_delete=models.PROTECT)
    installment_no = models.IntegerField(verbose_name='Install No.')
    deduction = models.DecimalField(verbose_name='Deduction', default=0, decimal_places=2, max_digits=10)

    salary_sheet = models.ForeignKey('duet_account.SalarySheet', verbose_name='Salary Sheet', on_delete=models.CASCADE)

    class Meta:
        ordering = ['installment_no']
