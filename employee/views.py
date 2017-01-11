from django.views.generic import  DetailView, FormView, View
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.db.models import Sum

from duet_account.calculations import SalarySheetCalculations
from duet_account.homeLoan import HomeLoanOperations
from .models import Employee
from duet_account.models import EmployeeAllowanceDeduction, GPFAdvanceInstallment, MonthlyLogForGPF, GPFAdvance, \
	SalarySheet, HomeLoan, HomeLoanInstallment, AllowanceDeductionEmployeeClassValue

from braces.views import LoginRequiredMixin
from duet_account.salarySheet import SalarySheetDetail, SalarySheetQueryGeneration, SalarySheetOperations
from duet_account.providentFund import ProvidentFundAdvanceDetail, ProvidentFundOperations

from duet_admin.utils import CustomTableView, CustomUpdateView
from duet_account.forms import EmployeeSalarySheetQueryForm, GPFSummaryQueryForm


class EmployeeProfileUpdate(LoginRequiredMixin, CustomUpdateView):
	model = Employee
	fields = ['first_name', 'last_name', 'contact', 'address', 'tax_id_number', 'account_number']
	template_name = 'employee/employee/detail_form.html'
	cancel_url = 'employee-profile'
	title = 'Edit'

	def get_object(self, queryset=None):
		user = self.request.user
		return Employee.objects.get(user_ptr=user)

	def get_success_url(self):
		return reverse_lazy('employee-profile')


class EmployeeDetailBase(object):
	def get(self, request, *args, **kwargs):
		user = self.request.user
		self.employee = Employee.objects.get(user_ptr = user)
		return super().get(request, args, kwargs)


class EmployeeProfile(LoginRequiredMixin, DetailView):
	model = Employee
	template_name = 'employee/employee/detail.html'
	context_object_name = 'employee'

	def get(self, request, *args, **kwargs):
		user = self.request.user
		self.object = Employee.objects.get(user_ptr = user)
		context = self.get_context_data(object=self.object)
		return self.render_to_response(context)


class EmployeeSalaryList(LoginRequiredMixin, EmployeeDetailBase, CustomTableView):

	template_name = 'employee/employee/detail_list.html'
	model = SalarySheet
	fields = ['id', 'date', 'is_withdrawn', 'net_allowance', 'net_deduction', 'total_payment']
	filter_fields = {'id': ['icontains'], 'date': ['exact'], }
	title = 'Salary Sheet List'

	
	def get_queryset(self, **kwargs):
		qs = super().get_queryset(**kwargs)
		employee = self.employee
		return qs.filter(employee = employee, is_freezed = True)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

	actions = [
		{'url' : 'employee-salary-sheet-detail', 'icon' : 'glyphicon glyphicon-th-large', 'tooltip' : 'Detail', 'target': '_blank'},
		{'url': 'employee-salary-sheet-detail', 'icon': 'glyphicon glyphicon-download', 'tooltip': 'Download'},
	]


class EmployeeSalarySheetDetail(LoginRequiredMixin, SalarySheetDetail):
	template_name = 'employee/employee/salarySheet/detail.html'


class EmployeeAllowanceDeductionList(LoginRequiredMixin, View):
	template_name = 'employee/employee/detail_list.html'

	def create_entries(self, allowance_deductions, employee):
		employee_class = employee.employee_class
		allowance_deduction_employee_class_values = AllowanceDeductionEmployeeClassValue.objects.filter(
			employee_class=employee_class)
		provident_fund_profile = employee.providentfundprofile

		## loop employee's applicable allowancesDeductions
		entries = list()
		for a in allowance_deductions:
			entry = dict()
			allowance_deduction = a.allowance_deduction
			code = allowance_deduction.code
			is_percentage = allowance_deduction.is_percentage
			entry['name'] = allowance_deduction.name

			if code == 'gpf':
				entry['amount'] = SalarySheetCalculations.calculate_percentage_from_basic(self.employee_basic_pay, self.employee_personal_pay,
																					provident_fund_profile.percentage)
			elif code == 'h.loan':
				entry['amount'] = 'Variable'
			else:
				if a.value is not None:
					amount = SalarySheetCalculations.calculate_default_values(self.employee_basic_pay,
																						 self.employee_personal_pay,
																						 a.value, is_percentage)
				else:
					try:
						allowance_deduction_class_value = allowance_deduction_employee_class_values.get(
							allowance_deduction=allowance_deduction)
						amount = SalarySheetCalculations.calculate_default_values(self.employee_basic_pay,
																							 self.employee_personal_pay,
																							 allowance_deduction_class_value.value,
																							 is_percentage)
					except AllowanceDeductionEmployeeClassValue.DoesNotExist:
						amount = "Variable"
				entry['amount'] = amount
			entries.append(entry)
		return entries

	def get(self, request, *args, **kwargs):
		user = self.request.user
		employee = Employee.objects.get(user_ptr=user)
		employee_allowance_deductions = SalarySheetOperations.get_employee_allowance_deductions(employee)
		allowances = SalarySheetOperations.get_employee_applicable_allowances(employee_allowance_deductions)
		deductions = SalarySheetOperations.get_employee_applicable_deductions(employee_allowance_deductions)
		self.employee_basic_pay = SalarySheetOperations.get_employee_basic_pay(employee_allowance_deductions)
		self.employee_personal_pay = SalarySheetOperations.get_employee_personal_pay(employee_allowance_deductions)

		allowance_entries = self.create_entries( allowances, employee)
		deduction_entries = self.create_entries( deductions, employee)
		return render(request, 'employee/employee/allowanceDeduction/detail.html',
					  {'employee': employee, 'allowances': allowance_entries, 'deductions': deduction_entries})


########################################################### GPF  ##################################################

class EmployeeProvidentFundDetail(LoginRequiredMixin, CustomTableView):
	template_name = 'employee/employee/detail_list.html'
	actions = [{'url': 'employee-gpf-monthly-subscription-detail', 'icon': 'glyphicon glyphicon-th-large',
				'tooltip': 'Detail', 'target': '_blank'}, ]
	model = MonthlyLogForGPF
	title = 'GPF Montly Subscription Logs '

	exclude = ['id', 'provident_fund_profile']
	filter_fields = {'salary_sheet__date': ['exact'], }

	def get(self, request, *args, **kwargs):
		user = self.request.user
		employee = Employee.objects.get(user_ptr=user)
		self.provident_fund_profile = employee.providentfundprofile
		return super().get(request, args, kwargs)

	def get_queryset(self, **kwargs):
		qs = super().get_queryset(**kwargs)
		return qs.filter(provident_fund_profile=self.provident_fund_profile, salary_sheet__is_freezed=True)


class EmployeeProvidentFundMonthlySubscriptionDetail(LoginRequiredMixin, DetailView):
    model = MonthlyLogForGPF

    def get(self, request, *args, **kwargs):
        monthly_subscripion = self.get_object()
        salary_sheet = monthly_subscripion.salary_sheet
        return redirect('employee-salary-sheet-detail', pk=salary_sheet.pk)


class EmployeeProvidentFundAdvanceList(LoginRequiredMixin, CustomTableView):
	template_name = 'employee/employee/detail_list.html'

	model = GPFAdvance

	exclude = ['closing_date', 'provident_fund_profile', 'created_at', 'modified_at']

	title = 'General ProvidentFund Advance List'

	def get(self, request, *args, **kwargs):
		user = self.request.user
		employee = Employee.objects.get(user_ptr=user)
		self.provident_fund_profile = employee.providentfundprofile
		return super().get(request, args, kwargs)

	def get_queryset(self, **kwargs):
		qs = super().get_queryset(**kwargs)
		return qs.filter(provident_fund_profile=self.provident_fund_profile)

	actions = [
		{'url': 'employee-gpf-advance-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'View Detail'},
		{'url': 'employee-gpf-advance-detail-summary', 'icon': 'glyphicon glyphicon-book', 'target' : '_blank',
		 'tooltip': 'Summary'}]


class EmployeeGPFAdvanceInstalmentDetail(LoginRequiredMixin, DetailView):
    model = GPFAdvanceInstallment

    def get(self, request, *args, **kwargs):
        monthly_subscripion = self.get_object()
        salary_sheet = monthly_subscripion.salary_sheet
        return redirect('employee-salary-sheet-detail', pk=salary_sheet.pk)


class EmployeeProvidentFundAdvanceDetail(LoginRequiredMixin, ProvidentFundAdvanceDetail):
	template_name = 'employee/employee/providentFund/advance_detail.html'

	actions = [{'url': 'employee-gpf-advance-instalment-detail', 'icon': 'glyphicon glyphicon-th-large',
				'tooltip': 'View Details', 'target': '_blank'}]

	def get_queryset(self, **kwargs):
		qs = super().get_queryset(**kwargs)
		return qs.filter(gpf_advance=self.gpf_advance, salary_sheet__is_freezed = True)

########################################################### Home Loan  #################################################


class EmployeeHomeLoanList(LoginRequiredMixin, CustomTableView):
	template_name = 'employee/employee/detail_list.html'

	model = HomeLoan

	exclude = ['created_at', 'modified_at']

	title = 'Home Loan List'

	def get(self, request, *args, **kwargs):
		user = self.request.user
		self.employee = Employee.objects.get(user_ptr=user)
		return super().get(request, args, kwargs)

	def get_queryset(self, **kwargs):
		qs = super().get_queryset(**kwargs)
		return qs.filter(employee=self.employee)

	actions = [
		{'url': 'employee-home-loan-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'View Detail'},
		{'url': 'employee-home-loan-detail-summary', 'icon': 'glyphicon glyphicon-book', 'target': '_blank',
		 'tooltip': 'Summary'}]


class EmployeeHomeLoanDetail(LoginRequiredMixin, CustomTableView):
	model = HomeLoanInstallment
	template_name = 'employee/employee/homeLoan/advance_detail.html'

	exclude = ['id', 'gpf_advance']
	filter_fields = {'salary_sheet__date': ['exact'], }

	title = 'Installment List'

	def get(self, request, *args, **kwargs):
		self.home_loan = HomeLoan.objects.select_related('employee').get(
			pk=kwargs.pop('pk'))
		return super().get(request, args, kwargs)


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['home_loan'] = self.home_loan
		context['employee'] = self.home_loan.employee
		return context

	actions = [{'url': 'employee-home-loan-instalment-detail', 'icon': 'glyphicon glyphicon-th-large',
				'tooltip': 'View Details', 'target': '_blank'}]

	def get_queryset(self, **kwargs):
		qs = super().get_queryset(**kwargs)
		return qs.filter(home_loan=self.home_loan, salary_sheet__is_freezed = True)


class EmployeeHomeLoanInstalmentDetail(LoginRequiredMixin, DetailView):
	model = HomeLoanInstallment

	def get(self, request, *args, **kwargs):
		home_loan_installment = self.get_object()
		salary_sheet = home_loan_installment.salary_sheet
		return redirect('employee-salary-sheet-detail', pk=salary_sheet.pk)

########################################################### Query/Report ###############################################


class EmployeeSalarySheetQueryView(LoginRequiredMixin,EmployeeDetailBase, FormView):
	template_name = 'employee/employee/form_target_blank.html'
	form_class = EmployeeSalarySheetQueryForm
	query_template_name = 'report/query.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title']= 'Generate Salary Statement'
		return context

	def form_valid(self, form):
		user = self.request.user
		employee = Employee.objects.get(user_ptr=user)
		date_from = form.cleaned_data['date_from']
		date_to = form.cleaned_data['date_to']
		query_result = SalarySheetQueryGeneration.salary_sheet_employee(employee, date_from, date_to)
		return render(self.request, self.query_template_name, {'employee': employee,'details': query_result})


class EmployeeGPFAdvanceSummaryView(LoginRequiredMixin,EmployeeDetailBase, FormView):
	template_name = 'employee/employee/form_target_blank.html'
	form_class = EmployeeSalarySheetQueryForm
	query_template_name = 'report/query.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title']= 'Generate GPF Advance Summary'
		return context

	def form_valid(self, form):
		user = self.request.user
		employee = Employee.objects.get(user_ptr=user)
		date_from = form.cleaned_data['date_from']
		date_to = form.cleaned_data['date_to']
		query_result = ProvidentFundOperations.get_gpf_advance_summary_range(employee, date_from, date_to)
		return render(self.request, self.query_template_name, {'employee': employee, 'form': form, 'details': query_result})


class EmployeeGPFAdvanceDetailSummaryView(LoginRequiredMixin, DetailView):
	model = GPFAdvance
	query_template_name = 'report/query.html'

	def get(self, request, *args, **kwargs):
		gpf_advance = self.get_object()
		query_result = ProvidentFundOperations.get_gpf_advance_summary(gpf_advance)
		return render(self.request, self.query_template_name, {'details': query_result})


class EmployeeHomeLoanDetailSummaryView(LoginRequiredMixin, DetailView):
	model = HomeLoan
	query_template_name = 'report/query.html'

	def get(self, request, *args, **kwargs):
		home_loan = self.get_object()
		query_result = HomeLoanOperations.get_home_loan_summary(home_loan)
		return render(self.request, self.query_template_name, {'details': query_result})


class EmployeeGPFSummaryView(LoginRequiredMixin,EmployeeDetailBase, FormView):
	template_name = 'employee/employee/form_target_blank.html'
	form_class = GPFSummaryQueryForm
	query_template_name = "report/query.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title']= 'Generate GPF Summary'
		return context

	def form_valid(self, form):
		user = self.request.user
		employee = Employee.objects.get(user_ptr=user)
		provident_fund_profile = employee.providentfundprofile
		year_from = int(form.cleaned_data['year_from'])
		year_to = int(form.cleaned_data['year_to'])
		details = ProvidentFundOperations.get_gpf_yearly_details(employee, provident_fund_profile, year_from, year_to)
		return render(self.request, self.query_template_name, {'details': details, 'employee': employee})












