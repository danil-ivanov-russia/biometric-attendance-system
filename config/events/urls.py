from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('event/create', views.create_event, name='create'),
    path('event/<int:pk>/qrcode', views.create_event, name='qrcode'),
    path('event/<str:uuid>/attend', views.create_event, name='attend')
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
