from rest_framework import serializers
from .models import User, Post, Like

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'bio', 'is_active']

class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'content', 'total_likes']

    def get_total_likes(self, obj):
        return Like.objects.filter(post=obj, like=True).count()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'like']
