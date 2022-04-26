from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('new-event/', views.NewEventView.as_view(), name='new-event'),
    path('create/', views.create_event, name='create'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('create-user/', views.create_user, name='create-user'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('authenticate/', views.authenticate_user, name='authenticate'),
    path('<int:pk>/qrcode/', views.QRCodeView.as_view(), name='qrcode'),
    path('<slug:slug>/attend', views.AttendView.as_view(), name='attend'),
    path('<slug:slug>/upload-attendance-photo', views.upload_attendance_photo, name='upload-attendance-photo')
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
