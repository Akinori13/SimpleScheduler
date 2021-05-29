from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAnonymousUserMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self) -> bool:
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        return redirect('accounts:home')

