from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', EmployeeList.as_view(), name = 'employee-list'),
    url(r'^allowanceDeductions/$', AllowanceDeductionList.as_view(), name = 'allowancededuction-list'),
    url(r'^allowanceDeductions/create/$', AllowanceDeductionCreate.as_view(), name = 'allowancededuction-create'),
    url(r'^allowanceDeductions/(?P<slug>[-\w]+)/$', AllowanceDeductionDetail.as_view(), name = 'allowancededuction-detail'),
    url(r'^allowanceDeductions/update/(?P<slug>[-\w]+)/$', AllowanceDeductionUpdate.as_view(), name = 'allowancededuction-update'),
    url(r'^allowanceDeductions/delete/(?P<slug>[-\w]+)/$', AllowanceDeductionDelete.as_view(), name = 'allowancededuction-delete'),
  
    url(r'^departments/$', DepartmentList.as_view(), name = 'department-list'),
    url(r'^departments/create/$', DepartmentCreate.as_view(), name = 'department-create'),
    url(r'^departments/(?P<slug>[-\w]+)/$', DepartmentDetail.as_view(), name = 'department-detail'),
    url(r'^departments/update/(?P<slug>[-\w]+)/$', DepartmentUpdate.as_view(), name = 'department-update'),
    url(r'^departments/delete/(?P<slug>[-\w]+)/$', DepartmentDelete.as_view(), name = 'department-delete'),

    url(r'^designations/$', DesignationList.as_view(), name = 'designation-list'),
    url(r'^designations/create/$', DesignationCreate.as_view(), name = 'designation-create'),
    url(r'^designations/(?P<slug>[-\w]+)/$', DesignationDetail.as_view(), name = 'designation-detail'),
    url(r'^designations/update/(?P<slug>[-\w]+)/$', DesignationUpdate.as_view(), name = 'designation-update'),
    url(r'^designations/delete/(?P<slug>[-\w]+)/$', DesignationDelete.as_view(), name = 'designation-delete'),

    url(r'^employees/create/$', EmployeeCreate.as_view(), name = 'employee-create'),
    url(r'^employees/$', EmployeeList.as_view(), name = 'employee-list'),
    url(r'^employees/(?P<slug>[-\w]+)/$', EmployeeDetail.as_view(), name = 'employee-detail'),
    url(r'^employees/update/(?P<slug>[-\w]+)/$', EmployeeUpdate.as_view(), name = 'employee-update'),
    url(r'^employees/delete/(?P<slug>[-\w]+)/$', EmployeeDelete.as_view(), name = 'employee-delete'),
    url(r'^employees/assignToGroups/(?P<slug>[-\w]+)/$', AssignUserToGroup.as_view(), name='employee-assign-to-group'),

    url(r'^salaryScale/create/$', SalaryScaleCreate.as_view(), name = 'salary-scale-create'),
    url(r'^salaryScale/$', SalaryScaleList.as_view(), name = 'salary-scale-list'),
    url(r'^salaryScale/(?P<slug>[-\w]+)/$', SalaryScaleDetail.as_view(), name = 'salary-scale-detail'),
    url(r'^salaryScale/update/(?P<slug>[-\w]+)/$', SalaryScaleUpdate.as_view(), name = 'salary-scale-update'),
    url(r'^salaryScale/delete/(?P<slug>[-\w]+)/$', SalaryScaleDelete.as_view(), name = 'salary-scale-delete'),
    url(r'^salaryScale/active/(?P<slug>[-\w]+)/$', SalaryScaleActive.as_view(), name = 'salary-scale-active'),

    url(r'^salaryScale/createGrade/(?P<slug>[-\w]+)$', GradeCreate.as_view(), name = 'grade-create'),
    url(r'^grades/(?P<slug>[-\w]+)/$', GradeDetail.as_view(), name = 'grade-detail'),
    url(r'^grades/update/(?P<slug>[-\w]+)/$', GradeUpdate.as_view(), name = 'grade-update'),
    url(r'^grades/delete/(?P<slug>[-\w]+)/$', GradeDelete.as_view(), name = 'grade-delete'), 

    url(r'^employeeClasses/create/$', EmployeeClassCreate.as_view(), name = 'employee-class-create'),
    url(r'^employeeClasses/$', EmployeeClassList.as_view(), name = 'employee-class-list'),
    url(r'^employeeClasses/(?P<slug>[-\w]+)/$', EmployeeClassDetail.as_view(), name = 'employee-class-detail'),
    url(r'^employeeClasses/update/(?P<slug>[-\w]+)/$', EmployeeClassUpdate.as_view(), name = 'employee-class-update'),
    url(r'^employeeClasses/delete/(?P<slug>[-\w]+)/$', EmployeeClassDelete.as_view(), name = 'employee-class-delete'),

    url(r'^settings/$', SettingsList.as_view(), name = 'setting-list'),
    url(r'^settings/update/(?P<pk>\d+)/$', SettingUpdate.as_view(), name ='setting-update'),

    url(r'^userGroup/create/$', UserGroupCreate.as_view(), name='user-group-create'),
    url(r'^userGroup/$', UserGroupList.as_view(), name='user-group-list'),
    url(r'^userGroup/update/(?P<pk>\d+)/$', UserGroupUpdate.as_view(), name='user-group-update'),
    url(r'^userGroup/delete/(?P<pk>\d+)/$', UserGroupDelete.as_view(), name='user-group-delete'),


]