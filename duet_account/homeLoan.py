from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.contrib import messages
from datetime import datetime

from django.views.generic import DetailView, DeleteView, View
from django.db.models import Sum
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView

from duet_account.salarySheet import SalarySheetQueryGeneration
from .forms import MonthlyProvidentFundForm

from employee.models import Employee
from .models import HomeLoan, HomeLoanInstallment, SalarySheet
from duet_admin.models import Settings
from duet_admin import settingsCode
from .forms import HomeLoanInslallmentForm

from duet_admin.utils import LoginAndAccountantRequired, CustomTableView, CustomUpdateView, CustomCreateView


class HomeLoanCreate(LoginAndAccountantRequired, CustomCreateView):
    model = HomeLoan
    fields = ['date', 'amount', 'no_of_installments', 'monthly_payment']

    template_name = 'duet_account/employee/detail_form.html'
    title = 'Create Home Loan'

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        home_loan = HomeLoan.objects.filter(employee=self.employee, is_freezed = True)
        home_loan_current = home_loan.filter(is_closed=False)
        if home_loan_current.count() > 0:
            messages.error(request, "This employee has already taken a home loan")
            return redirect('duet_account:home-loan-list', slug=self.employee.slug)
        max_home_loan = Settings.objects.get(code=settingsCode.NO_HOME_LOAN).value
        if home_loan.count() >= max_home_loan:
            messages.error(request, "This employee has already taken maximum no of home loans")
            return redirect('duet_account:home-loan-list', slug=self.employee.slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def post(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        self.object = None
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.employee = self.employee
        self.object.save()
        return redirect('duet_account:home-loan-list', slug=self.employee.slug)


class HomeLoanList(LoginAndAccountantRequired, CustomTableView):
    model = HomeLoan

    exclude = [ 'employee', 'created_at', 'modified_at', 'closing_date', 'monthly_payment']

    title = 'Home Loan List'
    template_name = 'duet_account/employee/detail_list.html'

    actions = [
        {'url': 'duet_account:home-loan-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'View Detail'},
        {'url': 'duet_account:home-loan-detail-summary', 'icon': 'glyphicon glyphicon-book', 'target': '_blank',
         'tooltip': 'Summary'},
        {'url': 'duet_account:home-loan-edit', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_account:home-loan-freeze', 'icon': 'glyphicon glyphicon-lock', 'tooltip': 'Freeze'},
        {'url': 'duet_account:home-loan-close', 'icon': 'glyphicon glyphicon-ok', 'tooltip': 'Close'},
        {'url': 'duet_account:home-loan-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}]

    filter_fields = {'date': ['gt', 'lt', ], }

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(employee=self.employee)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class HomeLoanUpdate(LoginAndAccountantRequired, CustomUpdateView):
    model = HomeLoan
    fields = ['date', 'amount', 'no_of_installments', 'monthly_payment']
    template_name = 'duet_account/employee/detail_form.html'
    title = 'Edit - '

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        self.employee = object.employee
        if object.is_closed or object.is_freezed:
            return render(request,
                          'duet_account/employee/advance_update_not_allowed.html',
                          {'employee': self.employee})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        employee = self.object.employee
        return redirect('duet_account:home-loan-list', slug=employee.slug)


class HomeLoanDetail(LoginAndAccountantRequired, CustomTableView):
    template_name = 'duet_account/employee/homeLoan/advance_detail.html'
    model = HomeLoanInstallment

    exclude = ['id', 'home_loan']
    filter_fields = {'salary_sheet__date': ['exact'], }

    actions = [{'url': 'duet_account:home-loan-installment-detail', 'icon': 'glyphicon glyphicon-th-large',
                'tooltip': 'View Details', 'target': '_blank'}]

    title = 'Installment List'

    def get(self, request, *args, **kwargs):
        self.home_loan = HomeLoan.objects.select_related('employee').get(
            pk=kwargs.pop('pk'))
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(home_loan=self.home_loan)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_loan'] = self.home_loan
        context['employee'] = self.home_loan.employee
        return context


class HomeLoanDelete(LoginAndAccountantRequired, DeleteView):
    model = HomeLoan
    template_name = 'duet_account/employee/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return redirect('duet_account:home-loan-list', slug=self.employee.slug)
        except ProtectedError:
            return render(request, 'duet_account/employee/protection_error.html', {'employee': self.employee})

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        self.employee = object.employee
        if object.is_closed or object.is_freezed:
            return render(request,
                          'duet_account/employee/advance_update_not_allowed.html',
                          {'employee': self.employee})
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
        self.success_url = reverse_lazy('duet_account:home-loan-list', kwargs={'slug': employee_slug})
        return super().post(request, args, kwargs)


class HomeLoanConfirm(LoginAndAccountantRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = HomeLoan
    template_name = 'duet_account/employee/confirm_freeze.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        self.employee = object.employee
        if object.is_freezed:
            return render(request, 'duet_account/employee/update_not_allowed.html', {'employee': self.employee})
        return super().get(request, args, kwargs)

    def post(self, *args, **kwargs):
        home_loan = self.get_object()
        home_loan.is_freezed = True
        home_loan.save()
        return redirect('duet_account:home-loan-list', slug=home_loan.employee.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class HomeLoanClose(LoginAndAccountantRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = HomeLoan
    template_name = 'duet_account/employee/confirm_close.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        self.employee = object.employee
        if object.is_freezed is False:
            return render(request, 'duet_account/employee/close_not_allowed_not_freezed.html', {'employee': self.employee,
                                                                                     'object': object})
        if object.is_closed:
            return render(request, 'duet_account/employee/close_not_allowed_closed.html', {'employee': self.employee,
                                                                                     'object': object})
        return super().get(request, args, kwargs)

    def post(self, *args, **kwargs):
        home_loan = self.get_object()
        home_loan.is_closed = True
        home_loan.closing_date = datetime.today()
        home_loan.save()
        return redirect('duet_account:home-loan-list', slug=home_loan.employee.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context


class HomeLoanInstalmentDetail(LoginAndAccountantRequired, DetailView):
    model = HomeLoanInstallment

    def get(self, request, *args, **kwargs):
        home_loan_installment = self.get_object()
        salary_sheet = home_loan_installment.salary_sheet
        return redirect('duet_account:salary-sheet-detail', pk=salary_sheet.pk)


class HomeLoanDetailSummaryView(LoginAndAccountantRequired, DetailView):
    model = HomeLoan
    query_template_name = 'report/query.html'

    def get(self, request, *args, **kwargs):
        home_loan = self.get_object()
        query_result = HomeLoanOperations.get_home_loan_summary(home_loan)
        return render(self.request, self.query_template_name, {'details': query_result})


############################################### Home Loan Salary Related Operations ####################################################


class HomeLoanOperations(object):
    @staticmethod
    def get_home_loan_summary(home_loan):
        employee = home_loan.employee
        home_loan_installs = HomeLoanInstallment.objects.select_related('salary_sheet').filter(
            home_loan=home_loan, salary_sheet__is_freezed=True)
        html_body = "<table class='table table-condensed table-bordered " \
                    "table-striped'><thead><tr><th>Month</th><th>Instal. " \
                    "No</th><th>Deduction</th></tr></thead><tbody>"
        for installment in home_loan_installs:
            html_body += "<tr><td>" + installment.salary_sheet.get_date() + "</td>"
            html_body += "<td>" + str(installment.installment_no) + "</td>"
            html_body += "<td class='text-right'>" + str(installment.deduction) + "</td>"
            html_body += "</tr>"

        total_deduction = home_loan_installs.aggregate(total=Sum('deduction'))['total']

        html_body += "<tr><th>Total</th><td></td><th class='text-right'>" + str(total_deduction) + "</th></tr></tbody><table>"
        html_extra = SalarySheetQueryGeneration.employee_details_section(employee)
        html_extra += HomeLoanOperations.get_home_loan_section(home_loan)
        html = {'body': html_body, 'extra': html_extra

        }
        return {'html': html}

    @staticmethod
    def get_home_loan_section(home_loan):
        html = "<div class='home-loan-details-section panel panel-default'><div " \
               "class='panel-heading'>Home Loan - " + str(home_loan.id) + "</div><div " \
                                                                              "class='panel-body'>"
        html += "<div class='col-sm-4'><table>"
        html += "<tr><td class='label'>Amount : </td><td>" + str(home_loan.amount) + "</td></tr>"
        html += "<tr><td class='label'>Date: </td><td>" + str(home_loan.date) + "</td></tr></table></div>"
        html += "<div class='col-sm-4'><table>"
        html += "<tr><td class='label'>No of Installments : </td><td>" + str(
            home_loan.no_of_installments) + "</td></tr>"
        html += "<tr><td class='label'>Monthly Payment : </td><td>" + str(
            home_loan.monthly_payment) + "</td></tr></table></div>"
        html += "<div class='col-sm-4'><table><tr><td class='label'>Closing Date :  </td><td>" + str(
            home_loan.closing_date) + "</td></tr>"
        html += "<tr><td class='label'>Closed: </td><td>" + str(home_loan.is_closed) + "</td></tr>"
        html += "</table></div></div></div>"
        return html







