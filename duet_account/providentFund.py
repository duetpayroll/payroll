from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.contrib import messages
from datetime import datetime

from django.views.generic import DetailView, DeleteView, View
from django.db.models import Sum
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView

from duet_account.salarySheet import SalarySheetQueryGeneration
from duet_account.util import EmployeeQueryFormView
from .forms import MonthlyProvidentFundForm, GPFAdvanceInslallmentForm, YearlyLogForGPFFormUpdate, \
    YearlyLogForGPFFormCreate, EmployeeSalarySheetQueryForm, GPFSummaryQueryForm

from employee.models import Employee
from duet_admin.models import Settings
from .models import ProvidentFundProfile, MonthlyLogForGPF, GPFAdvance, GPFAdvanceInstallment, YearlyLogForGPF, \
    SalarySheet

from duet_admin.utils import LoginAndAccountantRequired, CustomTableView, CustomUpdateView, CustomCreateView
from duet_admin.settingsCode import NO_GPF_ADVANCE
from .calculations import SalarySheetCalculations


######################################### Provident Fund Profile #########################################


class ProvidentFundProfileUpdate(LoginAndAccountantRequired, CustomUpdateView):
    model = ProvidentFundProfile
    fields = ['has_interest', 'percentage']
    template_name = 'duet_account/employee/detail_form.html'
    title = 'Edit - '

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.object = ProvidentFundProfile.objects.get(employee=self.employee)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def post(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.object = ProvidentFundProfile.objects.get(employee=self.employee)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        employee = self.object.employee
        return redirect('duet_account:provident-fund-profile-detail', slug=employee.slug)


########################################################### GPF Monthly Subscription ##################################################
class ProvidentFundMonthlySubscriptionDetail(LoginAndAccountantRequired, DetailView):
    model = MonthlyLogForGPF

    def get(self, request, *args, **kwargs):
        monthly_subscripion = self.get_object()
        salary_sheet = monthly_subscripion.salary_sheet
        return redirect('duet_account:salary-sheet-detail', pk=salary_sheet.pk)


class ProvidentFundProfileDetail(LoginAndAccountantRequired, CustomTableView):
    model = MonthlyLogForGPF
    title = 'GPF Montly Subscription Logs '
    template_name = 'duet_account/employee/detail_list.html'

    exclude = ['id', 'provident_fund_profile']
    filter_fields = {'salary_sheet__date': ['exact'], }
    actions = [{'url': 'duet_account:gpf-monthly-subscription-detail', 'target': '_blank', 'icon': 'glyphicon '
                                                                                                   'glyphicon-th-large',
                'tooltip': 'Detail'}, ]

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.provident_fund_profile = ProvidentFundProfile.objects.get(employee=self.employee)
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(provident_fund_profile=self.provident_fund_profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['provident_fund_profile'] = self.provident_fund_profile
        context['employee'] = self.employee
        return context


########################################################### GPF Yearly Log ##################################################

class GPFYearlyLogs(LoginAndAccountantRequired, CustomTableView):
    model = YearlyLogForGPF
    title = 'GPF Yearly Logs '
    template_name = 'duet_account/employee/detail_list.html'

    exclude = ['id', 'provident_fund_profile', 'created_at', 'modified_at']
    filter_fields = {'date': ['exact'], }
    actions = [{'url': 'duet_account:gpf-yearly-log-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
               {'url': 'duet_account:gpf-yearly-log-confirm', 'icon': 'glyphicon glyphicon-lock', 'tooltip': 'Freeze'},
               {'url': 'duet_account:gpf-yearly-log-delete', 'icon': 'glyphicon glyphicon-trash',
                'tooltip': 'Delete'}, ]

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.provident_fund_profile = ProvidentFundProfile.objects.get(employee=self.employee)
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(provident_fund_profile=self.provident_fund_profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class GPFYearlyLogConfirm(LoginAndAccountantRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = YearlyLogForGPF
    template_name = 'duet_account/employee/providentFund/yearlyLog/confirm.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.employee = self.object.provident_fund_profile.employee
        if self.object.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': self.employee})
        return super().get(request, args, kwargs)

    def post(self, *args, **kwargs):
        yearly_log = self.get_object()
        employee = yearly_log.provident_fund_profile.employee
        yearly_log.is_freezed = True
        yearly_log.save()
        return redirect('duet_account:gpf-yearly-log', slug=employee.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class GPFYearlyLogCreate(LoginAndAccountantRequired, View):
    template_name = 'duet_account/employee/providentFund/yearlyLog/create.html'

    def get(self, request, slug):
        employee = Employee.objects.get(slug=slug)
        provident_fund_profile = ProvidentFundProfile.objects.get(employee=employee)
        yearly_log_for_gpf = YearlyLogForGPF()
        year_to = datetime.now().year
        year_from = year_to - 1

        details = ProvidentFundOperations.get_gpf_yearly_details(employee, provident_fund_profile, year_from, year_to)
        summary = details['summary']
        initial = {'net_deduction': summary['total_deduction'], 'net_interest': summary['total_interest'], \
                   'total_credit': summary['total_credit']}
        form = YearlyLogForGPFFormCreate(None, instance=yearly_log_for_gpf,
                                         provident_fund_profile=provident_fund_profile, initial=initial)
        return render(request, self.template_name, {'employee': employee, 'form': form, 'details': details})

    def post(self, request, slug):
        employee = Employee.objects.get(slug=slug)
        provident_fund_profile = ProvidentFundProfile.objects.get(employee=employee)
        yearly_log_for_gpf = YearlyLogForGPF()
        form = YearlyLogForGPFFormCreate(request.POST, instance=yearly_log_for_gpf,
                                         provident_fund_profile=provident_fund_profile)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
        return redirect('duet_account:gpf-yearly-log', slug=employee.slug)


class GPFYearlyLogUpdate(LoginAndAccountantRequired, View):
    template_name = 'duet_account/employee/providentFund/yearlyLog/create.html'

    def get(self, request, pk):
        yearly_log_for_gpf = YearlyLogForGPF.objects.select_related('provident_fund_profile__employee').get(pk=pk)
        provident_fund_profile = yearly_log_for_gpf.provident_fund_profile
        employee = provident_fund_profile.employee
        if yearly_log_for_gpf.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': employee})
        details = ProvidentFundOperations.get_gpf_yearly_details(employee, provident_fund_profile)
        form = YearlyLogForGPFFormUpdate(None, instance=yearly_log_for_gpf)
        return render(request, self.template_name, {'employee': employee, 'form': form, 'details': details})

    def post(self, request, pk):
        yearly_log_for_gpf = YearlyLogForGPF.objects.select_related('provident_fund_profile__employee').get(pk=pk)
        provident_fund_profile = yearly_log_for_gpf.provident_fund_profile
        employee = provident_fund_profile.employee
        form = YearlyLogForGPFFormUpdate(request.POST, instance=yearly_log_for_gpf)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
        return redirect('duet_account:gpf-yearly-log', slug=employee.slug)


class GPFYearlyLogDelete(LoginAndAccountantRequired, DeleteView):
    model = YearlyLogForGPF
    template_name = 'duet_account/employee/confirm_delete.html'

    def get(self, request, *args, **kwargs):
        yearly_log = self.get_object()
        self.employee = yearly_log.provident_fund_profile.employee
        if yearly_log.is_freezed:
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
        self.success_url = reverse_lazy('duet_account:gpf-yearly-log', kwargs={'slug': employee_slug})
        return super().post(request, args, kwargs)


class GPFSummaryView(EmployeeQueryFormView):
    template_name = 'duet_account/employee/form_target_blank.html'
    form_class = GPFSummaryQueryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate GPF Summary'
        return context

    def form_valid(self, form):
        employee = self.employee
        provident_fund_profile = employee.providentfundprofile
        year_from = int(form.cleaned_data['year_from'])
        year_to = int(form.cleaned_data['year_to'])
        details = ProvidentFundOperations.get_gpf_yearly_details(employee, provident_fund_profile, year_from,
                                                                 year_to)
        return render(self.request, self.query_template_name, {'details': details, 'employee': employee})


############################################################### GPF Advance ##########################################################

class ProvidentFundAdvanceCreate(LoginAndAccountantRequired, CustomCreateView):
    model = GPFAdvance
    fields = ['date', 'amount', 'no_of_installments', 'monthly_payment']

    template_name = 'duet_account/employee/detail_form.html'
    title = 'Create New Provident Fund Advance'

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        provident_fund_profile = self.employee.providentfundprofile
        no_current_home_loan = GPFAdvance.objects.filter(provident_fund_profile=provident_fund_profile, is_closed=False)
        max_gpf_advance = Settings.objects.get(code=NO_GPF_ADVANCE).value
        if no_current_home_loan.count() >= max_gpf_advance:
            messages.error(request, "This employee has already taken maximum no of GPF Advances")
            return redirect('duet_account:gpf-advance-list', slug=self.employee.slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def post(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.provident_fund_profile = ProvidentFundProfile.objects.get(employee=self.employee)
        self.object = None
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.provident_fund_profile = self.provident_fund_profile
        self.object.save()
        return redirect('duet_account:gpf-advance-list', slug=self.employee.slug)


class ProvidentFundAdvanceList(LoginAndAccountantRequired, CustomTableView):
    model = GPFAdvance

    exclude = ['closing_date', 'provident_fund_profile', 'created_at', 'modified_at']

    title = 'General ProvidentFund Advance List'
    template_name = 'duet_account/employee/detail_list.html'

    actions = [
        {'url': 'duet_account:gpf-advance-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'View Detail'},
        {'url': 'duet_account:gpf-advance-detail-summary', 'icon': 'glyphicon glyphicon-book', 'target': '_blank',
         'tooltip': 'Summary'},
        {'url': 'duet_account:gpf-advance-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_account:gpf-advance-freeze', 'icon': 'glyphicon glyphicon-lock', 'tooltip': 'Freeze'},
        {'url': 'duet_account:gpf-advance-close', 'icon': 'glyphicon glyphicon-ok', 'tooltip': 'Close'},
        {'url': 'duet_account:gpf-advance-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}]

    filter_fields = {'date': ['gt', 'lt', ], }

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.provident_fund_profile = ProvidentFundProfile.objects.get(employee=self.employee)
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(provident_fund_profile=self.provident_fund_profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['provident_fund_profile'] = self.provident_fund_profile
        context['employee'] = self.employee
        return context


class ProvidentFundAdvanceUpdate(LoginAndAccountantRequired, CustomUpdateView):
    model = GPFAdvance
    fields = ['date', 'amount', 'no_of_installments', 'monthly_payment']
    template_name = 'duet_account/employee/detail_form.html'
    title = 'Edit - '

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.employee = self.object.provident_fund_profile.employee
        if self.object.is_closed or self.object.is_freezed:
            return render(request, 'duet_account/employee/advance_update_not_allowed.html', {'employee': self.employee})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        employee = self.object.provident_fund_profile.employee
        return redirect('duet_account:gpf-advance-list', slug=employee.slug)


class ProvidentFundAdvanceDetail(CustomTableView):
    model = GPFAdvanceInstallment

    exclude = ['id', 'gpf_advance']
    filter_fields = {'salary_sheet__date': ['exact'], }

    actions = [{'url': 'duet_account:gpf-advance-installment-detail', 'icon': 'glyphicon glyphicon-th-large',
                'tooltip': 'View Details', 'target': '_blank'}]

    title = 'Installment List'

    def get(self, request, *args, **kwargs):
        self.gpf_advance = GPFAdvance.objects.select_related('provident_fund_profile__employee').get(
            pk=kwargs.pop('pk'))
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(gpf_advance=self.gpf_advance)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gpf_advance'] = self.gpf_advance
        context['employee'] = self.gpf_advance.provident_fund_profile.employee
        return context


class AccountProvidentFundAdvanceDetail(LoginAndAccountantRequired, ProvidentFundAdvanceDetail):
    template_name = 'duet_account/employee/providentFund/advance_detail.html'


class GPFAdvanceInstalmentDetail(LoginAndAccountantRequired, DetailView):
    model = GPFAdvanceInstallment

    def get(self, request, *args, **kwargs):
        monthly_subscripion = self.get_object()
        salary_sheet = monthly_subscripion.salary_sheet
        return redirect('duet_account:salary-sheet-detail', pk=salary_sheet.pk)


class GPFAdvanceDelete(LoginAndAccountantRequired, DeleteView):
    model = GPFAdvance
    template_name = 'duet_account/employee/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return redirect('duet_account:gpf-advance-list', slug=self.employee.slug)
        except ProtectedError:
            return render(request, 'duet_account/employee/protection_error.html', {'employee': self.employee})

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.employee = self.object.provident_fund_profile.employee
        if self.object.is_closed or self.object.is_freezed:
            return render(request, 'duet_account/employee/advance_update_not_allowed.html', {'employee': self.employee})
        request.session['employee_slug'] = self.employee.slug
        return super().get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def post(self, request, *args, **kwargs):
        employee_slug = request.session['employee_slug']
        self.employee = Employee.objects.get(slug=employee_slug)
        del request.session['employee_slug']
        self.success_url = reverse_lazy('duet_account:gpf-advance-list', kwargs={'slug': employee_slug})
        return super().post(request, args, kwargs)


class GPFAdvanceConfirm(LoginAndAccountantRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = GPFAdvance
    template_name = 'duet_account/employee/confirm_freeze.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        self.employee = object.provident_fund_profile.employee
        if object.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': self.employee})
        return super().get(request, args, kwargs)

    def post(self, *args, **kwargs):
        object = self.get_object()
        object.is_freezed = True
        object.save()
        return redirect('duet_account:gpf-advance-list', slug=object.provident_fund_profile.employee.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class GPFAdvanceClose(LoginAndAccountantRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = GPFAdvance
    template_name = 'duet_account/employee/confirm_close.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        self.employee = object.provident_fund_profile.employee
        if object.is_freezed is False:
            return render(request, 'duet_account/employee/close_not_allowed_not_freezed.html',
                          {'employee': self.employee, 'object': object})
        if object.is_closed:
            return render(request, 'duet_account/employee/close_not_allowed_closed.html',
                          {'employee': self.employee, 'object': object})
        return super().get(request, args, kwargs)

    def post(self, *args, **kwargs):
        object = self.get_object()
        object.is_closed = True
        object.closing_date = datetime.today()
        object.save()
        return redirect('duet_account:gpf-advance-list', slug=object.provident_fund_profile.employee.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class GPFAdvanceSummaryView(EmployeeQueryFormView):
    template_name = 'duet_account/employee/form_target_blank.html'
    form_class = EmployeeSalarySheetQueryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate GPF Advance Summary'
        return context

    def form_valid(self, form):
        employee = self.employee
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']
        query_result = ProvidentFundOperations.get_gpf_advance_summary_range(employee, date_from, date_to)
        return render(self.request, self.query_template_name,
                      {'employee': employee, 'form': form, 'details': query_result})


class GPFAdvanceDetailSummaryView(LoginAndAccountantRequired, DetailView):
    model = GPFAdvance
    query_template_name = 'report/query.html'

    def get(self, request, *args, **kwargs):
        gpf_advance = self.get_object()
        query_result = ProvidentFundOperations.get_gpf_advance_summary(gpf_advance)
        return render(self.request, self.query_template_name, {'details': query_result})


############################################### GPF Salary Related Operations ###############################################################


class ProvidentFundOperations(object):
    @staticmethod
    def get_gpf_yearly_details(employee, provident_fund_profile, year_from, year_to):

        def get_summary_config():
            return {'total_deduction': 0, 'total_interest': 0, 'total_credit': 0}

        def get_date_june_year_to():
            today = datetime.now()
            return today.replace(day=1, month=6, year=year_to)

        def get_date_july_year_from():
            today = datetime.now()
            return today.replace(day=1, month=7, year=year_from)

        def get_gpf_initial_credit(provident_fund_profile, date):
            try:
                previous_gpf_yearly_log = YearlyLogForGPF.objects.get(provident_fund_profile=provident_fund_profile,
                                                                      date=date)
                return previous_gpf_yearly_log.total_credit

            except YearlyLogForGPF.DoesNotExist:
                return 0

        year_from_july = get_date_july_year_from()
        year_to_june = get_date_june_year_to()
        summary = get_summary_config()
        header = "<span> GPF Summary (" + year_from_july.strftime("%b") + ',' + str(
            year_from_july.year) + " - " + year_to_june.strftime("%b") + ',' + str(year_to_june.year) + ")" + "</span>"

        salary_sheets = SalarySheet.objects.filter(date__gte=year_from_july, date__lte=year_to_june, employee=employee,
                                                   is_freezed=True).order_by('date')
        gpf_subscription_list = MonthlyLogForGPF.objects.filter(salary_sheet__in=salary_sheets)
        gpf_advance_installment_list = GPFAdvanceInstallment.objects.filter(salary_sheet__in=salary_sheets)
        gpf_advance_list = GPFAdvance.objects.filter(date__gte=year_from_july, date__lte=year_to_june,
                                                     provident_fund_profile=provident_fund_profile,
                                                     is_freezed=True).order_by('date')
        html_body = "<div class='panel-group'>"
        html_body += "<div class='panel panel-default'>"
        html_body += "<div class='panel-heading'>GPF Subscriptions and Advance Installments</div>"
        html_body += "<div class='panel-body'> <table class='table  table-condensed table-hover " \
                     "table-striped'><thead><tr><th>Date</th><th>GPF deductions</th><th>Interest</th>"
        for gpf_advance in gpf_advance_list:
            html_body += "<th> GPF Advance(" + str(gpf_advance.id) + ")</th>"
            html_body += "<th> GPF Adv.(" + str(gpf_advance.id) + ") Interest</th>"
        html_body += "</tr></thead><tbody>"

        for salary_sheet in salary_sheets:
            html_body += "<tr>"
            html_body += "<td class='date'>" + salary_sheet.get_date() + "</td>"
            try:
                gpf_subscription = gpf_subscription_list.get(salary_sheet=salary_sheet)
                html_body += "<td class='gpf_subscription'>" + str(gpf_subscription.deduction) + "</td>"
                html_body += "<td class='gpf_interest'>" + str(gpf_subscription.interest) + "</td>"
            except MonthlyLogForGPF.DoesNotExist:
                pass

            for gpf_advance in gpf_advance_list:
                try:
                    gpf_advance_installment = gpf_advance_installment_list.get(gpf_advance=gpf_advance,
                                                                               salary_sheet=salary_sheet)
                    html_body += "<td class='gpf_advance_installment_" + str(gpf_advance.id) + "'>" + str(
                        gpf_advance_installment.deduction) + "</td>"
                    html_body += "<td class='gpf_advance_interest_" + str(gpf_advance.id) + "'>" + str(
                        gpf_advance_installment.interest) + "</td>"
                except GPFAdvanceInstallment.DoesNotExist:
                    html_body += "<td></td>"
                    html_body += "<td></td>"
            html_body += "</tr>"

        html_body += "</tbody></table></div></div>"
        html_body += "<div class='col-sm-5 panel panel-default'><div class='panel-heading'> " \
                     "GPF Advances</div><div class='panel-body'><table class='table table-condensed table-hover " \
                     "table-striped'> <thead><tr><th>Date</th><th>Id</th><th>Amount</th><th>Excess</th><th>Closing " \
                     "Date</th> </tr></thead><tbody>"

        gpf_advance_excess = 0
        for gpf_advance in gpf_advance_list:
            html_body += "<tr>"
            html_body += "<td class='date'>" + str(gpf_advance.date) + "</td>"
            html_body += "<td class='id'>" + str(gpf_advance.id) + "</td>"
            html_body += "<td class='amount'>" + str(gpf_advance.amount) + "</td>"
            excess = SalarySheetCalculations.calculate_gpf_interest(gpf_advance.date, gpf_advance.amount)
            html_body += "<td class='excess'>" + str(excess) + "</td>"
            html_body += "<td class='closing_date'>" + str(gpf_advance.closing_date) + "</td>"
            gpf_advance_excess += excess
            html_body += "</tr>"

        html_body += "</tbody></table></div></div>"

        total_gpf_deduction = gpf_subscription_list.aggregate(total_deduction=Sum('deduction'))['total_deduction']
        if total_gpf_deduction is None:
            total_gpf_deduction = 0

        total_gpf_interest = gpf_subscription_list.aggregate(total_interest=Sum('interest'))['total_interest']
        if total_gpf_interest is None:
            total_gpf_interest = 0

        total_advance_deduction = gpf_advance_installment_list.aggregate(total_deduction=Sum('deduction'))[
            'total_deduction']
        if total_advance_deduction is None:
            total_advance_deduction = 0

        total_advance_interest = gpf_advance_installment_list.aggregate(total_interest=Sum('interest'))[
            'total_interest']
        if total_advance_interest is None:
            total_advance_interest = 0

        initial_credit = get_gpf_initial_credit(provident_fund_profile, year_from_july)
        initial_credit_interest = SalarySheetCalculations.calculate_gpf_interest_for_year(initial_credit)
        summary['total_deduction'] = total_gpf_deduction + total_advance_deduction
        summary['total_interest'] = total_gpf_interest + total_advance_interest + initial_credit_interest
        summary['total_credit'] = summary['total_deduction'] + summary[
            'total_interest'] + initial_credit - gpf_advance_excess

        html_body += "<div class='col-sm-7 panel panel-default'>"
        html_body += "<div class='panel-heading'>Summary Table</div>" \
                     "<div class='panel-body'><table class ='table table-condensed'><tbody>"
        html_body += "<tr><th>Total GPF Subscription Deduction </th><td>" + str(total_gpf_deduction) + "</td>"
        html_body += "<th> Total GPF Subscription Interest</th><td>" + str(total_gpf_interest) + "</td></tr>"

        html_body += "<tr><th> Total GPF Advance Deduction</th><td>" + str(total_advance_deduction) + "</td>"
        html_body += "<th> Total GPF Advance Interest </th> <td>" + str(total_advance_interest) + "</td></tr>"

        html_body += "<tr> <th> Total Deduction</th><th>" + str(summary['total_deduction']) + "</th>"
        html_body += "<th> Interest on Initial Credit </th> <td>" + str(initial_credit_interest) + "</td></tr>"

        html_body += "<tr><td></td><td></td><th>Total Interest </th><th>" + str(
            summary['total_interest']) + "</th></tr>"

        html_body += "<tr><th> Initial Credit </th><th>" + str(initial_credit) + "</th></tr>"

        html_body += "<tr><th> Excess</th><th>" + str(gpf_advance_excess) + "</th></tr>"
        html_body += "<tr><th>Total Credit</th><th>" + str(
            summary['total_credit']) + "</th></tr></tbody></table></div></div></div>"

        html_extra = SalarySheetQueryGeneration.employee_details_section(employee)

        html = {'body': html_body, 'title': header, 'extra': html_extra}

        return {'html': html, 'summary': summary, }

    @staticmethod
    def get_gpf_advance_summary_range(employee, month_from, month_to):
        salary_sheets = SalarySheet.objects.filter(employee=employee, date__gte=month_from, date__lte=month_to,
                                                   is_freezed=True).order_by('date')
        gpf_advance_installments = GPFAdvanceInstallment.objects.select_related('gpf_advance', 'salary_sheet').filter(
            salary_sheet__in=salary_sheets)
        gpf_advances = GPFAdvance.objects.filter(
            gpfadvanceinstallment__in=gpf_advance_installments).distinct().order_by('id')

        html_title = "<span class='title'>GPF Advance Summary (" + month_from.strftime("%b") + ", " + str(
            month_from.year) +\
                     " - " + month_to.strftime("%b") + ", " + str(month_to.year) + ")</span>"
        html_body = "<table class='table table-condensed table-bordered " \
               "table-striped'><thead><tr><th>Month</th>"
        for gpf_advance in gpf_advances:
            html_body += "<th> GPF Adv.( " + str(gpf_advance.id) + ") Inst</th>"
        for salary_sheet in salary_sheets:
            html_body += "<tr><th>" + str(salary_sheet.date) + "</th>"
            for gpf_advance in gpf_advances:
                try:
                    installment = gpf_advance_installments.get(salary_sheet=salary_sheet, gpf_advance=gpf_advance)
                    html_body += "<td>" + str(installment.deduction) + "(" + str(installment.installment_no) + "/" + str(
                        gpf_advance.no_of_installments) + ")</td>"
                except GPFAdvanceInstallment.DoesNotExist:
                    html_body += "<td></td>"
            html_body += "</tr>"
        html_body += "<tr><th>Total</th>"
        for gpf_advance in gpf_advances:
            total_deduction = \
            gpf_advance_installments.filter(gpf_advance=gpf_advance).aggregate(total=Sum('deduction'))['total']
            html_body += "<td>" + str(total_deduction) + "</td>"
        html_body += "</tr></tbody></table>"
        html_extra = SalarySheetQueryGeneration.employee_details_section(employee)
        html = {'body' : html_body,
                'title': html_title,
                'extra': html_extra}
        return {'html': html}

    @staticmethod
    def get_gpf_advance_summary(gpf_advance):
        employee = gpf_advance.provident_fund_profile.employee
        gpf_advance_installs = GPFAdvanceInstallment.objects.select_related('salary_sheet').filter(
            gpf_advance=gpf_advance, salary_sheet__is_freezed=True)
        html_body = "<table class='table table-condensed table-bordered " \
               "table-striped'><thead><tr><th>Month</th><th>Instal. " \
               "No</th><th>Deduction</th><th>Interest</th></tr></thead><tbody>"
        for installment in gpf_advance_installs:
            html_body += "<tr><td>" + installment.salary_sheet.get_date() + "</td>"
            html_body += "<td>" + str(installment.installment_no) + "</td>"
            html_body += "<td class='text-right'>" + str(installment.deduction) + "</td>"
            html_body += "<td class='text-right'>" + str(installment.interest) + "</td>"
            html_body += "</tr>"

        total_deduction = gpf_advance_installs.aggregate(total=Sum('deduction'))['total']
        total_interest = gpf_advance_installs.aggregate(total=Sum('interest'))['total']

        html_body += "<tr><th>Total</th><td></td><th class='text-right'>" + str(total_deduction) + "</th><th " \
                                                                                         "class='text-right'>" + \
                str(total_interest) + "</th></tr></tbody><table>"
        html_extra = SalarySheetQueryGeneration.employee_details_section(employee)
        html_extra += ProvidentFundOperations.get_gpf_advance_section(gpf_advance)
        html = {
            'body': html_body,
            'extra': html_extra

        }
        return {'html': html}

    @staticmethod
    def get_gpf_advance_section(gpf_advance):
        html = "<div class='gpf-advance-details-section panel panel-default'><div " \
               "class='panel-heading'>GPF Advance - " + str(gpf_advance.id) + "</div><div " \
               "class='panel-body'>"
        html += "<div class='col-sm-4'><table>"
        html += "<tr><td class='label'>Amount : </td><td>" + str(gpf_advance.amount) + "</td></tr>"
        html += "<tr><td class='label'>Date: </td><td>" + str(gpf_advance.date) + "</td></tr></table></div>"
        html += "<div class='col-sm-4'><table>"
        html += "<tr><td class='label'>No of Installments : </td><td>" + str(gpf_advance.no_of_installments) + "</td></tr>"
        html += "<tr><td class='label'>Monthly Payment : </td><td>" + str(gpf_advance.monthly_payment) + "</td></tr></table></div>"
        html += "<div class='col-sm-4'><table><tr><td class='label'>Closing Date :  </td><td>" + str(
            gpf_advance.closing_date) + "</td></tr>"
        html += "<tr><td class='label'>Closed: </td><td>" + str(gpf_advance.is_closed) + "</td></tr>"
        html += "</table></div></div></div>"
        return html
