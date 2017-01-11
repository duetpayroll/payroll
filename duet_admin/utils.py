from django_tables2 import SingleTableView
import django_tables2 as tables
from django.db import models
import django_filters as filters
from django import forms
from crispy_forms.helper import FormHelper
from django.views.generic import CreateView, UpdateView, View, TemplateView
from django.contrib import messages
from wkhtmltopdf.views import PDFTemplateResponse

from braces.views import GroupRequiredMixin, LoginRequiredMixin, SuperuserRequiredMixin

from duet_account.models import SalaryScale, Grade


class CustomUpdateView(UpdateView):
	success_message = ''

	def form_valid(self, form):
		response = super().form_valid(form)
		success_message = self.get_success_message(form.cleaned_data)
		if success_message:
			messages.success(self.request, success_message)
		return response

	def get_success_message(self, cleaned_data):
		return self.success_message % cleaned_data

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		if hasattr(self, 'title'):
			context['title'] = self.title
		if hasattr(self, 'cancel_url'):
			context['cancel_url'] = self.cancel_url
		return context


class CustomCreateView(CreateView):
	success_message = ''

	def form_valid(self, form):
		response = super().form_valid(form)
		success_message = self.get_success_message(form.cleaned_data)
		if success_message:
			messages.success(self.request, success_message)
		return response

	def get_success_message(self, cleaned_data):
		return self.success_message % cleaned_data

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		if hasattr(self, 'title'):
			context['title'] = self.title
		if hasattr(self, 'cancel_url'):
			context['cancel_url'] = self.cancel_url
		return context


class PageFilteredTableView(SingleTableView):
	filter_class = None
	formhelper_class = None
	context_filter_name = 'filter'

	def get_queryset(self, **kwargs):
		def get_filterset_class(self):
			attrs = dict()
			attrs['Meta'] = type('Meta', (), {'fields' : self.filter_fields, 'model': self.model})
			klass1 = type('Dfilter',(filters.FilterSet,), attrs)
			return klass1

		def get_form_class(self):
			attrs = dict()
			attrs['model'] = self.model
			attrs['form_tag'] = False
			attrs['help_text_inline'] = True
			attrs['form_class'] = 'form-horizontal'
			klass1 = type('Dform', (FormHelper,), attrs)
			return klass1

		qs = super().get_queryset()
		if hasattr(self, 'filter_fields'):
			self.formhelper_class = get_form_class(self)
			self.filter_class = get_filterset_class(self)
			self.filter = self.filter_class(self.request.GET, queryset = qs)
			self.filter.form.helper = self.formhelper_class()
			return self.filter.qs
		return qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		if hasattr(self, 'filter_fields'):
			context[self.context_filter_name] = self.filter
		return context


class AddTableMixin(object, ):
	table_pagination = {"per_page" : 15}

	def get_table_class(self):
		def get_table_column(field):
			if isinstance(field, models.DateTimeField):
				return tables.DateColumn("m/d/Y H:i")
			elif isinstance(field, models.DateField):
				return tables.DateColumn("m/d/Y")
			else:
				return tables.Column()

		if hasattr(self, 'fields'):
			attrs = dict(
			(field, get_table_column(field)) for
			field in self.fields
			)
		else:
			attrs = dict(
				(field.name, get_table_column(field)) for
				field in self.model._meta.fields if field.name not in self.exclude
				)

		metaAttrs = dict()
		metaAttrs['class'] = 'table'
		if hasattr(self, 'actions'):
			metaAttrs['actions'] = self.actions
		if hasattr(self, 'title'):
			metaAttrs['title'] = self.title
		if hasattr(self, 'add_link'):
			metaAttrs['add_link'] = self.add_link

		attrs['Meta'] = type('Meta', (), {'attrs' : metaAttrs})
		klass = type('Dtable', (tables.Table, ), attrs)
		return klass


class CustomTableView(AddTableMixin, PageFilteredTableView):
	"""

	"""


class AdminGroupRequiredMixin(GroupRequiredMixin):

	raise_exception = True
	group_required = u"admin"


class AccountantGroupRequiredMixin(GroupRequiredMixin):

	raise_exception = True
	group_required = u"accountant"


class LoginAndAdminRequired(LoginRequiredMixin, AdminGroupRequiredMixin):
	"""
	"""


class LoginAndAccountantRequired(LoginRequiredMixin, AccountantGroupRequiredMixin):
	"""
	"""


class LoginAndSuperuserRequired(LoginRequiredMixin, SuperuserRequiredMixin):
	raise_exception = True
	"""
	"""


class DownloadPDF(object,):
	@staticmethod
	def downloadPdf(request, template_name, file_name, context):
		response = PDFTemplateResponse(request=request, template=template_name, filename=file_name,
									   context=context, show_content_in_browser=False, cmd_options={'margin-top':
																										 50, })
		return response

class ValueFromListTuple(object):
	@staticmethod
	def get( list, key):
		for item in list:
			if item[0] is key:
				return item[1]
		return None


