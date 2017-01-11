from django import forms

from duet_account.models import Grade
from employee.models import Employee


class EmployeeCreateForm(forms.ModelForm):
    grade = forms.ModelChoiceField(label='Grade', queryset=Grade.objects.filter(salary_scale__is_active=True))

    class Meta:
        model = Employee
        fields = ['username', 'first_name', 'last_name', 'email', 'address', 'gender', 'dob', 'joining_date',
                  'designation', 'grade', 'department']
        widgets = {'dob': forms.DateInput(attrs={'class': 'date-picker'}),
            'joining_date': forms.DateInput(attrs={'class': 'date-picker'}), }

    def save(self, commit=True):
        # Save the provided password in hashed format
        employee = super().save(commit=False)
        employee.set_password("1234")
        if commit:
            employee.save()
        return employee


class EmployeeUpdateForm(forms.ModelForm):
    grade = forms.ModelChoiceField(label='Grade', queryset=Grade.objects.filter(salary_scale__is_active=True))

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'address', 'gender', 'dob', 'joining_date', 'designation',
                  'grade', 'department']

        widgets = {'dob': forms.DateInput(attrs={'class': 'date-picker'}),
                   'joining_date': forms.DateInput(attrs={'class': 'date-picker'}), }


class AssignUserToGroupForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['groups']
        widgets = {"groups": forms.CheckboxSelectMultiple()}
