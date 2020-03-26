from django.core.paginator import Paginator
from django.db.models import Q
from django.core.signing import BadSignature
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Count

from .utilities import signer
from .models import AdvUser, SubGroup, Bb, Comment, Subject, AdditionalFile
from .forms import *
from .decorators import user_required, teacher_required, user_is_entry_author, student_required

'''
Details about the selected bb
'''


@user_required
def detail(request, group_pk, pk):
    bb = Bb.objects.get(pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = UserCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')

    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)


'''
Search bbs 
'''


@user_required
@teacher_required
def by_group(request, pk):
    group = get_object_or_404(SubGroup, pk=pk)
    bbs = Bb.objects.filter(is_active=True, group=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(author__middle_name__icontains=keyword) | \
            Q(author__first_name__icontains=keyword) | \
            Q(author__last_name__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'group': group, 'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/by_group.html', context)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        comments = Comment.objects.filter(author=request.user.username)
        comments.delete()
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class DeleteTeacherView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'main/delete_teacher.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        comments = Comment.objects.filter(author=request.user.username)
        comments.delete()
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterTeacherView(CreateView):
    model = AdvUser
    template_name = 'main/teacher_register.html'
    form_class = RegisterTeacherForm
    success_url = reverse_lazy('main:register_done')


class BBPasswordResetView(PasswordResetView):
    template_name = 'main/password_reset.html'
    success_url = reverse_lazy('main:reset_password_done')
    success_message = 'Письмо выслано на почту'


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменён'


class ChangeTeacherInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Teacher
    template_name = 'main/change_user_info.html'
    form_class = ChangeTeacherInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:student_profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


@user_required
@user_is_entry_author
def comment_delete(request, group_pk, bb_pk, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        comment.delete()
        messages.add_message(request, messages.SUCCESS, 'Комментарий удален')
        return redirect('main:detail', group_pk, bb_pk)
    else:
        context = {'comment': comment}
        return render(request, 'main/comment_delete.html', context)


@user_required
@user_is_entry_author
def comment_change(request, group_pk, bb_pk, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        form = UserCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий исправлен')
            return redirect('main:detail', group_pk, bb_pk)
    else:
        form = UserCommentForm(instance=comment)
    context = {'comment': comment, 'form': form}
    return render(request, 'main/comment_change.html', context)


@user_required
@teacher_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'bb': bb}
        return render(request, 'main/profile_bb_delete.html', context)


@user_required
@teacher_required
def profile_bb_change(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'bb': bb, 'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_change.html', context)


@user_required
@teacher_required
def profile_bb_add(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_add.html', context)


@user_required
@teacher_required
def profile_file_add(request, pk):
    sub = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        formset = AIFormFileSet(request.POST, request.FILES, instance=sub)
        if formset.is_valid():
            formset.save()
            messages.add_message(request, messages.SUCCESS, 'Материал изменён')
            return redirect('main:profile_sub_detail', sub.pk)
    else:
        formset = AIFormFileSet(instance=sub)
    context = {'formset': formset, 'sub': sub}
    return render(request, 'main/profile_file_add.html', context)


@user_required
def profile_sub_detail(request, pk):
    sub = get_object_or_404(Subject, pk=pk)
    ais = sub.additionalfile_set.all()

    context = {'sub': sub, 'ais': ais}
    return render(request, 'main/profile_sub_detail.html', context)


@user_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = UserCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/profile_bb_detail.html', context)


@user_required
@student_required
def student_profile(request):
    bbs = Bb.objects.filter(group=request.user.group.pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(author__middle_name__icontains=keyword) | \
            Q(author__first_name__icontains=keyword) | \
            Q(author__last_name__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 8)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/profile.html', context)


@user_required
@teacher_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(author__middle_name__icontains=keyword) | \
            Q(author__first_name__icontains=keyword) | \
            Q(author__last_name__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/profile.html', context)


def list_schedule(request):
    shs = Schedule.objects.all()
    context = {'shs': shs, }
    return render(request, 'main/schedule.html', context)


def detail_schedule(request, pk):
    sh = get_object_or_404(Schedule, pk=pk)
    ais = sh.additionalschedule_set.all()
    sbs_monday = AdditionalSchedule.objects.filter(schedule=pk, day='0').order_by('day',
                                                                                         'start_time')
    sbs_tuesday = AdditionalSchedule.objects.filter(schedule=pk, day='1').order_by('day',
                                                                      'start_time')
    sbs_wednesday = AdditionalSchedule.objects.filter(schedule=pk, day='2').order_by('day',
                                                                        'start_time')
    sbs_thursday = AdditionalSchedule.objects.filter(schedule=pk, day='3').order_by('day',
                                                                       'start_time')

    sbs_friday = AdditionalSchedule.objects.filter(schedule=pk, day='4').order_by('day',
                                                                     'start_time')
    sbs_saturday = AdditionalSchedule.objects.filter(schedule=pk, day='5').order_by('day',
                                                                       'start_time')
    context = {'sh': sh, 'ais': ais, 'sbs_monday': sbs_monday, 'sbs_tuesday': sbs_tuesday,
               'sbs_wednesday': sbs_wednesday,
               'sbs_thursday': sbs_thursday, 'sbs_friday': sbs_friday, 'sbs_saturday': sbs_saturday, }
    return render(request, 'main/detail_schedule.html', context)



@user_required
@student_required
def student_schedule(request):
    sbs = AdditionalSchedule.objects.filter(schedule__group=request.user.group).order_by('day', 'start_time')

    sbs_monday = AdditionalSchedule.objects.filter(schedule__group=request.user.group, day='0').order_by('day',
                                                                                                         'start_time')
    sbs_tuesday = AdditionalSchedule.objects.filter(schedule__group=request.user.group, day='1').order_by('day',
                                                                                                          'start_time')
    sbs_wednesday = AdditionalSchedule.objects.filter(schedule__group=request.user.group, day='2').order_by('day',
                                                                                                            'start_time')
    sbs_thursday = AdditionalSchedule.objects.filter(schedule__group=request.user.group, day='3').order_by('day',
                                                                                                           'start_time')

    sbs_friday = AdditionalSchedule.objects.filter(schedule__group=request.user.group, day='4').order_by('day',
                                                                                                         'start_time')
    sbs_saturday = AdditionalSchedule.objects.filter(schedule__group=request.user.group, day='5').order_by('day',
                                                                                                           'start_time')

    scheduler = {}

    for items in sbs:
        if items.day not in scheduler:
            scheduler[items.day] = [{
                field: value for field, value in vars(items).items() if not field.startswith('day')
            }]
        else:
            scheduler[items.day] += [{
                field: value for field, value in vars(items).items() if not field.startswith('day')
            }]

    schedule = []
    for sb in sbs:
        if sb.day not in schedule:
            schedule.append(
                [sb.get_day_display, sb.start_time, sb.subject.name_of_subject, sb.teacher.last_name,
                 sb.teacher.first_name,
                 sb.teacher.middle_name, sb.structure.structure_name, sb.auditory.auditory_number])

    '''
    GET CERTAIN SUBJECTS ON CERTAIN DAYS
    '''

    context = {'sbs': sbs, 'sbs_monday': sbs_monday, 'sbs_tuesday': sbs_tuesday, 'sbs_wednesday': sbs_wednesday,
               'sbs_thursday': sbs_thursday, 'sbs_friday': sbs_friday, 'sbs_saturday': sbs_saturday, }
    return render(request, 'main/schedule.html', context)


@user_required
@student_required
def student_subjects(request):
    sbs = AdditionalSchedule.objects.filter(schedule__group=request.user.group)
    paginator = Paginator(sbs, 8)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'sbs': page.object_list}
    return render(request, 'main/subjects.html', context)


@user_required
@teacher_required
def teacher_subjects(request):
    sbs = AdditionalSchedule.objects.filter(teacher=request.user.pk)
    paginator = Paginator(sbs, 8)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'sbs': page.object_list}
    return render(request, 'main/subjects.html', context)


def login_page(request):
    form = LoginForm
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_teacher:
            login(request, user)
            return redirect('main:teacher_subjects')
        elif user is not None and user.is_superuser:
            login(request, user)
            return HttpResponseRedirect('../admin/')
        elif user is not None:
            login(request, user)
            return redirect('main:student_profile')
        else:
            messages.info(request, 'Вы ввели неверный логин либо пароль')

    context = {'form': form}
    return render(request, 'main/login.html', context)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


def index(request):
    bbs = Bb.objects.filter(is_active=True, group__name__icontains='Общие')
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword) | \
            Q(author__middle_name__icontains=keyword) | Q(author__first_name__icontains=keyword) | \
            Q(author__last_name__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 5)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/index.html', context)


def error_perm_teach(request):
    return render(request, 'main/teacher_error.html')


def reset_password_confirm(request):
    return render(request, 'registration/password_reset_confirm.html')


def reset_password_done(request):
    return render(request, 'registration/password_reset_done.html')
