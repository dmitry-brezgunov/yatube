from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail

User = get_user_model()


class CreationForm(UserCreationForm):
    '''Форма регистрации пользователя'''
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def send_email(self):
        email = self.cleaned_data['email']
        send_mail('Подтверждение регистрации Yatube', 'Вы зарегистрированы!',
                  'Yatube.ru <admin@yatube.ru>', [email], fail_silently=False)
