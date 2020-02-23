from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


# создадим собственный класс для формы регистрации
# сделаем его наследником предустановленного класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # модель уже существует, сошлёмся на неё
        model = User
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ("first_name", "last_name", "username", "email")
    def send_email(self):
        email = self.cleaned_data['email']
        send_mail('Подтверждение регистрации Yatube', 'Вы зарегистрированы!', 'Yatube.ru <admin@yatube.ru>', [email], fail_silently=False)
