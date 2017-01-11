from django.views.generic import FormView

from duet_admin.utils import LoginAndAccountantRequired
from employee.models import Employee


class EmployeeQueryFormView(LoginAndAccountantRequired, FormView):
    query_template_name = 'report/query.html'

    def get(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        self.employee = Employee.objects.get(slug=kwargs.pop('slug'))
        return super().post(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context