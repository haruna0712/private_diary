from django.urls import path

from . import views


app_name = 'diary'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('top_page/', views.TopPageView.as_view(),name="top_page"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('share-list/', views.DiaryListView.as_view(), name="diary_list"),
    path('share-detail/<int:pk>/', views.DiaryDetailView.as_view(), name="diary_detail"),
    path('share-create/', views.DiaryCreateView.as_view(), name="diary_create"),
    path('share-update/<int:pk>/', views.DiaryUpdateView.as_view(), name="diary_update"),
    path('share-delete/<int:pk>/', views.DiaryDeleteView.as_view(), name="diary_delete"),
    path('share-buy/<int:pk>/', views.DiaryBuyView.as_view(), name="diary_buy"),
    path('share-credit/<int:pk>/', views.DiaryCreditView.as_view(), name="diary_credit"),
    path('upload/', views.upload_file.as_view(), name='upload_file'),
    path('upload-video/', views.upload_video, name='upload_video'),
    path('videos/', views.video_list, name='video_list'),
    path('diary/<int:pk>/docker_calculate/', views.docker_calculate, name='docker_calculate'),
]
