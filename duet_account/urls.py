from django.conf.urls import url
from .views import EmployeeList
from .allowanceDeduction import ConfigureAllowanceDeduction, ConfigureAllowanceDeductionEmployeeClassValue, \
    AllowanceDeductionDetail, AllowanceDeductionList, AllowanceDeductionUpdate, ConfigureEmployeeAllowanceDeduction

from .providentFund import ProvidentFundProfileUpdate, ProvidentFundProfileDetail, GPFYearlyLogs, GPFYearlyLogCreate, \
    ProvidentFundAdvanceList, ProvidentFundMonthlySubscriptionDetail, ProvidentFundAdvanceCreate, \
    ProvidentFundAdvanceUpdate, AccountProvidentFundAdvanceDetail, GPFAdvanceDelete, GPFAdvanceConfirm, \
    GPFAdvanceClose, GPFAdvanceInstalmentDetail, GPFYearlyLogConfirm, GPFYearlyLogDelete, GPFYearlyLogUpdate, \
    GPFAdvanceSummaryView, GPFSummaryView, GPFAdvanceDetailSummaryView

from .salarySheet import SalarySheetCreate, SalarySheetUpdate, AccountSalarySheetDetail, SalarySheetConfirm, \
    SalarySheetDelete, EmployeeSalarySheetList,SalarySheetQuerySummaryAndDetailsView, SalarySheetQueryView, \
    SalarySheetQuerySummaryAndDetailsRangeView, AccountSalarySheetDetailEmployeeBase, SalarySheetDetailPdf

from .homeLoan import HomeLoanList, HomeLoanCreate, HomeLoanUpdate, HomeLoanDetail, HomeLoanDelete, HomeLoanConfirm, \
    HomeLoanClose, HomeLoanInstalmentDetail, HomeLoanDetailSummaryView

urlpatterns = [
    url(r'^$', EmployeeList.as_view(), name = 'employee-list'),
    url(r'^employees/manageAllowanceDeductions/(?P<slug>[-\w]+)/$', ConfigureEmployeeAllowanceDeduction.as_view(), name = 'configure-employee-allowance-deduction'),
    url(r'^employees/(?P<slug>[-\w]+)/$', EmployeeSalarySheetList.as_view(), name ='employee-detail'),
    url(r'^employees/$', EmployeeList.as_view(), name = 'employee-list'),

########################################## GPF  #####################################################

    url(r'^employees/providentFund/edit/(?P<slug>[-\w]+)/$', ProvidentFundProfileUpdate.as_view(), name = 'provident-fund-profile-update'),
    url(r'^employees/providentFund/detail/(?P<slug>[-\w]+)/$', ProvidentFundProfileDetail.as_view(), name ='provident-fund-profile-detail'),
    url(r'^providentFunds/montlySubscriptionLogs/detail/(?P<pk>\d+)/$',
        ProvidentFundMonthlySubscriptionDetail.as_view(), name='gpf-monthly-subscription-detail'),
    url(r'^providentFunds/summary/(?P<slug>[-\w]+)/$', GPFSummaryView.as_view(), name='gpf-summary'),

########################################## GPF Yearly Log #####################################################

    url(r'^employees/providentFund/gpfYearlyLog/(?P<slug>[-\w]+)/$', GPFYearlyLogs.as_view(),name ='gpf-yearly-log'),
    url(r'^employees/providentFund/gpfYearlyLog/create/(?P<slug>[-\w]+)/$', GPFYearlyLogCreate.as_view(),name ='create-gpf-yearly-log'),
    url(r'^employees/providentFund/gpfYearlyLog/freeze/(?P<pk>\d+)/$', GPFYearlyLogConfirm.as_view(), name = 'gpf-yearly-log-confirm'),
    url(r'^employees/providentFund/gpfYearlyLog/delete/(?P<pk>\d+)/$', GPFYearlyLogDelete.as_view(), name = 'gpf-yearly-log-delete'),
    url(r'^employees/providentFund/gpfYearlyLog/update/(?P<pk>\d+)/$', GPFYearlyLogUpdate.as_view(), name = 'gpf-yearly-log-update'),

########################################## Salary Sheet #####################################################

    url(r'^employees/GenerateSalarySheet/(?P<slug>[-\w]+)/$', SalarySheetCreate.as_view(), name = 'generate-salary-sheet'),
   	url(r'^salarySheets/update/(?P<pk>\d+)/$', SalarySheetUpdate.as_view(), name = 'salary-sheet-update'),
   	url(r'^salarySheets/delete/(?P<pk>\d+)/$', SalarySheetDelete.as_view(), name = 'salary-sheet-delete'),
   	url(r'^salarySheets/detail/(?P<pk>\d+)/$', AccountSalarySheetDetail.as_view(), name ='salary-sheet-detail'),
   	url(r'^salarySheets/downloadPdf/(?P<pk>\d+)/$', SalarySheetDetailPdf.as_view(), name ='salary-sheet-detail-pdf'),
   	url(r'^employees/salarySheets/detail/(?P<pk>\d+)/$', AccountSalarySheetDetailEmployeeBase.as_view(),
        name ='salary-sheet-detail-employee-base'),
    url(r'^salarySheets/freeze/(?P<pk>\d+)/$', SalarySheetConfirm.as_view(), name = 'salary-sheet-confirm'),
    url(r'^salarySheets/query/(?P<slug>[-\w]+)/$', SalarySheetQueryView.as_view(), name = 'salary-sheet-query'),
    url(r'^salarySheets/query/month$', SalarySheetQuerySummaryAndDetailsView.as_view(),
        name='salary-sheet-query-summary-details'),
    url(r'^salarySheets/query/range$', SalarySheetQuerySummaryAndDetailsRangeView.as_view(),
        name='salary-sheet-query-summary-details-range'),

########################################## Allowance Deduction #####################################################

   	url(r'^allowanceDeductions/$', AllowanceDeductionList.as_view(), name = 'allowance-deduction-list'),
    url(r'^allowanceDeductions/(?P<slug>[-\w]+)/$', AllowanceDeductionDetail.as_view(), name = 'allowance-deduction-detail'),
   	url(r'^allowanceDeductions/edit/(?P<slug>[-\w]+)/$', AllowanceDeductionUpdate.as_view(), name = 'allowance-deduction-update'),
   	url(r'^allowanceDeductions/ConfigureValuesForEmployeeClass/(?P<slug>[-\w]+)/$', ConfigureAllowanceDeductionEmployeeClassValue.as_view(), name = 'configure-allowance-deduction-employee-class'),
   	url(r'^allowanceDeductions/ConfigureAllowancesDeductions$', ConfigureAllowanceDeduction.as_view(), name = 'configure-allowance-deduction'),

############################ GPF Advance #####################################

    url(r'^employees/providentFund/advances/(?P<slug>[-\w]+)/$', ProvidentFundAdvanceList.as_view(), name='gpf-advance-list'),
    url(r'^employees/providentFunds/createAdvance/(?P<slug>[-\w]+)/$', ProvidentFundAdvanceCreate.as_view(), name = 'gpf-new-advance'),
    url(r'^providentFunds/advances/edit/(?P<pk>\d+)/$', ProvidentFundAdvanceUpdate.as_view(), name = 'gpf-advance-update'),
    url(r'^providentFunds/advances/detail/(?P<pk>\d+)/$', AccountProvidentFundAdvanceDetail.as_view(), name ='gpf-advance-detail'),
    url(r'^providentFunds/advances/delete/(?P<pk>\d+)/$', GPFAdvanceDelete.as_view(), name = 'gpf-advance-delete'),
    url(r'^providentFunds/advances/freeze/(?P<pk>\d+)/$', GPFAdvanceConfirm.as_view(), name='gpf-advance-freeze'),
    url(r'^providentFunds/advances/close/(?P<pk>\d+)/$', GPFAdvanceClose.as_view(), name='gpf-advance-close'),
    url(r'^providentFunds/advances/installment/detail/(?P<pk>\d+)/$', GPFAdvanceInstalmentDetail.as_view(), name = 'gpf-advance-installment-detail'),
    url(r'^providentFunds/advanceSummary/(?P<slug>[-\w]+)/$', GPFAdvanceSummaryView.as_view(),
        name='gpf_advance_summary'),
    url(r'^providentFunds/advance/(?P<pk>\d+)$', GPFAdvanceDetailSummaryView.as_view(),
        name='gpf-advance-detail-summary'),

############################ Home Loan #####################################

    url(r'^employees/homeLoan/(?P<slug>[-\w]+)/$', HomeLoanList.as_view(),name='home-loan-list'),
    url(r'^employees/homeLoan/create/(?P<slug>[-\w]+)/$', HomeLoanCreate.as_view(),name='home-loan-create'),
    url(r'^employees/homeLoan/edit/(?P<pk>\d+)/$', HomeLoanUpdate.as_view(),name='home-loan-edit'),
    url(r'^employees/homeLoan/detail/(?P<pk>\d+)/$', HomeLoanDetail.as_view(),name='home-loan-detail'),
    url(r'^employees/homeLoan/delete/(?P<pk>\d+)/$', HomeLoanDelete.as_view(),name='home-loan-delete'),
    url(r'^employees/homeLoan/freeze/(?P<pk>\d+)/$', HomeLoanConfirm.as_view(),name='home-loan-freeze'),
    url(r'^employees/homeLoan/close/(?P<pk>\d+)/$', HomeLoanClose.as_view(),name='home-loan-close'),
    url(r'^employees/homeLoan/installment/detail/(?P<pk>\d+)/$', HomeLoanInstalmentDetail.as_view(),name = 'home-loan-installment-detail'),
    url(r'^homeLoan/(?P<pk>\d+)$', HomeLoanDetailSummaryView.as_view(),name='home-loan-detail-summary'),
]



