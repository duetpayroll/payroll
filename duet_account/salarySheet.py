from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import DetailView, DeleteView, View, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.db.models import Sum

from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from duet_account.util import EmployeeQueryFormView
from .forms import SalarySheetDetailsForm, SalarySheetForm, SalarySheetAccountQueryForm, EmployeeSalarySheetQueryForm, \
    GPFSummaryQueryForm, MonthlyProvidentFundForm, GPFAdvanceInslallmentForm, HomeLoanInslallmentForm, \
    SalarySheetAccountQueryFormRange

from .calculations import SalarySheetCalculations

from employee.models import Employee
from .models import SalarySheetDetails, SalarySheet, AllowanceDeductionEmployeeClassValue, EmployeeAllowanceDeduction, \
    MonthlyLogForGPF, GPFAdvanceInstallment, AllowanceDeduction, ProvidentFundProfile, GPFAdvance, HomeLoan, \
    HomeLoanInstallment

from duet_admin.utils import CustomTableView, LoginAndAccountantRequired, ValueFromListTuple, DownloadPDF
from duet_admin.choices import REPORT_TYPE, EMPLOYEE_CATEGORY


class SalarySheetList(CustomTableView):
    model = SalarySheet
    template_name = 'duet_account/list.html'

    fields = ['id', 'date', 'is_freezed', 'is_withdrawn', 'net_allowance', 'net_deduction', 'total_payment']
    filter_fields = {'id': ['icontains'], 'date': ['exact'], }

    title = 'Salary Sheet List'

    actions = [{'url': 'duet_account:salary-sheet-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip':
        'Detail', 'target': '_blank'},
               {'url': 'duet_account:salary-sheet-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
               {'url': 'duet_account:salary-sheet-confirm', 'icon': 'glyphicon glyphicon-lock', 'tooltip': 'Freeze'},
               {'url': 'duet_account:salary-sheet-detail-pdf', 'icon': 'glyphicon glyphicon-download',
                'tooltip': 'Download'},
               {'url': 'duet_account:salary-sheet-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]


class EmployeeSalarySheetList(LoginAndAccountantRequired, SalarySheetList):
    template_name = 'duet_account/employee/detail_list.html'

    exclude = ['comment', 'employee']
    filter_fields = {'date': ['exact']}

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        employee = self.employee
        return qs.filter(employee=employee)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.employee
        context['employee'] = employee
        return context


class SalarySheetCreate(LoginAndAccountantRequired, View):

    def create_formset_home_loan(self, request, employee):
        formset = []
        try:
            home_loan = HomeLoan.objects.get(employee=employee, is_freezed=True, is_closed=False)
            installment_no = home_loan._get_last_installment_number() + 1;
            initial = {'deduction': home_loan.monthly_payment, 'installment_no': installment_no}
            home_loan_installment_form = HomeLoanInslallmentForm(request.POST or None, prefix='home_loan',
                                                                 instance=HomeLoanInstallment(), home_loan=home_loan,
                                                                 initial=initial)
            formset.append(home_loan_installment_form)
            return formset
        except HomeLoan.DoesNotExist:
            return formset

    def create_formset_gpf(self, request, employee, basic_pay, personal_pay):
        formset = []
        try:
            provident_fund_profile = ProvidentFundProfile.objects.get(employee=employee)
            deduction = SalarySheetCalculations.calculate_percentage_from_basic(basic_pay, personal_pay,
                                                                                provident_fund_profile.percentage)
            form = MonthlyProvidentFundForm(request.POST or None, prefix='gpf', instance=MonthlyLogForGPF(),
                                            provident_fund_profile=provident_fund_profile,
                                            initial={'deduction': deduction})
            formset.append(form)
            gpf_advances = GPFAdvance.objects.filter(provident_fund_profile=provident_fund_profile,
                                                     is_freezed=True, is_closed=False)
            count = 1
            for gpf_advance in gpf_advances:
                installment_no = gpf_advance._get_last_installment_number() + 1;
                initial = {'deduction': gpf_advance.monthly_payment, 'installment_no': installment_no}
                gpf_installment_form = GPFAdvanceInslallmentForm(request.POST or None,
                                                                 prefix='gpf_advance' + str(count),
                                                                 instance=GPFAdvanceInstallment(),
                                                                 gpf_advance=gpf_advance, initial=initial)
                formset.append(gpf_installment_form)
                count = count + 1
            return formset
        except ProvidentFundProfile.DoesNotExist:
            return formset

    def create_formset(self, request, allowance_deductions, prefix, employee):
        formset = []
        employee_class = employee.employee_class
        allowance_deduction_employee_class_values = AllowanceDeductionEmployeeClassValue.objects.filter(
            employee_class=employee_class)

        ## loop employee's applicable allowancesDeductions
        for a in allowance_deductions:
            initial = {'amount': 0}
            allowance_deduction = a.allowance_deduction
            code = allowance_deduction.code
            is_percentage = allowance_deduction.is_percentage

            if code == 'gpf':
                forms = self.create_formset_gpf(request, employee, self.employee_basic_pay,
                                                               self.employee_personal_pay)
                formset = formset + forms

            elif code == 'h.loan':
                forms = self.create_formset_home_loan(request, employee)
                formset = formset + forms

            else:
                if a.value:
                    initial['amount'] = SalarySheetCalculations.calculate_default_values(self.employee_basic_pay,
                                                                                         self.employee_personal_pay,
                                                                                         a.value, is_percentage)
                else:
                    try:
                        allowance_deduction_class_value = allowance_deduction_employee_class_values.get(
                            allowance_deduction=allowance_deduction)
                        initial['amount'] = SalarySheetCalculations.calculate_default_values(self.employee_basic_pay,
                                                                                             self.employee_personal_pay,
                                                                                             allowance_deduction_class_value.value,
                                                                                             is_percentage)
                    except AllowanceDeductionEmployeeClassValue.DoesNotExist:
                        pass
                form = SalarySheetDetailsForm(request.POST or None, prefix=prefix + str(a.id),
                                              instance=SalarySheetDetails(), allowance_deduction=allowance_deduction,
                                              initial=initial)
                formset.append(form)
        return formset

    def get(self, request, slug):
        employee = Employee.objects.get(slug=slug)

        employee_allowance_deductions = SalarySheetOperations.get_employee_allowance_deductions(employee)
        allowances = SalarySheetOperations.get_employee_applicable_allowances(employee_allowance_deductions)
        deductions = SalarySheetOperations.get_employee_applicable_deductions(employee_allowance_deductions)

        if SalarySheetOperations.check_employee_allowance_deduction_configurations(request,
                                                                                   employee_allowance_deductions) is False:
            return redirect('duet_account:configure-employee-allowance-deduction', slug=employee.slug)

        self.employee_basic_pay = SalarySheetOperations.get_employee_basic_pay(employee_allowance_deductions)
        self.employee_personal_pay = SalarySheetOperations.get_employee_personal_pay(employee_allowance_deductions)

        allowance_formset = self.create_formset(request, allowances, 'allowance-', employee)
        deduction_formset = self.create_formset(request, deductions, 'deduction-', employee)
        salarySheetForm = SalarySheetForm(instance=SalarySheet())

        return render(request, 'duet_account/employee/salarySheet/generate_salary_sheet.html',
                      {'salary_sheet_form': salarySheetForm, 'employee': employee,
                       'allowanace_formset': allowance_formset, 'deduction_formset': deduction_formset})

    def post(self, request, slug):
        employee = Employee.objects.select_related('grade').get(slug=slug)

        employee_allowance_deductions = SalarySheetOperations.get_employee_allowance_deductions(employee)
        allowances = SalarySheetOperations.get_employee_applicable_allowances(employee_allowance_deductions)
        deductions = SalarySheetOperations.get_employee_applicable_deductions(employee_allowance_deductions)
        if SalarySheetOperations.check_employee_allowance_deduction_configurations(request,
                                                                                   employee_allowance_deductions) is False:
            return redirect('duet_account:employee-detail', slug=employee.slug)

        self.employee_basic_pay = SalarySheetOperations.get_employee_basic_pay(employee_allowance_deductions)
        self.employee_personal_pay = SalarySheetOperations.get_employee_personal_pay(employee_allowance_deductions)
        allowance_formset = self.create_formset(request, allowances, 'allowance-', employee)
        deduction_formset = self.create_formset(request, deductions, 'deduction-', employee)

        salary_sheet_form = SalarySheetForm(request.POST, instance=SalarySheet())

        formset = allowance_formset + deduction_formset

        if salary_sheet_form.is_valid():
            salary_sheet = salary_sheet_form.save(commit=False)
            salary_sheet.employee = employee
            salary_sheet.account_number = employee.account_number
            salary_sheet.grade = employee.grade
            salary_sheet.save()
            for form in formset:
                instance = form.save(commit=False, salary_sheet=salary_sheet)
                instance.save()
            return redirect('duet_account:salary-sheet-detail-employee-base', pk=salary_sheet.pk)
        return render(request, 'duet_account/employee/salarySheet/generate_salary_sheet.html',
                      {'salary_sheet_form': salary_sheet_form, 'employee': employee,
                       'allowanace_formset': allowance_formset, 'deduction_formset': deduction_formset})


class SalarySheetUpdate(LoginAndAccountantRequired, View):
    def update_formset_home_loan(self, request, salary_sheet):
        formset = []
        try:
            home_loan_installment = HomeLoanInstallment.objects.select_related('home_loan').get(
                salary_sheet=salary_sheet)
            home_loan_installment_form = HomeLoanInslallmentForm(request.POST or None, prefix='home_loan',
                                                                 instance=home_loan_installment,
                                                                 home_loan=home_loan_installment.home_loan)
            formset.append(home_loan_installment_form)
            return formset
        except HomeLoanInstallment.DoesNotExist:
            return formset

    def update_formset_gpf(self, request, salary_sheet):
        formset = []
        try:
            monthly_log = MonthlyLogForGPF.objects.get(salary_sheet=salary_sheet)
            form = MonthlyProvidentFundForm(request.POST or None, prefix='gpf', instance=monthly_log)
            formset.append(form)
        except MonthlyLogForGPF.DoesNotExist:
            pass

        gpf_advance_installments = GPFAdvanceInstallment.objects.filter(salary_sheet=salary_sheet)
        for gpf_advance_installment in gpf_advance_installments:
            gpf_installment_form = GPFAdvanceInslallmentForm(request.POST or None,
                                                             prefix='gpf_advance' + str(gpf_advance_installment.id),
                                                             instance=gpf_advance_installment,
                                                             gpf_advance=gpf_advance_installment.gpf_advance)
            formset.append(gpf_installment_form)
        return formset

    def update_formset(self, request, allowance_deductions, prefix, employee):
        formset = []
        for a in allowance_deductions:
            initial = {'amount': a.amount}
            form = SalarySheetDetailsForm(request.POST or None, prefix=prefix + str(a.id), instance=a,
                                          allowance_deduction=a.allowance_deduction, initial=initial)
            formset.append(form)
        return formset

    def get(self, request, pk):
        salary_sheet = SalarySheet.objects.get(pk=pk)
        employee = salary_sheet.employee
        if salary_sheet.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': employee})

        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet=salary_sheet)
        allowances = salary_sheet_details.exclude(allowance_deduction__category='d')
        deductions = salary_sheet_details.filter(allowance_deduction__category='d')

        gpf_formset = self.update_formset_gpf(request, salary_sheet)
        home_loan_formset = self.update_formset_home_loan(request, salary_sheet)
        allowanace_formset = self.update_formset(request, allowances, 'allowance-', employee)
        deduction_formset = self.update_formset(request, deductions, 'deduction-', employee)

        deduction_formset = gpf_formset + home_loan_formset + deduction_formset

        salary_sheet_form = SalarySheetForm(instance=salary_sheet)
        return render(request, 'duet_account/employee/salarySheet/generate_salary_sheet.html',
                      {'salary_sheet_form': salary_sheet_form, 'employee': employee,
                       'allowanace_formset': allowanace_formset, 'deduction_formset': deduction_formset})

    def post(self, request, pk):
        salary_sheet = SalarySheet.objects.get(pk=pk)
        employee = salary_sheet.employee
        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet=salary_sheet)

        gpf_formset = self.update_formset_gpf(request, salary_sheet)
        allowances = salary_sheet_details.exclude(allowance_deduction__category='d')
        deductions = salary_sheet_details.filter(allowance_deduction__category='d')

        allowance_formset = self.update_formset(request, allowances, 'allowance-', employee)
        home_loan_formset = self.update_formset_home_loan(request, salary_sheet)
        deduction_formset = gpf_formset + home_loan_formset + self.update_formset(request, deductions, 'deduction-',
                                                                                 employee)


        formset = allowance_formset + deduction_formset

        salary_sheet_form = SalarySheetForm(request.POST, instance=salary_sheet)

        if salary_sheet_form.is_valid():
            salary_sheet_form.save()
            for form in formset:
                instance = form.save(salary_sheet=salary_sheet)
            return redirect('duet_account:salary-sheet-detail', pk=salary_sheet.pk)
        return render(request, 'duet_account/employee/salarySheet/generate_salary_sheet.html',
                      {'salary_sheet_form': salary_sheet_form, 'employee': employee,
                       'allowanace_formset': allowance_formset, 'deduction_formset': deduction_formset})


class SalarySheetDetail(DetailView):
    model = SalarySheet

    def get_gpf_deductions(self, salary_sheet):
        gpf_details = dict()
        deduction = 0
        try:
            monthly_log = MonthlyLogForGPF.objects.get(salary_sheet=salary_sheet)
            gpf_details['gpf_subscription'] = monthly_log
            deduction = monthly_log.deduction
        except MonthlyLogForGPF.DoesNotExist:
            pass
        gpf_advance_installments = GPFAdvanceInstallment.objects.filter(salary_sheet=salary_sheet)
        gpf_advance_deductions = gpf_advance_installments.aggregate(total=Sum("deduction"))['total']
        if gpf_advance_deductions is None:
            gpf_advance_deductions = 0
        gpf_details['gpf_advance_installments'] = gpf_advance_installments
        gpf_details['total_gpf_deduction'] = gpf_advance_deductions + deduction
        return gpf_details

    def get_home_loan(self, salary_sheet):
        try:
            return HomeLoanInstallment.objects.select_related('home_loan').get(salary_sheet=salary_sheet)
        except HomeLoanInstallment.DoesNotExist:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        salary_sheet = self.object
        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet=salary_sheet)
        allowances = salary_sheet_details.exclude(allowance_deduction__category='d')
        deductions = salary_sheet_details.filter(allowance_deduction__category='d')
        gpf_details = self.get_gpf_deductions(salary_sheet)
        context['home_loan_installment'] = self.get_home_loan(salary_sheet)
        context['allowances'] = allowances
        context['deductions'] = deductions
        context['gpf_details'] = gpf_details
        employee = salary_sheet.employee
        context['employee'] = employee
        context['employee_grade'] = employee.grade
        return context


class AccountSalarySheetDetail(LoginAndAccountantRequired, SalarySheetDetail):
    template_name = 'duet_account/employee/salarySheet/detail.html'


class SalarySheetDetailPdf(LoginRequiredMixin, SalarySheetDetail):
    template_name = 'duet_account/employee/salarySheet/detail.html'
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        file_name = 'payslip-' + str(self.object.id)
        return DownloadPDF.downloadPdf(request, context, self.template_name, file_name)


class AccountSalarySheetDetailEmployeeBase(LoginAndAccountantRequired, SalarySheetDetail):
    template_name = 'duet_account/employee/salarySheet/employee_base_detail.html'

class SalarySheetDelete(LoginAndAccountantRequired, DeleteView):
    model = SalarySheet
    template_name = 'duet_account/employee/confirm_delete.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.employee = self.object.employee
        if self.object.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': self.employee})
        request.session['employee_slug'] = self.employee.slug
        return super().get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def post(self, request, *args, **kwargs):
        employee_slug = request.session['employee_slug']
        del request.session['employee_slug']
        self.success_url = reverse_lazy('duet_account:employee-detail', kwargs={'slug': employee_slug})
        return super().post(request, args, kwargs)


class SalarySheetConfirm(LoginAndAccountantRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = SalarySheet
    template_name = 'duet_account/employee/salarySheet/confirm.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.employee = self.object.employee
        if self.object.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': self.employee})
        return super().get(request, args, kwargs)

    def post(self, *args, **kwargs):
        salary_sheet = self.get_object()
        salary_sheet.is_freezed = True
        salary_sheet.save()
        return redirect('duet_account:employee-detail', slug=salary_sheet.employee.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class SalarySheetQuerySummaryAndDetailsView(LoginAndAccountantRequired, FormView):
    template_name = 'duet_account/form_target_blank.html'
    form_class = SalarySheetAccountQueryForm
    query_template_name = "report/query.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate Salary Statement For'
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        date = data['month']
        designation = data['designation']
        department = data['department']
        employee_class = data['employee_class']
        employee_category = data['employee_category']
        html_head = "Salary Statement of " + date.strftime("%b") + ", " + str(date.year)
        salary_sheets = SalarySheet.objects.select_related('employee', 'employee__department', 'employee__department',
                                                           'employee__grade__employee_class').filter(
            date__month=date.month, date__year=date.year).order_by('employee__grade__grade_no',
                                                                   'employee__department__name')
        html_extra = ""
        if designation is not None:
            salary_sheets = salary_sheets.filter(employee__designation=designation)
            html_extra += "Designation: " + designation.name + ", "
        if department is not None:
            salary_sheets = salary_sheets.filter(employee__department=department)
            html_extra += "Department: " + department.acronym + ", "
        if employee_class is not None:
            salary_sheets = salary_sheets.filter(employee__grade__employee_class=employee_class)
            html_extra += "Employee Class: " + employee_class.name + ", "
        if employee_category is not "":
            salary_sheets = salary_sheets.filter(employee__category=employee_category)
            html_extra += "Employee Category: " + ValueFromListTuple.get(EMPLOYEE_CATEGORY, employee_category) + ", "
        if data['is_freezed'] is True:
            salary_sheets = salary_sheets.filter(is_freezed=True)
            html_extra += "Only Freezed Salary Sheets, "

        report_type = data['report_type']
        html_extra += "Report Type: " + ValueFromListTuple.get(REPORT_TYPE, report_type)
        if report_type is 'd':
            query_result = SalarySheetQueryGeneration.get_salary_sheet_all_details(salary_sheets)
        else:
            query_result = SalarySheetQueryGeneration.get_salary_sheet_all_summary(salary_sheets)

        html = query_result['html']
        html['extra'] = html_extra
        html['title'] = html_head
        return render(self.request, self.query_template_name, {'details': query_result})


class SalarySheetQuerySummaryAndDetailsRangeView(LoginAndAccountantRequired, FormView):
    template_name = 'duet_account/form_target_blank.html'
    form_class = SalarySheetAccountQueryFormRange
    query_template_name = "report/query.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate Salary Statement For'
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        from_date = data['month_from']
        to_date = data['month_to']
        designation = data['designation']
        department = data['department']
        employee_class = data['employee_class']
        employee_category = data['employee_category']
        html_head = "Salary Statement (" + from_date.strftime("%b") + ", " + str(from_date.year) + " - " + \
                    to_date.strftime("%b") + ", " + str(to_date.year) + ")"
        salary_sheets = SalarySheet.objects.filter(is_freezed=True, date__gte=from_date, date__lte=to_date)
        employees = Employee.objects.select_related('designation', 'department', 'providentfundprofile', 'grade__employee_class'
                                                    ).all().order_by(
            'grade__grade_no', 'dob', 'department__name')
        html_extra = ""
        if designation is not None:
            employees = employees.filter(designation=designation)
            html_extra += "Designation: " + designation.name + ", "
        if department is not None:
            employees = employees.filter(department=department)
            html_extra += "Department: " + department.acronym + ", "
        if employee_class is not None:
            employees = employees.filter(grade__employee_class=employee_class)
            html_extra += "Employee Class: " + employee_class.name + ", "
        if employee_category is not "":
            employees = employees.filter(category=employee_category)
            html_extra += "Employee Category: " + ValueFromListTuple.get(EMPLOYEE_CATEGORY, employee_category) + ", "
        salary_sheets = salary_sheets.filter(employee__in=employees)

        report_type = data['report_type']
        html_extra += "Report Type: " + ValueFromListTuple.get(REPORT_TYPE, report_type)
        if report_type is 'd':
            query_result = SalarySheetQueryGeneration.get_salary_sheet_all_details_range(salary_sheets, employees)
        else:
            query_result = SalarySheetQueryGeneration.get_salary_sheet_all_summary_range(salary_sheets, employees)

        html = query_result['html']
        html['extra'] = html_extra
        html['title'] = html_head
        return render(self.request, self.query_template_name, {'details': query_result})


class SalarySheetQueryView(EmployeeQueryFormView):
    template_name = 'duet_account/employee/form_target_blank.html'
    form_class = EmployeeSalarySheetQueryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate Salary Statement'
        return context

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']
        query_result = SalarySheetQueryGeneration.salary_sheet_employee(self.employee, date_from, date_to)
        return render(self.request, self.query_template_name, {'employee': self.employee, 'details': query_result})


class SalarySheetOperations:
    @staticmethod
    def get_employee_allowance_deductions(employee):
        return EmployeeAllowanceDeduction.objects.filter(employee=employee)

    @staticmethod
    def get_employee_applicable_allowances(allowance_deductions):
        return allowance_deductions.filter(is_applicable=True, allowance_deduction__is_applicable=True).exclude(
            allowance_deduction__category='d')

    @staticmethod
    def get_employee_applicable_deductions(allowance_deductions):
        return allowance_deductions.filter(allowance_deduction__category='d', is_applicable=True,
                                           allowance_deduction__is_applicable=True)

    @staticmethod
    def get_employee_basic_pay(allowance_deductions):
        return allowance_deductions.get(allowance_deduction__code='bp').value

    @staticmethod
    def get_employee_personal_pay(allowance_deductions):
        return allowance_deductions.get(allowance_deduction__code='pp').value

    @staticmethod
    def check_employee_allowance_deduction_configurations(request, allowance_deductions):
        def send_message():
            messages.error(request, "Basic Pay/Personal Pay Not Defined")

        try:
            basic_pay = allowance_deductions.get(allowance_deduction__code='bp')
            if basic_pay.value is None:
                send_message()
                return False
        except EmployeeAllowanceDeduction.DoesNotExist:
            send_message()
            return False
        try:
            personal_pay = allowance_deductions.get(allowance_deduction__code='pp')
            if personal_pay is None:
                send_message()
                return False
        except EmployeeAllowanceDeduction.DoesNotExist:
            send_message()
            return False

        return True


class SalarySheetQueryGeneration(object):
    @staticmethod
    def check_total(total):
        if total is None:
            return 0
        return total

    @staticmethod
    def check_none(ob):
        if ob is None:
            return ""
        return ob

    @staticmethod
    def get_allowance_deductions_total(salary_sheet_details, a):
        return SalarySheetQueryGeneration.check_total(
            salary_sheet_details.filter(allowance_deduction=a).aggregate(total=Sum('amount'))['total'])

    @staticmethod
    def get_allowance_deductions_amount(salary_sheet_details, salary_sheet, a):
        try:
            return salary_sheet_details.get(salary_sheet=salary_sheet, allowance_deduction=a).amount
        except SalarySheetDetails.DoesNotExist:
            return 0

    @staticmethod
    def get_net_allowance(salary_sheet_details, salary_sheet):
        allowance = \
        salary_sheet_details.filter(salary_sheet=salary_sheet).exclude(allowance_deduction__category='d').aggregate(
            total=Sum("amount"))['total']
        if allowance is None:
            allowance = 0
        return allowance

    @staticmethod
    def get_net_deduction(salary_sheet_details, gpf_subscriptions, gpf_advance_installments, salary_sheet):
        deduction = salary_sheet_details.filter(salary_sheet=salary_sheet, allowance_deduction__category='d').aggregate(
            total=Sum("amount"))['total']
        if deduction is None:
            deduction = 0
        try:
            gpf_subscription_deduction = gpf_subscriptions.get(salary_sheet=salary_sheet)
            deduction = deduction + gpf_subscription_deduction.deduction
        except MonthlyLogForGPF.DoesNotExist:
            pass

        gpf_advances_deduction = \
        gpf_advance_installments.filter(salary_sheet=salary_sheet).aggregate(total=Sum("deduction"))['total']
        if gpf_advances_deduction is not None:
            deduction = deduction + gpf_advances_deduction
        try:
            home_loan_installment = HomeLoanInstallment.objects.get(salary_sheet= salary_sheet)
            deduction += home_loan_installment.deduction
        except HomeLoanInstallment.DoesNotExist:
            pass
        return deduction

    @staticmethod
    def get_net_allowance_range(salary_sheet_details):
        allowance = salary_sheet_details.exclude(allowance_deduction__category='d').aggregate(total=Sum("amount"))['total']
        if allowance is None:
            allowance = 0
        return allowance

    @staticmethod
    def get_net_deduction_range(salary_sheet_details, gpf_subscriptions, gpf_advance_installments,
                                home_loan_installments):
        deduction = SalarySheetQueryGeneration.check_total(salary_sheet_details.filter(
            allowance_deduction__category='d').aggregate(
            total=Sum("amount"))['total'])

        gpf_subscription_deduction = SalarySheetQueryGeneration.check_total(gpf_subscriptions.aggregate(total=Sum(
            "deduction"))['total'])
        deduction += gpf_subscription_deduction

        gpf_advances_deduction = SalarySheetQueryGeneration.check_total(gpf_advance_installments.aggregate(total=Sum(
            "deduction"))['total'])
        deduction += gpf_advances_deduction

        home_loan_installment_deductions =SalarySheetQueryGeneration.check_total(home_loan_installments.aggregate(total=Sum(
        "deduction"))['total'])
        deduction += home_loan_installment_deductions

        return deduction

    @staticmethod
    def get_salary_sheet_all_summary(salary_sheets):
        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet__in=salary_sheets)
        gpf_deductions = MonthlyLogForGPF.objects.filter(salary_sheet__in=salary_sheets)
        gpf_advance_installments = GPFAdvanceInstallment.objects.filter(salary_sheet__in=salary_sheets)

        html_body = "<table class='table table table-condensed table-striped table-bordered'>"
        html_body += "<thead class='thead'><tr><th style='min-width: 150px' class='text-center'>Employee Name" \
                "</th><th style='min-width: 100px' class='text-center' rowspan='2'>Designation </th><th " \
                "style='min-width: 70px' class='text-center'>Department </th><th style='min-width: 50px' " \
                "class='text-center'>Account no.</th><th class='text-center'>Net Pay</th></tr>"

        html_body += "</thead><tbody>"

        total_payment = 0
        for salary_sheet in salary_sheets:
            html_body += "<tr>"
            name = salary_sheet.employee.get_full_name()
            html_body += "<th class='name'>" + name + "</th>"
            html_body += "<td class='designation'>" + salary_sheet.employee.designation.name + "</td>"
            html_body += "<td class='department'>" + salary_sheet.employee.department.acronym + "</td>"
            html_body += "<td class='account-number'>" + SalarySheetQueryGeneration.check_none(
                salary_sheet.employee.account_number) + "</td>"
            net_allowance = SalarySheetQueryGeneration.get_net_allowance(salary_sheet_details, salary_sheet)
            net_deduction = SalarySheetQueryGeneration.get_net_deduction(salary_sheet_details, gpf_deductions,
                                                                         gpf_advance_installments, salary_sheet)
            salary_total_payment = net_allowance - net_deduction
            html_body += "<td class='text-right net-pay'>" + str(salary_total_payment) + "</td>"
            html_body += "</tr>"
            total_payment += salary_total_payment

        html_body += "</tbody><tfoot class='tfoot'><tr><th class='total'>Total</th><td></td><td></td><td></td>"

        html_body += "<th class='text-right net-pay'>" + str(total_payment) + "</th></tr></tfoot></table>"

        html = {
            'body' : html_body
        }

        return {'html': html}

    @staticmethod
    def get_salary_sheet_all_summary_range(salary_sheets, employees):
        salary_sheet_details = SalarySheetDetails.objects.select_related('salary_sheet__employee').filter(
            salary_sheet__in=salary_sheets)
        gpf_deductions = MonthlyLogForGPF.objects.select_related('provident_fund_profile').filter(salary_sheet__in=salary_sheets)
        gpf_advance_installments = GPFAdvanceInstallment.objects.select_related('gpf_advance__provident_fund_profile').filter(
            salary_sheet__in=salary_sheets)
        home_loan_installments =HomeLoanInstallment.objects.select_related('home_loan__employee').filter(salary_sheet__in=salary_sheets)

        html_body = "<table class='table table table-condensed table-striped table-bordered'>"
        html_body += "<thead class='thead'><tr><th style='min-width: 150px' class='text-center'>Employee Name" \
                "</th><th style='min-width: 100px' class='text-center' rowspan='2'>Designation </th><th " \
                "style='min-width: 70px' class='text-center'>Department </th><th style='min-width: 50px' " \
                "class='text-center'>Account no.</th><th class='text-center'>Net Pay</th></tr>"

        html_body += "</thead><tbody>"

        total_payment = 0
        for employee in employees:
            employee_salary_sheet_details = salary_sheet_details.filter(salary_sheet__employee=employee)
            employee_gpf_deductions = gpf_deductions.filter(provident_fund_profile=employee.providentfundprofile)
            employee_gpf_advance_installments = gpf_advance_installments.filter(
                gpf_advance__provident_fund_profile=employee.providentfundprofile)
            employee_home_loan_installments = home_loan_installments.filter(home_loan__employee=employee)
            html_body += "<tr>"
            name = employee.get_full_name()
            html_body += "<th class='name'>" + name + "</th>"
            html_body += "<td class='designation'>" + employee.designation.name + "</td>"
            html_body += "<td class='department'>" + employee.department.acronym + "</td>"
            html_body += "<td class='account-number'>" + SalarySheetQueryGeneration.check_none(employee.account_number) + "</td>"
            net_allowance = SalarySheetQueryGeneration.get_net_allowance_range(employee_salary_sheet_details)
            net_deduction = SalarySheetQueryGeneration.get_net_deduction_range(employee_salary_sheet_details, employee_gpf_deductions,
                                                                               employee_gpf_advance_installments, employee_home_loan_installments)
            salary_total_payment = net_allowance - net_deduction
            html_body += "<td class='text-right net-pay'>" + str(salary_total_payment) + "</td>"
            html_body += "</tr>"
            total_payment += salary_total_payment

        html_body += "</tbody><tfoot class='tfoot'><tr><th class='total'>Total</th><td></td><td></td><td></td>"

        html_body += "<th class='text-right net-pay'>" + str(total_payment) + "</th></tr></tfoot></table>"

        html = {
            'body' : html_body
        }

        return {'html': html}

    @staticmethod
    def get_salary_sheet_all_details(salary_sheets):
        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet__in=salary_sheets)
        gpf_deductions = MonthlyLogForGPF.objects.filter(salary_sheet__in=salary_sheets)
        gpf_advance_installments = GPFAdvanceInstallment.objects.filter(salary_sheet__in=salary_sheets)
        home_loan_installments = HomeLoanInstallment.objects.filter(salary_sheet__in=salary_sheets)

        allowance_deductions = AllowanceDeduction.objects.all()

        allowances = allowance_deductions.exclude(category='d')
        deductions = allowance_deductions.filter(category='d')

        allow_col = allowances.__len__() + 1
        ded_col = deductions.__len__() + 2


        html_body = "<table class='table table table-condensed table-striped table-bordered'>"
        html_body += "<thead class='thead'><tr><th style='min-width: 150px' class='text-center' rowspan='2'>Employee " \
                "</th><th style='min-width: 100px' class='text-center' rowspan='2'>Designation </th><th " \
                "style='min-width: 70px' class='text-center' rowspan='2'>Department </th><th style='min-width: 50px' " \
                "class='text-center' rowspan='2'>Account No</th>"
        html_body += "<th class='text-center' colspan=" + str(allow_col) + "> Pay & Allowances</th><th class='text-center'" \
                                                                      " colspan=" + str(
            ded_col) + "> Deductions</th><th class='text-center' rowspan='2'>Net Pay</th></tr>"

        html_body += "<tr>"

        for a in allowances:
            html_body += "<th class='text-right " + a.code + "'>" + a.name + "</th>"
        html_body += "<th class='text-center gross-total'>Gross Total</th>"

        for a in deductions:
            html_body += "<th class='text-right " + a.code + "'>" + a.name + "</th>"
            if a.code == 'gpf':
                html_body += "<th class='text-center gpf-adv'>" + "GPF Adv." + "</th>"
        html_body += "<th class='text-center total-deduction'>Total Deduction</th></tr></thead><tbody>"

        for salary_sheet in salary_sheets:
            html_body += "<tr>"
            name = salary_sheet.employee.get_full_name()
            html_body += "<th class='name'>" + name + "</th>"
            html_body += "<td class='designation'>" + salary_sheet.employee.designation.name + "</td>"
            html_body += "<td class='department'>" + salary_sheet.employee.department.acronym + "</td>"
            html_body += "<td class='account-number'>" + SalarySheetQueryGeneration.check_none(
                salary_sheet.employee.account_number) + "</td>"

            for a in allowances:
                amount = SalarySheetQueryGeneration.get_allowance_deductions_amount(salary_sheet_details,
                                                                                    salary_sheet, a)
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"

            net_allowance = SalarySheetQueryGeneration.get_net_allowance(salary_sheet_details, salary_sheet)
            html_body += "<td class='text-right gross-total'>" + str(net_allowance) + "</td>"

            for d in deductions:
                if d.code == 'gpf':
                    try:
                        amount = gpf_deductions.get(salary_sheet=salary_sheet).deduction
                    except MonthlyLogForGPF.DoesNotExist:
                        amount = 0
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"
                    amount = SalarySheetQueryGeneration.check_total(
                        gpf_advance_installments.filter(salary_sheet=salary_sheet).aggregate(total=Sum('deduction'))[
                            'total'])
                    html_body += "<td class='text-right gpf-adv'>" + str(amount) + "</td>"
                elif d.code == 'h.loan':
                    try:
                        amount = home_loan_installments.get(salary_sheet=salary_sheet).deduction
                    except HomeLoanInstallment.DoesNotExist:
                        amount = 0
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"
                else:
                    amount = SalarySheetQueryGeneration.get_allowance_deductions_amount(salary_sheet_details,
                                                                                    salary_sheet, d)
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"

            net_deduction = SalarySheetQueryGeneration.get_net_deduction(salary_sheet_details, gpf_deductions,
                                                                         gpf_advance_installments, salary_sheet)
            html_body += "<td class='text-right total-deduction'>" + str(net_deduction) + "</td>"
            html_body += "<td class='text-right net-pay'>" + str(net_allowance - net_deduction) + "</td>"
            html_body += "</tr>"

        html_body += "</tbody><tfoot class='tfoot'><tr><th class='total'>Total</th><td></td><td></td><td></td>"

        total_gross_payment = 0
        total_gross_deduction = 0
        for a in allowances:
            amount = SalarySheetQueryGeneration.get_allowance_deductions_total(salary_sheet_details, a)
            html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            total_gross_payment = total_gross_payment + amount
        html_body += "<th class='text-right gross-total'>" + str(total_gross_payment) + "</ths>"

        for a in deductions:
            if a.code == 'gpf':
                amount = SalarySheetQueryGeneration.check_total(
                    gpf_deductions.aggregate(total=Sum('deduction'))['total'])
                advance_amount = SalarySheetQueryGeneration.check_total(
                    gpf_advance_installments.aggregate(total=Sum('deduction'))['total'])
                total_gross_deduction = total_gross_deduction + advance_amount
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
                html_body += "<td class='text-right gpf-adv'>" + str(advance_amount) + "</td>"
            elif a.code == 'h.loan':
                amount = SalarySheetQueryGeneration.check_total(
                    home_loan_installments.aggregate(total=Sum('deduction'))['total'])
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            else:
                amount = SalarySheetQueryGeneration.get_allowance_deductions_total(salary_sheet_details, a)
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"

            total_gross_deduction = total_gross_deduction + amount

        total_net_pay = total_gross_payment - total_gross_deduction
        html_body += "<th class='text-right total-deduction'>" + str(total_gross_deduction) + "</th>"
        html_body += "<th class='text-right net-pay'>" + str(total_net_pay) + "</th></tr></tfoot></table>"

        html = {'body':html_body}
        return {'html': html}

    @staticmethod
    def get_salary_sheet_all_details_range(salary_sheets, employees):
        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet__in=salary_sheets)
        gpf_deductions = MonthlyLogForGPF.objects.select_related('provident_fund_profile').filter(salary_sheet__in=salary_sheets)
        gpf_advance_installments = GPFAdvanceInstallment.objects.select_related("gpf_advance__provident_fund_profile").filter(
            salary_sheet__in=salary_sheets)
        home_loan_installments = HomeLoanInstallment.objects.select_related('home_loan__employee').filter(
            salary_sheet__in=salary_sheets)

        allowance_deductions = AllowanceDeduction.objects.all()

        allowances = allowance_deductions.exclude(category='d')
        deductions = allowance_deductions.filter(category='d')

        ###################### table header ####################################
        allow_col = allowances.__len__() + 1
        ded_col = deductions.__len__() + 2

        html_body = "<table class='table table table-condensed table-striped table-bordered'>"
        html_body += "<thead class='thead'><tr><th style='min-width: 150px' class='text-center' rowspan='2'>Employee " \
                     "</th><th style='min-width: 100px' class='text-center' rowspan='2'>Designation </th><th " \
                     "style='min-width: 70px' class='text-center' rowspan='2'>Department </th><th style='min-width: 50px' " \
                     "class='text-center' rowspan='2'>Account No</th>"
        html_body += "<th class='text-center' colspan=" + str(allow_col) + "> Pay & Allowances</th><th class='text-center'" \
                         " colspan=" + str(ded_col) + "> Deductions</th><th class='text-center' rowspan='2'>Net Pay</th></tr>"

        html_body += "<tr>"

        for a in allowances:
            html_body += "<th class='text-right " + a.code + "'>" + a.name + "</th>"
        html_body += "<th class='text-center gross-total'>Gross Total</th>"

        for a in deductions:
            html_body += "<th class='text-right " + a.code + "'>" + a.name + "</th>"
            if a.code == 'gpf':
                html_body += "<th class='text-center gpf-adv'>" + "GPF Adv." + "</th>"
        html_body += "<th class='text-center total-deduction'>Total Deduction</th></tr></thead><tbody>"

        ############################# end Table Header ###########################

        ############################ table body ################################
        for employee in employees:
            employee_salary_sheet_details = salary_sheet_details.filter(salary_sheet__employee= employee)
            html_body += "<tr>"
            html_body += "<td class='name'>" + employee.get_full_name() + "</td>"
            html_body += "<td class='designation'>" + employee.designation.name + "</td>"
            html_body += "<td class='department'>" + employee.department.acronym + "</td>"
            html_body += "<td class='account-number'>" + str(employee.account_number) + "</td>"

            for a in allowances:
                total_allowance_a = SalarySheetQueryGeneration.get_allowance_deductions_total(
                    employee_salary_sheet_details, a)
                html_body += "<td class='text-right " + a.code + "'>" + str(total_allowance_a) + "</td>"

            net_allowance = SalarySheetQueryGeneration.get_net_allowance_range(employee_salary_sheet_details)
            html_body += "<td class='text-right gross-total'>" + str(net_allowance) + "</td>"

            employee_gpf_deductions = gpf_deductions.filter(provident_fund_profile=employee.providentfundprofile)
            employee_gpf_advance_installments = gpf_advance_installments.filter(
                gpf_advance__provident_fund_profile= employee.providentfundprofile)
            employee_home_loan_installments = home_loan_installments.filter(home_loan__employee=employee)

            for d in deductions:
                if d.code == 'gpf':
                    amount = SalarySheetQueryGeneration.check_total(employee_gpf_deductions.aggregate(total=Sum(
                        'deduction'))['total'])

                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"
                    amount = SalarySheetQueryGeneration.check_total(employee_gpf_advance_installments.aggregate(
                        total=Sum('deduction'))['total'])
                    html_body += "<td class='text-right gpf-adv'>" + str(amount) + "</td>"

                elif d.code == 'h.loan':
                    amount = SalarySheetQueryGeneration.check_total(employee_home_loan_installments.aggregate(
                    total=Sum('deduction'))['total'])
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"
                else:
                    amount = SalarySheetQueryGeneration.get_allowance_deductions_total(employee_salary_sheet_details, d)
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"

            net_deduction = SalarySheetQueryGeneration.get_net_deduction_range(employee_salary_sheet_details,
                                                                               employee_gpf_deductions, employee_gpf_advance_installments, employee_home_loan_installments)
            html_body += "<td class='text-right total-deduction'>" + str(net_deduction) + "</td>"
            html_body += "<td class='text-right net-pay'>" + str(net_allowance - net_deduction) + "</td>"
            html_body += "</tr>"

        html_body += "</tbody>"
        ############################ end Table Body ###########################

        ############################ Table Footer ############################
        html_body += "<tfoot class='tfoot'><tr><th class='total'>Total</th><td></td><td></td><td></td>"

        total_gross_payment = 0
        total_gross_deduction = 0
        for a in allowances:
            amount = SalarySheetQueryGeneration.get_allowance_deductions_total(salary_sheet_details, a)
            html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            total_gross_payment = total_gross_payment + amount
        html_body += "<th class='text-right gross-total'>" + str(total_gross_payment) + "</ths>"

        for a in deductions:
            if a.code == 'gpf':
                amount = SalarySheetQueryGeneration.check_total(
                    gpf_deductions.aggregate(total=Sum('deduction'))['total'])
                advance_amount = SalarySheetQueryGeneration.check_total(
                    gpf_advance_installments.aggregate(total=Sum('deduction'))['total'])
                total_gross_deduction = total_gross_deduction + advance_amount
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
                html_body += "<td class='text-right gpf-adv'>" + str(advance_amount) + "</td>"
            elif a.code == 'h.loan':
                amount = SalarySheetQueryGeneration.check_total(
                    home_loan_installments.aggregate(total=Sum('deduction'))['total'])
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            else:
                amount = SalarySheetQueryGeneration.get_allowance_deductions_total(salary_sheet_details, a)
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"

            total_gross_deduction = total_gross_deduction + amount

        total_net_pay = total_gross_payment - total_gross_deduction
        html_body += "<th class='text-right total-deduction'>" + str(total_gross_deduction) + "</th>"
        html_body += "<th class='text-right net-pay'>" + str(total_net_pay) + "</th></tr></tfoot></table>"

        ############################## end Table Footer #######################
        html = {'body': html_body}
        return {'html': html}

    @staticmethod
    def salary_sheet_employee(employee, date_from, date_to):

        salary_sheets = SalarySheet.objects.filter(date__gte=date_from, date__lte=date_to, employee=employee,
                                                   is_freezed=True).order_by('date')

        salary_sheet_details = SalarySheetDetails.objects.filter(salary_sheet__in=salary_sheets)
        gpf_deductions = MonthlyLogForGPF.objects.filter(salary_sheet__in=salary_sheets)
        gpf_advance_installments = GPFAdvanceInstallment.objects.filter(salary_sheet__in=salary_sheets)
        home_loan_installments = HomeLoanInstallment.objects.filter(salary_sheet__in=salary_sheets)

        allowance_deductions = AllowanceDeduction.objects.all()

        allowances = allowance_deductions.exclude(category='d')
        deductions = allowance_deductions.filter(category='d')

        allow_col = allowances.__len__() + 1
        ded_col = deductions.__len__() + 2

        html_head = "<span class='title'> Salary Statement(" + date_from.strftime("%b") + ", " + str(date_from.year) \
                    + " - " + date_to.strftime("%b") + ", " + str(date_to.year) +")</span>"

        html_body = "<table class='table table table-condensed table-striped table-bordered'>"
        html_body += "<thead class='thead'><tr><th style='min-width: 90px' class='text-center' rowspan='2'>Month </th>"
        html_body += "<th class='text-center' colspan=" + str(allow_col) + "> Pay & Allowances</th><th class='text-center'" \
                                                                      " colspan=" + str(
            ded_col) + "> Deductions</th><th class='text-center' rowspan='2'>Net Pay</th></tr>"

        html_body += "<tr>"

        for a in allowances:
            html_body += "<th class='text-right " + a.code + "'>" + a.name + "</th>"
        html_body += "<th class='text-center gross-total'>Gross Total</th>"

        for a in deductions:
            html_body += "<th class='text-right " + a.code + "'>" + a.name + "</th>"
            if a.code == 'gpf':
                html_body += "<th class='text-center gpf-adv'>" + "GPF Adv." + "</th>"
        html_body += "<th class='text-center total-deduction'>TotalDeduction</th></tr></thead><tbody>"

        for salary_sheet in salary_sheets:
            html_body += "<tr>"
            date = salary_sheet.date
            html_body += "<th class='date'>" + date.strftime("%b") + ", " + date.strftime("%Y") + "</th>"

            for a in allowances:
                amount = SalarySheetQueryGeneration.get_allowance_deductions_amount(salary_sheet_details,
                                                                                    salary_sheet, a)
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"

            net_allowance = SalarySheetQueryGeneration.get_net_allowance(salary_sheet_details, salary_sheet)
            html_body += "<td class='text-right gross-total'>" + str(net_allowance) + "</td>"

            for d in deductions:
                if d.code == 'gpf':
                    amount = gpf_deductions.get(salary_sheet=salary_sheet).deduction
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"
                    amount = SalarySheetQueryGeneration.check_total(
                        gpf_advance_installments.filter(salary_sheet=salary_sheet).aggregate(total=Sum('deduction'))[
                            'total'])
                    html_body += "<td class='text-right gpf-adv'>" + str(amount) + "</td>"
                elif d.code == 'h.loan':
                    try:
                        amount = home_loan_installments.get(salary_sheet=salary_sheet).deduction
                    except HomeLoanInstallment.DoesNotExist:
                        amount = 0
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"

                else:
                    amount = SalarySheetQueryGeneration.get_allowance_deductions_amount(salary_sheet_details,
                                                                                    salary_sheet, d)
                    html_body += "<td class='text-right " + d.code + "'>" + str(amount) + "</td>"

            net_deduction = SalarySheetQueryGeneration.get_net_deduction(salary_sheet_details, gpf_deductions,
                                                                         gpf_advance_installments, salary_sheet)
            html_body += "<td class='text-right total-deduction'>" + str(net_deduction) + "</td>"
            html_body += "<td class='text-right net-pay'>" + str(net_allowance - net_deduction) + "</td>"
            html_body += "</tr>"


        html_body += "</tbody><tfoot class='tfoot'><tr><th class='total'>Total</th>"

        total_gross_payment = 0
        total_gross_deduction = 0
        for a in allowances:
            amount = SalarySheetQueryGeneration.get_allowance_deductions_total(salary_sheet_details, a)
            html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            total_gross_payment = total_gross_payment + amount
        html_body += "<td class='text-right gross-total'>" + str(total_gross_payment) + "</td>"

        for a in deductions:
            if a.code == 'gpf':
                amount = SalarySheetQueryGeneration.check_total(
                    gpf_deductions.aggregate(total=Sum('deduction'))['total'])
                advance_amount = SalarySheetQueryGeneration.check_total(
                    gpf_advance_installments.aggregate(total=Sum('deduction'))['total'])
                total_gross_deduction +=  advance_amount
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
                html_body += "<td class='text-right gpf-adv'>" + str(advance_amount) + "</td>"
            elif a.code == 'h.loan':
                amount = SalarySheetQueryGeneration.check_total(
                    home_loan_installments.aggregate(total=Sum('deduction'))['total'])
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            else:
                amount = SalarySheetQueryGeneration.get_allowance_deductions_total(salary_sheet_details, a)
                html_body += "<td class='text-right " + a.code + "'>" + str(amount) + "</td>"
            total_gross_deduction += amount

        total_net_pay = total_gross_payment - total_gross_deduction
        html_body += "<td class='text-right total-deduction'>" + str(total_gross_deduction) + "</td>"
        html_body += "<td class='text-right net-pay'>" + str(total_net_pay) + "</td></tr></tfoot></table>"
        html_extra = SalarySheetQueryGeneration.employee_details_section(employee)

        html = {'body': html_body,
                'title': html_head,
                'extra': html_extra
        }

        return {'html': html}

    @staticmethod
    def employee_details_section(employee):
        html = "<div class='employee-details-section'>"
        html += "<div class='col-sm-4'>"
        html += "<div class='name'>" + employee.get_full_name() + "</div>"
        html += "<div>" + employee.designation.name + "</div>"
        html += "<div>" + employee.department.acronym + "</div></div>"
        html += "<div class='col-sm-4'><table><tr><td class='label'>Contact : </td>"
        html += "<td>" + str(employee.contact) + "</td></tr><tr><td class='label'>Email : </td>"
        html += "<td>" + employee.email + "</td>"
        html += "</tr><tr><td class='label'>Address : </td><td>" + str(employee.address) + "</td>"
        html += "</tr></table></div>"
        html += "<div class='col-sm-4'><table><tr>"
        html += "<td class='label'>Joining Date: </td><td>" + str(employee.joining_date) + "</td></tr>"
        html += "<tr><td class='label'>Account Number: </td><td>" + str(employee.account_number) + "</td></tr>"
        html += "<tr><td class='label'>TIN :  </td><td>" + str(employee.tax_id_number) + \
                "</td></tr></table></div><div class= 'clear'></div></div><div class='clear'></div>"
        return html
