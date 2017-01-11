from django.conf.urls import url
from .views import *
from wkhtmltopdf.views import PDFTemplateView

urlpatterns = [
    url(r'^$', EmployeeProfile.as_view(), name='employee-profile'),
    url(r'^profile/edit/$', EmployeeProfileUpdate.as_view(), name='employee-profile-update'),

    url(r'^allowanceDeductions/$', EmployeeAllowanceDeductionList.as_view(), name='employee-allowance-deduction-list'),

####################################### Salary Sheet ######################################################

    url(r'^salaryLists/$', EmployeeSalaryList.as_view(), name='employee-salary-list'),
    url(r'^salaryStatement/$', EmployeeSalarySheetQueryView.as_view(), name='employee-salary-statement'),
    url(r'^employees/salarySheets/detail/(?P<pk>\d+)/$', EmployeeSalarySheetDetail.as_view(), name='employee-salary-sheet-detail'),

####################################### Provident Fund ###################################################

    url(r'^gpfMonthlyLogs/$', EmployeeProvidentFundDetail.as_view(), name='employee-gpf-monthly-logs'),
    url(r'^providentFund/summary$', EmployeeGPFSummaryView.as_view(), name='employee-gpf-summary'),
    url(r'^gpfMonthlyLogs/detail/(?P<pk>\d+)$', EmployeeProvidentFundMonthlySubscriptionDetail.as_view(),
        name='employee-gpf-monthly-subscription-detail'),

########################################### provident fund advance ###################################

    url(r'^providentFundAdvances/$', EmployeeProvidentFundAdvanceList.as_view(), name='employee-gpf-advance-list'),
    url(r'^providentFundAdvances/detail/(?P<pk>\d+)/$', EmployeeProvidentFundAdvanceDetail.as_view(),
        name='employee-gpf-advance-detail'),
    url(r'^providentFundAdvances/instalmentDetail/(?P<pk>\d+)$', EmployeeGPFAdvanceInstalmentDetail.as_view(),
        name='employee-gpf-advance-instalment-detail'),
    url(r'^gpfAdvanceSummary/$', EmployeeGPFAdvanceSummaryView.as_view(), name='employee-gpf_advance_summary'),
    url(r'^providentFundAdvances/(?P<pk>\d+)$', EmployeeGPFAdvanceDetailSummaryView.as_view(),
        name='employee-gpf-advance-detail-summary'),

################################################## home loan ##################################
    url(r'^homeLoan/$', EmployeeHomeLoanList.as_view(), name='employee-home-loan-list'),
    url(r'^homeLoan/detail/(?P<pk>\d+)/$', EmployeeHomeLoanDetail.as_view(),
        name='employee-home-loan-detail'),
    url(r'^homeLoan/instalmentDetail/(?P<pk>\d+)$', EmployeeHomeLoanInstalmentDetail.as_view(),
        name='employee-home-loan-instalment-detail'),
    url(r'^homeLoan/(?P<pk>\d+)$', EmployeeHomeLoanDetailSummaryView.as_view(),
            name='employee-home-loan-detail-summary'),

]
