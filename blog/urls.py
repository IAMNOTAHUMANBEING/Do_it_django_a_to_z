from django.urls import path, include
from . import views

urlpatterns = [
    path('<int:pk>/', views.PostDetail.as_view()),
    # FBV
    # path('<int:pk>/', views.single_post_page),
    path('', views.PostList.as_view()),
    # FBV
    # path('', views.index),
]
