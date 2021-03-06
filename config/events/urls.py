from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new-event/', views.NewEventView.as_view(), name='new-event'),
    path('create/', views.create_event, name='create'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('create-user/', views.create_user, name='create-user'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('authenticate/', views.authenticate_user, name='authenticate'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('upload-face-data-photo/<int:pk>', views.upload_face_data_photo, name='upload-face-data-photo'),
    path('delete-biometrics/<int:pk>', views.delete_biometrics, name='delete-biometrics'),
    path('event/<int:pk>', views.EventView.as_view(), name='event'),
    path('event/<int:pk>/json', views.provide_json, name='json'),
    path('event/<int:pk>/detail', views.EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/attend', views.AttendView.as_view(), name='attend'),
    path('<slug:slug>/upload-attendance-photo', views.upload_attendance_photo, name='upload-attendance-photo'),
    path('<slug:slug>/attendees', views.attendees_list, name='attendees'),
    path('<slug:slug>/qrcode', views.qrcode, name='qrcode')
]
