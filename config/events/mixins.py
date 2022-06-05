from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class LoginRequiredMessageMixin(LoginRequiredMixin):
    permission_denied_message = 'You have to be logged in to access that page'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR,
                                 self.permission_denied_message)
            return self.handle_no_permission()
        return super(LoginRequiredMessageMixin, self).dispatch(
            request, *args, **kwargs
        )
