from django.urls import path, re_path
from . import views

urlpatterns = [
    path('page/', views.Page_data.as_view()),
    path('page_detail/', views.Page_detail.as_view()),
    path('page_update/', views.Page_update.as_view()),

    path('index/', views.List.as_view()),
    path('index_detail/', views.Info.as_view()),
]


handler404 = "api.live.views.page_not_found"

handler500 = "api.live.views.page_error"