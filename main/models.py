import os

from django.core.signing import Signer
from learnDjango.settings import ALLOWED_HOSTS
from django.db.models import signals
from django.core.mail import send_mail, EmailMultiAlternatives
from django.dispatch import Signal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.contrib import messages
import datetime
from django.core.exceptions import ValidationError

from .utilities import (send_activation_notification, get_timestamp_path, get_namestamp_path,
                        send_new_comment_notification)

DAYS_OF_WEEK = (
    ("0", 'Понедельник'),
    ("1", 'Вторник'),
    ("2", 'Среда'),
    ("3", 'Четверг'),
    ("4", 'Пятница'),
    ("5", 'Суббота'),
)

TIME_CHOICES = (
    ("08:30:00", '08:30:00'),
    ("10:25:00", '10:25:00'),
    ("12:35:00", '12:35:00'),
    ("14:30:00", '14:30:00'),
    ("16:25:00", '16:25:00'),
    ("18:10:00", '18:10:00'),
)


class Structure(models.Model):
    structure_name = models.CharField(max_length=15, verbose_name='Учебный корпус')

    def __str__(self):
        return self.structure_name

    class Meta:
        verbose_name_plural = 'Учебные корпуса'
        verbose_name = 'Учебный корпус'
        ordering = ['structure_name']


class Auditory(models.Model):
    auditory_number = models.CharField(max_length=5, verbose_name='Аудитория')

    def __str__(self):
        return self.auditory_number

    class Meta:
        verbose_name_plural = 'Аудитории'
        verbose_name = 'Аудитория'
        ordering = ['auditory_number']


class Schedule(models.Model):
    group = models.ForeignKey('SubGroup', on_delete=models.CASCADE, verbose_name='Группа')

    def __str__(self):
        return 'Расписание для группы --- ' + str(self.group)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'


class AdditionalSchedule(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, verbose_name='Расписание')
    subject = models.ForeignKey('Subject', on_delete=models.PROTECT, null=True, verbose_name='Дисциплина')
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, null=True, verbose_name='Преподаватель')
    structure = models.ForeignKey('Structure', on_delete=models.PROTECT, null=True, verbose_name='Учебный корпус')
    auditory = models.ForeignKey('Auditory', on_delete=models.PROTECT, null=True, verbose_name='Аудитория')
    start_time = models.CharField(max_length=10, choices=TIME_CHOICES, null=True, verbose_name='Начало занятия')
    day = models.CharField(max_length=1, choices=DAYS_OF_WEEK, null=True, verbose_name='День недели')

    # def clean(self):
    #     try:
    #         AdditionalSchedule.objects.get(start_time=self.cleaned_data['start_time'],
    #                                        day=self.cleaned_data['day'])
    #         # if we get this far, we have an exact match for this form's data
    #         raise self.ValidationError("Exists already!")
    #     except AdditionalSchedule.DoesNotExist:
    #         # because we didn't get a match
    #         pass
    #
    #     return self.cleaned_data

    # def clean(self, *args, **kwargs):
    #
    #     sh = AdditionalSchedule.objects.filter(schedule=self.schedule, start_time=self.start_time,
    #                                            day=self.day)
    #     if (AdditionalSchedule.objects.filter(schedule=self.schedule, start_time=self.start_time,
    #                                            day=self.day).exists()):
    #         raise ValidationError('Нельзя назначить пару в одно и тоже время!')
    #     else:
    #         super(AdditionalSchedule, self).clean(*args, **kwargs)

    def __str__(self):
        return 'Добавление занятий'

    class Meta:
        verbose_name_plural = 'Продолжение расписания'
        verbose_name = 'Продолжение расписания'


class Subject(models.Model):
    name_of_subject = models.CharField(max_length=220, verbose_name='Название предмета')

    def __str__(self):
        return self.name_of_subject

    class Meta:
        verbose_name_plural = 'Предметы'
        verbose_name = 'Предмет'
        ordering = ['name_of_subject']


class AdditionalFile(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    file = models.FileField(upload_to=get_namestamp_path, verbose_name='Материал')

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name_plural = 'Дополнительные материалы'
        verbose_name = 'Дополнительный материал'


class Comment(models.Model):
    bb = models.ForeignKey('Bb', on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-created_at']


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)


class AdditionalImage(models.Model):
    bb = models.ForeignKey('Bb', on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'


class Bb(models.Model):
    group = models.ForeignKey('SubGroup', on_delete=models.CASCADE, verbose_name='Группа')
    title = models.CharField(max_length=40, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Информация')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    author = models.ForeignKey('Teacher', on_delete=models.CASCADE,
                               verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    def full_name(obj):
        return "%s %s %s" % (obj.author.last_name, obj.author.first_name, obj.author.middle_name)

    full_name.short_description = 'Преподаватель'

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class Group(models.Model):
    name = models.CharField(max_length=50, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    super_group = models.ForeignKey('SuperGroup', on_delete=models.PROTECT, null=True, blank=True,
                                    verbose_name='Форма обучения')


class SuperGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_group__isnull=True)


class SuperGroup(Group):
    objects = SuperGroupManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ["order", "name"]
        verbose_name = 'Форма обучения'
        verbose_name_plural = 'Формы обучения'


class SubGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_group__isnull=False)


class SubGroup(Group):
    objects = SubGroupManager()

    def __str__(self):
        return '%s - %s' % (self.super_group.name, self.name)

    class Meta:
        proxy = True
        ordering = ['super_group__order', 'super_group__name', 'order', 'name']
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)


class AdvUser(AbstractUser):
    group = models.ForeignKey('SubGroup', on_delete=models.PROTECT, null=True, verbose_name='Группа')
    is_teacher = models.BooleanField(default=False, verbose_name='Преподаватель')
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещания о новых комментариях?')

    def delete(self, *args, **kwargs):
        Comment.objects.filter(author=self.username).delete()
        super().delete(*args, **kwargs)

    def full_name(obj):
        return "%s %s" % (obj.last_name, obj.first_name)

    full_name.short_description = 'Студент'

    class Meta(AbstractUser.Meta):
        verbose_name_plural = 'Студенты'
        verbose_name = 'Студент'
        ordering = ['last_name']


class Teacher(AdvUser):
    middle_name = models.CharField(max_length=50, db_index=True, verbose_name='Отчество')
    position = models.CharField(max_length=50, db_index=True, verbose_name='Должность')
    degree = models.CharField(max_length=100, blank=True, verbose_name='Степень')
    rank = models.CharField(max_length=40, blank=True, verbose_name='Звание')

    def delete(self, *args, **kwargs):
        Comment.objects.filter(author=self.username).delete()
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, **kwargs)

    def full_name(obj):
        return "%s %s %s" % (obj.last_name, obj.first_name, obj.middle_name)

    full_name.short_description = 'Преподаватель'

    class Meta(AbstractUser.Meta):
        verbose_name_plural = 'Преподаватели'
        verbose_name = 'Преподаватель'
        ordering = ['username']


def notify_admin(sender, instance, created, **kwargs):
    '''Оповещает администратора о добавлении нового пользователя.'''
    if created:
        signer = Signer()
        if ALLOWED_HOSTS:
            host = 'http://' + ALLOWED_HOSTS[0] + '/admin/main/teacher'
        else:
            host = 'http://localhost:8000/admin/main/teacher/?q=' + instance.last_name + "+" + instance.first_name
            subject = 'Создан новый преподаватель'
            html_message = '<p>Был зарегистрирован преподаватель <strong>%s</strong> <strong>%s</strong> ' \
                           '<strong>%s</strong>.' \
                           '<p>Активируйте пользователя в <a href="%s">админ-панели</a>, ' \
                           'если это действительно преподаватель, либо удалите, если это не так.</p> ' \
                           % (instance.last_name, instance.first_name, instance.middle_name, host)
            from_addr = instance.email
            admin = AdvUser.objects.filter(username='admin')
            email = ''
            for a in admin:
                email = a.email
            recipient_list = (email,)
            msg = EmailMultiAlternatives(subject, html_message, from_addr, recipient_list)
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()


signals.post_save.connect(notify_admin, sender=Teacher)
