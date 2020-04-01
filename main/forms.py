from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.forms.formsets import formset_factory
from django.utils.translation import gettext_lazy as _

from .middlewares import help_text
from .models import user_registrated
from .models import *


class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'bb': forms.HiddenInput, 'author': forms.HiddenInput}


class GuestCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('is_active', 'content',)
        widgets = {'bb': forms.HiddenInput}


AIFormFileSet = inlineformset_factory(Subject, AdditionalFile, fields='__all__', extra=5)


class BbForm(forms.ModelForm):
    class Meta:
        model = Bb
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')


class SubGroupForm(forms.ModelForm):
    super_group = forms.ModelChoiceField(queryset=SuperGroup.objects.all(), empty_label=None,
                                         label='Форма обучения', required=True)

    class Meta:
        model = SubGroup
        fields = '__all__'


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not AdvUser.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("Пользователь с указанным адресом электронной почты не зарегистрирован!")
        return email


class RegisterTeacherForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин**', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя**', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия**', widget=forms.TextInput)
    middle_name = forms.CharField(required=True, label='Отчество**', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты**', widget=forms.EmailInput)
    password1 = forms.CharField(label='Пароль**', widget=forms.PasswordInput,
                                help_text=help_text())
    password2 = forms.CharField(label='Пароль (повторно)**', widget=forms.PasswordInput,
                                help_text='Повторите пароль')
    position = forms.CharField(required=True, label='Должность**', widget=forms.TextInput)
    degree = forms.CharField(required=False, label='Степень', widget=forms.TextInput)
    rank = forms.CharField(required=False, label='Звание', widget=forms.TextInput)

    is_teacher = forms.BooleanField(required=True, label='Преподаватель', initial=True, widget=forms.HiddenInput())

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        list_email = AdvUser.objects.filter(email=email)
        if list_email.count():
            raise ValidationError('Такой email уже зарегистрирован')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = AdvUser.objects.filter(username=username)
        if r.count():
            raise ValidationError("Такой логин уже существует")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data and \
                self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError("Введенные пароли не совпадают")
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        return user

    class Meta:
        model = Teacher
        fields = ('username', 'email', 'password1', 'password2', 'last_name', 'first_name', 'middle_name',
                  'position', 'degree', 'rank', 'send_messages', 'is_teacher')


class RegisterUserForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин**', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя**', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия**', widget=forms.TextInput)
    group = forms.ModelChoiceField(queryset=SubGroup.objects.all(), required=True, label='Группа*', )
    email = forms.EmailField(required=True, label='Адрес электронной почты**', widget=forms.EmailInput)
    password1 = forms.CharField(label='Пароль*', widget=forms.PasswordInput,
                                help_text=help_text())
    password2 = forms.CharField(label='Пароль (повторно)**', widget=forms.PasswordInput,
                                help_text='Повторите пароль')


    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        list_email = AdvUser.objects.filter(email=email)
        if list_email.count():
            raise ValidationError('Такой email уже зарегистрирован')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = AdvUser.objects.filter(username=username)
        if r.count():
            raise ValidationError("Такой никнейм уже существует")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data and \
                self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError("Введенные пароли не совпадают")
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'last_name', 'first_name', 'group')


class ChangeTeacherInfoForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput)
    middle_name = forms.CharField(required=True, label='Отчество', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты', widget=forms.EmailInput)
    position = forms.CharField(required=True, label='Должность', widget=forms.TextInput)
    degree = forms.CharField(required=False, label='Степень', widget=forms.TextInput)
    rank = forms.CharField(required=False, label='Звание', widget=forms.TextInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = AdvUser.objects.filter(username=username)
        if r.count():
            raise ValidationError("Этот логин занят")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        list_email = AdvUser.objects.filter(email=email)
        if list_email.count():
            raise ValidationError('Такой email уже занят')
        return email

    class Meta:
        model = Teacher
        fields = ('username', 'email', 'first_name', 'last_name', 'middle_name',
                  'position', 'degree', 'rank', 'send_messages')


class ChangeUserInfoForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты', widget=forms.EmailInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        list_email = AdvUser.objects.filter(email=email)
        if list_email.count():
            raise ValidationError('Такой email уже занят')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = AdvUser.objects.filter(username=username)
        if r.count():
            raise ValidationError("Этот логин занят")
        return username

    # def __init__(self, *args, **kwargs):
    #     super(ChangeUserInfoForm, self).__init__(*args, **kwargs)
    #     instance = getattr(self, 'instance', None)
    #     if instance and instance.id:
    #         self.fields['group'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = AdvUser
        fields = ('username', 'first_name', 'last_name', 'email')



class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _('Два поля пароля не совпадают.'),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=help_text(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = {
        **SetPasswordForm.error_messages,
        'password_incorrect': _("Ваш старый пароль был введен неправильно. Пожалуйста, введите его снова."),
    }
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class LoginForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = AdvUser
        fields = ('username', 'password')
