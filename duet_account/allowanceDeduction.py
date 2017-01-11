from django.shortcuts import render, redirect
from django.views.generic import  DetailView, View
from django.core.urlresolvers import reverse_lazy

from .forms import EmployeeAllowanceDeductionForm, AllowanceDeductionEmployeeClassValueForm, ConfigureAllowanceDeductionForm

from employee.models import Employee
from .models import AllowanceDeduction, EmployeeAllowanceDeduction, EmployeeClass, AllowanceDeductionEmployeeClassValue

from duet_admin.utils import LoginAndAccountantRequired, CustomTableView, CustomUpdateView


class AllowanceDeductionList(LoginAndAccountantRequired, CustomTableView):
	model = AllowanceDeduction
	template_name = 'duet_account/list.html'

	exclude=['id', 'code', 'description', 'order', 'created_at', 'modified_at', 'slug']
	filter_fields = {
		'name' : ['icontains'],
		'category': ['exact'],
	}
	title = 'Pay, Allowances and Deductions List'
	actions = [ 
		{'url' : 'duet_account:allowance-deduction-detail', 'tooltip' : 'Detail', 'icon' : 'glyphicon glyphicon-th-large'},
		{'url' : 'duet_account:configure-allowance-deduction-employee-class', 'tooltip' : 'Configure Default Values', 'icon' : 'glyphicon glyphicon-cog'},
		{'url' : 'duet_account:allowance-deduction-update', 'tooltip' : 'Edit',  'icon' : 'glyphicon glyphicon-pencil'}
		]

	add_link = [
		{ 'url' : 'duet_account:configure-allowance-deduction', 'icon' : 'glyphicon glyphicon-cog'}
		]


class AllowanceDeductionDetail(LoginAndAccountantRequired, DetailView):
	model = AllowanceDeduction
	template_name = 'duet_account/allowanceDeduction/detail.html'
	context_object_name = 'allowanceDeduction'


class ConfigureEmployeeAllowanceDeduction(LoginAndAccountantRequired, View):
	template_name = 'duet_account/employee/allowanceDeduction/configure.html'

	def createFormset(self,request, allowance_deductions , prefix, employee): 
		formset = []
		employee_allowances = EmployeeAllowanceDeduction.objects.filter(employee = employee)
		for a in allowance_deductions:
			try:
				employee_allowance_deduction = employee_allowances.get(allowance_deduction = a)
			except EmployeeAllowanceDeduction.DoesNotExist:
				employee_allowance_deduction = EmployeeAllowanceDeduction()
			form = EmployeeAllowanceDeductionForm(request.POST or None, prefix = prefix +  str(a.id), instance = employee_allowance_deduction, allowance_deduction = a)
			formset.append(form)
		return formset

	def get(self, request, slug):
		employee = Employee.objects.get(slug = slug)
		allowance_deductions = AllowanceDeduction.objects.filter()
		allowances = allowance_deductions.exclude(category = 'd')
		deductions = allowance_deductions.filter(category = 'd')
		allowanace_formset = self.createFormset(request, allowances, 'allowance-', employee)
		deduction_formset  = self.createFormset(request, deductions, 'deduction-', employee)
		return render(request, self.template_name, {'employee' : employee, 'allowanace_formset' : allowanace_formset, 'deduction_formset' : deduction_formset})

	def post(self, request, slug):
		employee = Employee.objects.get(slug = slug)
		allowance_deductions = AllowanceDeduction.objects.filter()
		allowances = allowance_deductions.exclude(category = 'd')
		deductions = allowance_deductions.filter(category = 'd')
		allowanace_formset = self.createFormset(request, allowances, 'allowance-', employee)
		deduction_formset = self.createFormset(request, deductions, 'deduction-', employee)
		formset = allowanace_formset + deduction_formset
		for form in formset:
			if form.is_valid():
				instance = form.save(commit = False)
				instance.employee = employee
				instance.save()
		return redirect('duet_account:employee-detail', slug = employee.slug)


class AllowanceDeductionUpdate(LoginAndAccountantRequired, CustomUpdateView):
	model = AllowanceDeduction
	fields = [ 'description', 'is_percentage', 'is_applicable', 'payment_type']
	template_name = 'duet_account/create.html'
	success_url = reverse_lazy('duet_account:allowance-deduction-list')
	cancel_url = 'duet_account:allowance-deduction-list'
	title = 'Edit - '


class ConfigureAllowanceDeductionEmployeeClassValue(LoginAndAccountantRequired, View):
	def create_formset(self, request, employee_classes, allowance_deduction):
		formset = []
		allownace_deduction_employee_class_values = AllowanceDeductionEmployeeClassValue.objects.filter(allowance_deduction = allowance_deduction)
		for _class in employee_classes:
			try:
				allowance_deduction_class_value = allownace_deduction_employee_class_values.get(employee_class = _class)
			except AllowanceDeductionEmployeeClassValue.DoesNotExist:
				allowance_deduction_class_value = AllowanceDeductionEmployeeClassValue()
			initial = {'value' : allowance_deduction_class_value.value}
			form = AllowanceDeductionEmployeeClassValueForm(request.POST or None, prefix='employee-class-' + str(_class.id), instance=allowance_deduction_class_value, employee_class = _class, allowance_deduction = allowance_deduction, initial = initial)
			formset.append(form)
		return formset

	def get(self, request, slug):
		allowance_deduction = AllowanceDeduction.objects.get(slug = slug)
		employee_classes = EmployeeClass.objects.all()
		formset = self.create_formset(request, employee_classes, allowance_deduction)
		return render(request, 'duet_account/allowanceDeduction/configureAllowanceDeductionEmployeeClass.html',
					  {'allowanceDeduction' : allowance_deduction, 'formset' : formset})

	def post(self, request, slug):
		allowance_deduction = AllowanceDeduction.objects.get(slug = slug)
		employee_classes = EmployeeClass.objects.all()
		formset = self.create_formset(request, employee_classes, allowance_deduction)
		for form in formset:
			if form.is_valid():
				form.save()
		return redirect('duet_account:allowance-deduction-list')


class ConfigureAllowanceDeduction(LoginAndAccountantRequired, View):
	def createFormset(self,request, allowance_deductions , prefix): 
		formset = []
		for a in allowance_deductions:
			form = ConfigureAllowanceDeductionForm(request.POST or None, prefix = prefix +  str(a.id), instance = a)
			formset.append(form)
		return formset

	def get(self, request):
		allowance_deductions = AllowanceDeduction.objects.all()
		allowance_form_set = self.createFormset(request, allowance_deductions.exclude(category = 'd'), 'allowances')
		deduction_form_set = self.createFormset(request, allowance_deductions.filter(category = 'd'), 'deduction')
		return render(request, 'duet_account/allowanceDeduction/configure.html', {'allowanceFormSet' :
																				  allowance_form_set, 'deductionFormSet' : deduction_form_set})

	def post(self, request):
		allowance_deductions = AllowanceDeduction.objects.all()
		allowance_form_set = self.createFormset(request, allowance_deductions.exclude(category = 'd'), 'allowances')
		deduction_form_set = self.createFormset(request, allowance_deductions.filter(category = 'd'), 'deduction')
		formset = allowance_form_set + deduction_form_set
		for form in formset:
			if form.is_valid():
				form.save()
		return redirect('duet_account:allowance-deduction-list')