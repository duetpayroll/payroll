from allauth.account.views import SignupView, LoginView, LogoutView, PasswordChangeView


class LoginView(LoginView):
    template_name = 'account/login.html'

class LogoutView(LoginView):
    template_name = 'account/logout.html'

class PasswordChangeView(PasswordChangeView):
    template_name = 'account/password_change.html'