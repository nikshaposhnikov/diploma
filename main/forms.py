from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.forms.formsets import formset_factory

from .models import user_registrated
from .models import AdvUser, SuperGroup, SubGroup, Bb, AdditionalImage, Comment, Subject, AdditionalFile


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
                                         label='Надгруппа', required=True)

    class Meta:
        model = SubGroup
        fields = '__all__'


class RegisterTeacherForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput)
    middle_name = forms.CharField(required=True, label='Отчество', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Повторите пароль')
    position = forms.CharField(required=True, label='Должность', widget=forms.TextInput)
    degree = forms.CharField(required=True, label='Степень', widget=forms.TextInput)
    rank = forms.CharField(required=True, label='Звание', widget=forms.TextInput)

    # def clean_email(self):
    #     email = self.cleaned_data['email'].lower()
    #     list_email = AdvUser.objects.filter(email=email)
    #     if list_email.count():
    #         raise ValidationError('Такой email уже зарегистрирован')
    #     return email

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
        user_registrated.send(RegisterTeacherForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'middle_name',
                  'position', 'degree', 'rank', 'send_messages', 'is_teacher')


class RegisterUserForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput)
    middle_name = forms.CharField(required=True, label='Отчество', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Повторите пароль')

    # def clean_email(self):
    #     email = self.cleaned_data['email'].lower()
    #     list_email = AdvUser.objects.filter(email=email)
    #     if list_email.count():
    #         raise ValidationError('Такой email уже зарегистрирован')
    #     return email

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
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'middle_name',
                  'send_messages')


class ChangeTeacherInfoForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput)
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput)
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput)
    middle_name = forms.CharField(required=True, label='Отчество', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Повторите пароль')
    position = forms.CharField(required=True, label='Должность', widget=forms.TextInput)
    degree = forms.CharField(required=True, label='Степень', widget=forms.TextInput)
    rank = forms.CharField(required=True, label='Звание', widget=forms.TextInput)

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'middle_name',
                  'position', 'degree', 'rank', 'send_messages')


class ChangeUserInfoForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput)
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class LoginForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = AdvUser
        fields = ('username', 'password')
