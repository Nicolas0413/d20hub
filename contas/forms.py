from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class SignupForm(UserCreationForm):

    class Meta:

        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = _('Digite seu nome de usuário')
        self.fields['email'].widget.attrs['placeholder'] = 'Digite seu email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Digite sua senha'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirme sua senha'
