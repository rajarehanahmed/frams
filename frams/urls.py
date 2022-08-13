from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('progoffice/', include('progoffice.urls')),
    path('teacher/', include('teacher.urls')),
    path('activate/<uidb64>/<token>/', views.activate, name="active"),

    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), 
     name="reset_password"),
    path('reset_password_sent/',
     auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_sent.html'),
     name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html' ),
     name="password_reset_confirm"),
    path('reset_password_complete/',
     auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_done.html' ),
     name="password_reset_complete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
