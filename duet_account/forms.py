from django import forms
from django.utils.dateformat import DateFormat

from .models import EmployeeAllowanceDeduction, AllowanceDeduction, SalarySheetDetails, SalarySheet, \
	AllowanceDeductionEmployeeClassValue, MonthlyLogForGPF, GPFAdvanceInstallment, YearlyLogForGPF, HomeLoanInstallment
from .calculations import SalarySheetCalculations
from datetime import datetime
from employee.models import Designation
from duet_admin.models import Department
from duet_account.models import EmployeeClass
from duet_admin.choices import EMPLOYEE_CATEGORY, REPORT_TYPE, YEAR_CHOICES


class SalarySheetDetailsEditForm(forms.ModelForm):
	amount = forms.DecimalField(label='')
	class Meta:
		model = SalarySheetDetails
		fields = ['amount', ]


class SalarySheetForm(forms.ModelForm):
	class Meta:
		model = SalarySheet
		fields = ['date', 'is_withdrawn','comment']
		widgets = {"date" : forms.DateInput(attrs={'class':'month-picker'})}

	def __init__(self, *args, **kwargs):
		super(SalarySheetForm, self).__init__(*args, **kwargs)
		today = DateFormat(datetime.today())
		today = today.format('Y-m-d')
		self.initial['date'] = today


class SalarySheetDetailsForm(forms.ModelForm):
	amount = forms.DecimalField(label='')
	class Meta:
		model = SalarySheetDetails
		fields = ['amount', ]

	def __init__(self, *args, **kwargs):
		self.allowance_deduction = kwargs.pop('allowance_deduction')
		self.title = self.allowance_deduction.name
		super().__init__(*args, **kwargs)

	def save(self, commit=True, **kwargs):
		instance = super().save(commit=False)
		salary_sheet = kwargs.pop('salary_sheet')
		instance.salary_sheet = salary_sheet
		instance.allowance_deduction = self.allowance_deduction
		if commit:
			instance.save()
		return instance


class EmployeeAllowanceDeductionForm(forms.ModelForm):

	is_applicable = forms.BooleanField(label = "", required = False)
	class Meta:
		model = EmployeeAllowanceDeduction
		fields =['is_applicable', 'value',]
		widgets = {"value": forms.NumberInput(attrs={'class': 'number-medium'})}


	def __init__(self, *args, **kwargs):
		self.allowance_deduction = kwargs.pop('allowance_deduction')
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		instance = super(EmployeeAllowanceDeductionForm, self).save(commit=False)
		instance.allowance_deduction = self.allowance_deduction
		if commit:
			instance.save()
		return instance
		

class AllowanceDeductionEmployeeClassValueForm(forms.ModelForm):
	class Meta:
		model = AllowanceDeductionEmployeeClassValue
		fields =['value']

	def __init__(self, *args, **kwargs):
		self.employee_class = kwargs.pop('employee_class')
		self.allowance_deduction = kwargs.pop('allowance_deduction')
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.employee_class = self.employee_class
		instance.allowance_deduction = self.allowance_deduction
		if commit:
			instance.save()
		return instance


class ConfigureAllowanceDeductionForm (forms.ModelForm):
	is_applicable = forms.BooleanField(label = "", required = False)
	order = forms.IntegerField(label = "", required= False)
	class Meta:
		model = AllowanceDeduction
		fields = ['is_applicable', 'order']


class MonthlyProvidentFundForm(forms.ModelForm):
	class Meta:
		model = MonthlyLogForGPF
		fields = ['deduction']

	def __init__(self, *args, **kwargs):
		if 'provident_fund_profile' in kwargs:
			self.provident_fund_profile = kwargs.pop('provident_fund_profile')
		self.title = "GPF"
		super().__init__(*args, **kwargs)

	def save(self, commit=True, **kwargs):
		instance = super().save(commit=False)
		salary_sheet = kwargs.pop('salary_sheet')
		instance.salary_sheet = salary_sheet
		if not instance.id:
			instance.provident_fund_profile = self.provident_fund_profile
		if instance.provident_fund_profile.has_interest:
			instance.interest = SalarySheetCalculations.calculate_gpf_interest(salary_sheet.date,
																			   instance.deduction)
		else:
			instance.interest = 0
		if commit:
			instance.save()
		return instance
			

class GPFAdvanceInslallmentForm(forms.ModelForm):
	class Meta:
		model = GPFAdvanceInstallment
		fields = ['installment_no', 'deduction']
		widgets = {"installment_no" : forms.NumberInput(attrs={'class':'number-small'}),
					"deduction" : forms.NumberInput(attrs={'class':'number-medium'})}

	def __init__(self, *args, **kwargs):
		self.gpf_advance = kwargs.pop('gpf_advance')
		self.title = "GPF Adv.-" + str(self.gpf_advance.id)
		super().__init__(*args, **kwargs)

	def save(self, commit=True, **kwargs):
		instance = super().save(commit=False)
		instance.gpf_advance = self.gpf_advance
		salary_sheet = kwargs.pop('salary_sheet')
		instance.salary_sheet = salary_sheet
		if self.gpf_advance.provident_fund_profile.has_interest:
			instance.interest = SalarySheetCalculations.calculate_gpf_interest(salary_sheet.date,
																	   instance.deduction)
		else:
			instance.interest = 0
		if commit:
			instance.save()
		return instance


class YearlyLogForGPFFormUpdate(forms.ModelForm):
	class Meta:
		model = YearlyLogForGPF
		fields = ['net_deduction', 'net_interest', 'total_credit']


class YearlyLogForGPFFormCreate(YearlyLogForGPFFormUpdate):
	def __init__(self, *args, **kwargs):
		self.provident_fund_profile = kwargs.pop('provident_fund_profile')
		self.title = "GPF Yearly Log"
		super().__init__(*args, **kwargs)

	def save(self, commit=True, **kwargs):
		instance = super().save(commit=False)
		instance.provident_fund_profile = self.provident_fund_profile
		today = datetime.today()
		instance.date = today.replace(day=1, month=7)
		if commit:
			instance.save()
		return instance


class HomeLoanInslallmentForm(forms.ModelForm):
	class Meta:
		model = HomeLoanInstallment
		fields = ['installment_no', 'deduction']
		widgets = {"installment_no" : forms.NumberInput(attrs={'class':'number-small'}),
					"deduction" : forms.NumberInput(attrs={'class':'number-medium'})}

	def __init__(self, *args, **kwargs):
		self.home_loan = kwargs.pop('home_loan')
		self.title = "Home Loan-" + str(self.home_loan.id)
		super().__init__(*args, **kwargs)

	def save(self, commit=True, **kwargs):
		instance = super().save(commit=False)
		instance.home_loan = self.home_loan
		salary_sheet = kwargs.pop('salary_sheet')
		instance.salary_sheet = salary_sheet
		if commit:
			instance.save()
		return instance


class SalarySheetAccountQueryForm(forms.Form):
	month = forms.DateField(label='Month', widget = forms.DateInput(attrs={'class': 'month-picker'}))
	designation = forms.ModelChoiceField(label="Designation", queryset=Designation.objects.all(), required=False)
	department = forms.ModelChoiceField(label="Department", queryset=Department.objects.all(), required=False)
	employee_class = forms.ModelChoiceField(label="Employee Class", queryset=EmployeeClass.objects.all(),required=False)
	employee_category = forms.ChoiceField(label="Category", choices=EMPLOYEE_CATEGORY, required=False)
	report_type = forms.ChoiceField(label="Report Type", choices= REPORT_TYPE)
	is_freezed = forms.BooleanField(label='Salary Sheet Freezed Only', required=False)


class SalarySheetAccountQueryFormRange(forms.Form):
	month_from = forms.DateField(label='Month From', widget = forms.DateInput(attrs={'class': 'month-picker'}))
	month_to = forms.DateField(label='Month To', widget = forms.DateInput(attrs={'class': 'month-picker'}))
	designation = forms.ModelChoiceField(label="Designation", queryset=Designation.objects.all(), required=False)
	department = forms.ModelChoiceField(label="Department", queryset=Department.objects.all(), required=False)
	employee_class = forms.ModelChoiceField(label="Employee Class", queryset=EmployeeClass.objects.all(),required=False)
	employee_category = forms.ChoiceField(label="Category", choices=EMPLOYEE_CATEGORY, required=False)
	report_type = forms.ChoiceField(label="Report Type", choices= REPORT_TYPE)


class EmployeeSalarySheetQueryForm(forms.Form):
	date_from = forms.DateField(label='From', widget = forms.DateInput(attrs={'class': 'month-picker'}))
	date_to = forms.DateField(label='To',  widget = forms.DateInput(attrs={'class': 'month-picker'}))


class GPFSummaryQueryForm(forms.Form):
	year_from = forms.TypedChoiceField(label='Year From', choices=YEAR_CHOICES)
	year_to = forms.TypedChoiceField(label='Year To', choices=YEAR_CHOICES)

	def __init__(self, *args, **kwargs):
		super(GPFSummaryQueryForm, self).__init__(*args, **kwargs)
		self.initial['year_from'] = datetime.now().year - 1
		self.initial['year_to'] = datetime.now().year



