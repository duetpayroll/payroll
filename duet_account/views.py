from employee.models import Employee

from duet_admin.utils import CustomTableView, LoginAndAccountantRequired


class EmployeeList(LoginAndAccountantRequired, CustomTableView):
	model = Employee
	template_name = 'duet_account/list.html'

	fields = ['id', 'first_name', 'last_name', 'email', 'contact', 'department', 'designation', 'category']
	filter_fields = {'designation': ['exact'], 'category': ['exact'], 'department': ['exact'], 'first_name': [
		'icontains']}
	actions = [
		{'url':'duet_account:generate-salary-sheet', 'icon':'glyphicon glyphicon-usd', 'tooltip':'Generate Salary Sheet'},
		{'url':'duet_account:configure-employee-allowance-deduction', 'icon':'glyphicon glyphicon-cog', 'tooltip':'Configure Default Values'},
		{'url':'duet_account:employee-detail', 'icon':'glyphicon glyphicon-th-large', 'tooltip':'Detail'},
	]

	title = 'Employee List'



