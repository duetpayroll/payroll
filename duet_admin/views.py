from django.shortcuts import render, redirect
from django.views.generic import DetailView, DeleteView, View
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView

from .forms import EmployeeCreateForm, EmployeeUpdateForm, AssignUserToGroupForm

from django.contrib.auth.models import Group
from .models import Department, Settings
from employee.models import Employee, Designation
from duet_account.models import AllowanceDeduction, Grade, EmployeeClass, SalaryScale

from .utils import CustomTableView, CustomUpdateView, CustomCreateView, LoginAndAdminRequired, LoginAndSuperuserRequired


####################################### Allowance Deduction ###############################################

class AllowanceDeductionList(LoginAndAdminRequired, CustomTableView):
    model = AllowanceDeduction
    template_name = 'duet_admin/list.html'
    fields = ['name', 'code', 'category', 'is_applicable']
    filter_fields = {'name': ['icontains'], 'category': ['exact'], }

    actions = [
        {'url': 'duet_admin:allowancededuction-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:allowancededuction-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:allowancededuction-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Pay, Allowance and Deduction List'

    add_link = [{'url': 'duet_admin:allowancededuction-create', 'icon': 'glyphicon glyphicon-plus'}]


class AllowanceDeductionCreate(LoginAndAdminRequired, CustomCreateView):
    model = AllowanceDeduction
    fields = ['name', 'code', 'description', 'category', 'is_percentage', 'is_applicable', 'payment_type']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:allowancededuction-list'
    title = 'Create New Pay, Allowance or Deduction '
    success_message = 'A New Pay/Allowance/Deduction Has Been Created'


class AllowanceDeductionUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = AllowanceDeduction
    fields = ['name', 'code', 'description', 'category', 'is_percentage', 'is_applicable', 'payment_type']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:allowancededuction-list'
    title = 'Edit - '
    success_message = 'The Pay/Allowance/Deduction Has Been Updated'


class AllowanceDeductionDetail(LoginAndAdminRequired, DetailView):
    model = AllowanceDeduction
    template_name = 'duet_admin/allowanceDeduction/detail.html'
    context_object_name = 'allowanceDeduction'


class AllowanceDeductionDelete(LoginAndAdminRequired, DeleteView):
    model = AllowanceDeduction
    success_url = reverse_lazy('duet_admin:allowancededuction-list')
    template_name = 'duet_admin/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, 'common/protection_error.html')


####################################### Employee ##############################################################


class EmployeeCreate(LoginAndAdminRequired, CustomCreateView):
    template_name = 'duet_admin/create.html'
    form_class = EmployeeCreateForm
    model = Employee
    title = 'Create New Employee'
    cancel_url = 'duet_admin:employee-list'


class EmployeeList(LoginAndAdminRequired, CustomTableView):
    model = Employee
    template_name = 'duet_admin/list.html'

    fields = ['id', 'first_name', 'last_name', 'email', 'department',
              'designation', 'category']
    filter_fields = {'designation': ['exact'], 'category': ['exact'], 'department': ['exact']}

    actions = [{'url': 'duet_admin:employee-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:employee-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:employee-assign-to-group', 'icon': 'glyphicon glyphicon-user','tooltip': 'Assign To Groups'},
        {'url': 'duet_admin:employee-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Employee List'

    add_link = [{'url': 'duet_admin:employee-create', 'icon': 'glyphicon glyphicon-plus'}]


class EmployeeUpdate(LoginAndAdminRequired, CustomUpdateView):
    template_name = 'duet_admin/create.html'
    model = Employee
    form_class = EmployeeUpdateForm
    cancel_url = 'duet_admin:employee-list'
    title = 'Edit -  '
    success_message = 'New Employee Has Been Created'


class EmployeeDetail(LoginAndAdminRequired, DetailView):
    model = Employee
    template_name = 'duet_admin/employee/detail.html'
    context_object_name = 'employee'


class EmployeeDelete(LoginAndAdminRequired, DeleteView):
    model = Employee
    success_url = reverse_lazy('duet_admin:employee-list')
    template_name = 'duet_admin/confirm_delete.html'


####################################### Department ##############################################################

class DepartmentList(LoginAndAdminRequired, CustomTableView):
    model = Department
    template_name = 'duet_admin/list.html'

    fields = ['name', 'acronym', 'code', 'type']
    filter_fields = {'name': ['icontains'], 'type': ['exact'], }

    actions = [{'url': 'duet_admin:department-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:department-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:department-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Department List'

    add_link = [{'url': 'duet_admin:department-create', 'icon': 'glyphicon glyphicon-plus'}]


class DepartmentCreate(LoginAndAdminRequired, CustomCreateView):
    model = Department
    fields = ['name', 'code', 'acronym', 'description', 'type']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:department-list'
    title = 'Create New Department  '


class DepartmentUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = Department
    fields = ['name', 'code', 'acronym', 'description', 'type']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:department-list'
    title = 'Edit -  '


class DepartmentDetail(LoginAndAdminRequired, DetailView):
    model = Department
    template_name = 'duet_admin/department/detail.html'
    context_object_name = 'department'


class DepartmentDelete(LoginAndAdminRequired, DeleteView):
    model = Department
    success_url = reverse_lazy('duet_admin:department-list')
    template_name = 'duet_admin/confirm_delete.html'


####################################### Designation ##############################################################


class DesignationList(LoginAndAdminRequired, CustomTableView):
    model = Designation
    template_name = 'duet_admin/list.html'

    fields = ['name', 'created_at', 'modified_at']
    filter_fields = {'name': ['icontains'] }

    actions = [{'url': 'duet_admin:designation-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:designation-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:designation-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Designation List'

    add_link = [{'url': 'duet_admin:designation-create', 'icon': 'glyphicon glyphicon-plus'}]


class DesignationCreate(LoginAndAdminRequired, CustomCreateView):
    model = Designation
    fields = ['name', 'description']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:designation-list'
    title = 'Create New Designation'


class DesignationUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = Designation
    fields = ['name', 'description']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:designation-list'
    title = 'Edit -  '


class DesignationDetail(LoginAndAdminRequired, DetailView):
    model = Designation
    template_name = 'duet_admin/designation/detail.html'
    context_object_name = 'designation'


class DesignationDelete(LoginAndAdminRequired, DeleteView):
    model = Designation
    success_url = reverse_lazy('duet_admin:designation-list')
    template_name = 'duet_admin/confirm_delete.html'


####################################### Grade ###############################################


class SalaryScaleDetail(LoginAndAdminRequired, CustomTableView):
    model = Grade
    template_name = 'duet_admin/list.html'

    fields = ['grade_no', 'employee_class', 'description',]
    filter_fields = {'grade_no': ['exact'], }

    actions = [{'url': 'duet_admin:grade-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:grade-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:grade-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Grade List'

    add_link = []

    def get(self, request, *args, **kwargs):
        self.salary_scale = SalaryScale.objects.get(slug=kwargs.pop('slug'))
        new_grade_link = {'icon' : 'glyphicon glyphicon-plus',
                          'url' : 'duet_admin:grade-create',
                          'slug' : self.salary_scale.slug}
        if len(self.add_link) == 0:
            self.add_link.append(new_grade_link)
        return super().get(request, args, kwargs)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(salary_scale=self.salary_scale)


class GradeCreate(LoginAndAdminRequired, CustomCreateView):
    model = Grade
    fields = ['grade_no', 'description', 'employee_class']
    template_name = 'duet_admin/create.html'
    title = 'Create New Grade'

    def get(self, request, *args, **kwargs):
        self.salaryScale = SalaryScale.objects.get(slug=kwargs.pop('slug'))
        self.title = 'Create New Grade For ' + self.salaryScale.name
        return super(GradeCreate, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('duet_admin:salary-scale-detail', kwargs={'slug': self.salaryScale.slug})

    def post(self, request, *args, **kwargs):
        self.salaryScale = SalaryScale.objects.get(slug=kwargs.pop('slug'))
        return super(GradeCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.salary_scale = self.salaryScale
        return super().form_valid(form)


class GradeUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = Grade
    fields = ['grade_no', 'description', 'employee_class']
    template_name = 'duet_admin/create.html'
    title = 'Edit -  '

    def get_success_url(self):
        return reverse_lazy('duet_admin:salary-scale-detail', kwargs={'slug': self.salaryScale.slug})

    def post(self, request, *args, **kwargs):
        grade = self.get_object()
        self.salaryScale = grade.salary_scale
        return super().post(request, *args, **kwargs)


class GradeDetail(LoginAndAdminRequired, DetailView):
    model = Grade
    template_name = 'duet_admin/grade/detail.html'
    context_object_name = 'grade'


class GradeDelete(LoginAndAdminRequired, DeleteView):
    model = Grade
    template_name = 'duet_admin/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('duet_admin:salary-scale-detail', kwargs={'slug': self.salaryScale.slug})

    def post(self, request, *args, **kwargs):
        grade = self.get_object()
        self.salaryScale = grade.salary_scale
        return super().post(request, *args, **kwargs)


####################################### SalaryScale ###############################################


class SalaryScaleList(LoginAndAdminRequired, CustomTableView):
    model = SalaryScale
    template_name = 'duet_admin/list.html'

    fields = ['name', 'date', 'is_active', 'created_at', 'modified_at']
    filter_fields = {'name': ['icontains'], }

    actions = [{'url': 'duet_admin:salary-scale-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:salary-scale-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:salary-scale-active', 'icon': 'glyphicon glyphicon-ok', 'tooltip': 'Make Active'},
        {'url': 'duet_admin:salary-scale-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Salary Scale List'

    add_link = [{'url': 'duet_admin:salary-scale-create', 'icon': 'glyphicon glyphicon-plus'}]


class SalaryScaleCreate(LoginAndAdminRequired, CustomCreateView):
    model = SalaryScale
    fields = ['name', 'date']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:salary-scale-list'
    title = 'Create Salary Scale'


class SalaryScaleUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = SalaryScale
    fields = ['name', 'date']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:salary-scale-list'
    title = 'Edit -  '


class SalaryScaleDelete(LoginAndAdminRequired, DeleteView):
    model = SalaryScale
    success_url = reverse_lazy('duet_admin:salary-scale-list')
    template_name = 'duet_admin/confirm_delete.html'


class SalaryScaleActive(LoginAndAdminRequired, SingleObjectTemplateResponseMixin, BaseDetailView):
    model = SalaryScale
    template_name = 'duet_admin/salaryScale/confirm_active.html'

    def post(self, *args, **kwargs):
        salary_scale = self.get_object()
        SalaryScale.objects.all().update(is_active =False)
        salary_scale.is_active = True
        salary_scale.save()
        return redirect('duet_admin:salary-scale-list')


####################################### Employee Class ######################################################################


class EmployeeClassList(LoginAndAdminRequired, CustomTableView):
    model = EmployeeClass
    template_name = 'duet_admin/list.html'

    exclude = ['id']
    filter_fields = {'name': ['icontains'], }

    actions = [{'url': 'duet_admin:employee-class-detail', 'icon': 'glyphicon glyphicon-th-large', 'tooltip': 'Detail'},
        {'url': 'duet_admin:employee-class-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:employee-class-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'Employee Class List'

    add_link = [{'url': 'duet_admin:employee-class-create', 'icon': 'glyphicon glyphicon-plus'}]


class EmployeeClassCreate(LoginAndAdminRequired, CustomCreateView):
    model = EmployeeClass
    fields = ['name', 'description']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:employee-class-list'
    title = 'Create New Employee Class'


class EmployeeClassUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = EmployeeClass
    fields = ['name', 'description']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:employee-class-list'
    title = 'Edit -  '


class EmployeeClassDetail(LoginAndAdminRequired, DetailView):
    model = EmployeeClass
    template_name = 'duet_admin/employeeClass/detail.html'
    context_object_name = 'employeeClass'


class EmployeeClassDelete(LoginAndAdminRequired, DeleteView):
    model = EmployeeClass
    success_url = reverse_lazy('duet_admin:employee-class-list')
    template_name = 'duet_admin/confirm_delete.html'


####################################### Setting ######################################################################


class SettingsList(LoginAndAdminRequired, CustomTableView):
    model = Settings
    template_name = 'duet_admin/list.html'

    exclude = ['id', 'code']
    filter_fields = {'name': ['icontains'], }

    actions = [{'url': 'duet_admin:setting-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'} ]

    title = 'Settings'


class SettingUpdate(LoginAndAdminRequired, CustomUpdateView):
    model = Settings
    fields = ['value']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:setting-list'
    title = 'Edit -  '


####################################### User Group #######################################################################

class UserGroupList(LoginAndAdminRequired, CustomTableView):
    model = Group
    template_name = 'duet_admin/list.html'
    exclude = ['id']
    filter_fields = {'name': ['icontains'] }

    actions = [
        {'url': 'duet_admin:user-group-update', 'icon': 'glyphicon glyphicon-pencil', 'tooltip': 'Update'},
        {'url': 'duet_admin:user-group-delete', 'icon': 'glyphicon glyphicon-trash', 'tooltip': 'Delete'}, ]

    title = 'User Group List'

    add_link = [{'url': 'duet_admin:user-group-create', 'icon': 'glyphicon glyphicon-plus'}]


class UserGroupCreate(LoginAndSuperuserRequired, CustomCreateView):
    model = Group
    fields = ['name']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:user-group-list'
    success_url = reverse_lazy('duet_admin:user-group-list')
    title = 'Create New User '


class UserGroupUpdate(LoginAndSuperuserRequired, CustomUpdateView):
    model = Group
    fields = ['name']
    template_name = 'duet_admin/create.html'
    cancel_url = 'duet_admin:user-group-list'
    success_url = reverse_lazy('duet_admin:user-group-list')
    title = 'Edit - '


class UserGroupDelete(LoginAndSuperuserRequired, DeleteView):
    model = Group
    success_url = reverse_lazy('duet_admin:user-group-list')
    template_name = 'duet_admin/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, 'common/protection_error.html')


class AssignUserToGroup (LoginAndAdminRequired, CustomUpdateView):
    template_name = 'duet_admin/create.html'
    form_class = AssignUserToGroupForm
    model = Employee
    cancel_url = 'duet_admin:employee-list'
    title = 'Assign Employee To Groups -'



