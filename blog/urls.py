from django.urls import path
from .views import UserAPIView,PostAPIView,LikeAPIView,UserDataAPIView,UserUpdateAPIView,PostUpdateAPIView,PostListAPIView,UserDeleteAPIView,PostDeleteAPIView

urlpatterns = [
    path('add_user/', UserAPIView.as_view(), name='add_user'),
    path('add_post/', PostAPIView.as_view(), name='add_post'),
    path('add_like/', LikeAPIView.as_view(), name='add_like'),
    path('user_data/', UserDataAPIView.as_view(), name='user_data'),
    path('user_update/', UserUpdateAPIView.as_view(), name='user_update'),
    path('post_update/', PostUpdateAPIView.as_view(), name='post_update'),
    path('all_post/', PostListAPIView.as_view(), name='all_post'),
    path('delete_user/', UserDeleteAPIView.as_view(), name='delete_user'),
    path('delete_post/', PostDeleteAPIView.as_view(), name='delete_post'),
]
