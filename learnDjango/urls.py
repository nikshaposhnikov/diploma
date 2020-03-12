"""learnDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache
from .forms import EmailValidationOnForgotPassword
from main.views import BBPasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/password_reset/', BBPasswordResetView.as_view(form_class=EmailValidationOnForgotPassword),
         name='admin_password_reset', ),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done', ),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm', ),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete', ),
    path('api/', include('api.urls')),
    path('', include('main.urls', namespace='')),
]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
