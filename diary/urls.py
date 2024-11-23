from django.urls import path

from . import views


app_name = 'diary'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('top_page/', views.TopPageView.as_view(),name="top_page"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('diary-list/', views.DiaryListView.as_view(), name="diary_list"),
    path('diary-detail/<int:pk>/', views.DiaryDetailView.as_view(), name="diary_detail"),
    path('diary-create/', views.DiaryCreateView.as_view(), name="diary_create"),
    path('diary-update/<int:pk>/', views.DiaryUpdateView.as_view(), name="diary_update"),
    path('diary-delete/<int:pk>/', views.DiaryDeleteView.as_view(), name="diary_delete"),
    path('diary-buy/<int:pk>/', views.DiaryBuyView.as_view(), name="diary_buy"),
    path('diary-credit/<int:pk>/', views.DiaryCreditView.as_view(), name="diary_credit"),
    path('upload/', views.upload_file.as_view(), name='upload_file'),
    path('upload-video/', views.upload_video, name='upload_video'),
    path('videos/', views.video_list, name='video_list'),
]
