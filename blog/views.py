from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Post, Like
from .serializers import UserSerializer,PostSerializer
from .models import User, CustomToken
from django.utils import timezone
from django.db.models import Q,Count

#add user 
class UserAPIView(APIView):
    def post(self, request):
        required_fields = ['username', 'email', 'password', 'age']
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response({
                "status": 400,
                "message": f"{', '.join(missing_fields)} {'is' if len(missing_fields) == 1 else 'are'} required field{'s' if len(missing_fields) > 1 else ''}"
            }, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        age = request.data.get('age')
        bio = request.data.get('bio')

        # Check if email already exists
        if User.objects.filter(email=email,is_active=True).exists():
            return Response({
                "status": 400,
                "message": "Email is already exists, please use another email"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
                age=age,
                bio=bio,
                is_active=True
            )

            # Generate and save custom token
            custom_token = CustomToken.generate_token(user)

            return Response({
                "status": 200,
                "message": "User added successfully",
                "token": custom_token.token
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#add post
class PostAPIView(APIView):
    def post(self, request):
        # Check if token is present in the request header
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid and fetch the associated user
        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if required fields are present
        required_fields = ['title', 'description', 'content']
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response({
                "status": 400,
                "message": f"{', '.join(missing_fields)} {'is' if len(missing_fields) == 1 else 'are'} required fields"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the post title already exists
        title = request.data.get('title')
        if Post.objects.filter(title=title).exists():
            return Response({
                "status": 400,
                "message": "A post with this title already exists, please use different title"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the post
        try:
            post = Post.objects.create(
                user=user,
                title=request.data.get('title'),
                description=request.data.get('description'),
                content=request.data.get('content'),
                is_active = True,
                private = request.data.get('private',False),
                created_at=timezone.now(),
                updated_at=timezone.now()  # Assuming initial creation and update times are the same
            )
            return Response({
                "status": 200,
                "message": "Post added successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#add like
class LikeAPIView(APIView):
    def post(self, request):
        # Check if token is present in the request header
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid and fetch the associated user
        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if required fields are present
        required_fields = ['like', 'post_id']
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response({
                "status": 400,
                "message": f"{', '.join(missing_fields)} {'is' if len(missing_fields) == 1 else 'are'} required fields"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract required data from request
        like = request.data.get('like')
        post_id = request.data.get('post_id')

        # Check if the post exists
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({
                "status": 400,
                "message": "Post does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the like value is valid
        if not isinstance(like, bool):
            return Response({
                "status": 400,
                "message": "Invalid value for 'like'. It should be a boolean (True/False)"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the like
        try:
            like_instance, created = Like.objects.get_or_create(
                post=post,
                user=user,
                defaults={'like': like, 'created_at': timezone.now()}
            )
            if not created:
                like_instance.like = like
                like_instance.save()
            return Response({
                "status": 200,
                "message": "Like updated successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#############################################
        
# show a specific user data
class UserDataAPIView(APIView):
    def get(self, request):
        # Check if token is present in the request header
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the current user using the token
        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                "status": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Fetch user data
        user_serializer = UserSerializer(user)

        # Fetch all posts created by the current user
        user_posts = Post.objects.filter(user=user)

        # Serialize posts along with total number of likes for each active post
        posts_data = []
        for post in user_posts:
            if post.is_active:
                post_data = PostSerializer(post).data
                total_likes = Like.objects.filter(post=post, like=True).count()
                post_data['total_likes'] = total_likes
                posts_data.append(post_data)

        data = {
            "status": status.HTTP_200_OK,
            "message": "User data fetched successfully",
            "user": user_serializer.data,
            "posts": posts_data
        }
        return Response(data)
    
#############################################
    
#update user
class UserUpdateAPIView(APIView):
    def put(self, request):
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        allowed_fields = ['username', 'email', 'age', 'bio']

        update_data = {key: request.data.get(key) for key in allowed_fields}

        extra_fields = set(request.data.keys()) - set(allowed_fields)
        if extra_fields:
            return Response({
                "status": 400,
                "message": f"Unexpected fields: {', '.join(extra_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = timezone.now()

        user.save()

        serializer = UserSerializer(user)
        data = {
            "status": status.HTTP_200_OK,
            "message": "User updated successfully",
            "data": serializer.data
        }
        return Response(data)
    
#update post
class PostUpdateAPIView(APIView):
    def put(self, request):
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        post_id = request.data.get('post_id')
        if not post_id:
            return Response({
                "status": 400,
                "message": "Post ID is required in the request data"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id, user=user)
        except Post.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Post not found or does not belong to the current user"
            }, status=status.HTTP_404_NOT_FOUND)

        update_data = {
            key: request.data.get(key) for key in ['title', 'description', 'content','private']
        }

        allowed_fields = ['post_id','title', 'description', 'content']
        unexpected_fields = set(request.data.keys()) - set(allowed_fields)
        if unexpected_fields:
            return Response({
                "status": 400,
                "message": f"Unexpected fields: {', '.join(unexpected_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        new_title = update_data.get('title')
        if new_title and Post.objects.exclude(id=post_id).filter(title=new_title).exists():
            return Response({
                "status": 400,
                "message": "A post with this title already exists, please use a different title"
            }, status=status.HTTP_400_BAD_REQUEST)

        for key, value in update_data.items():
            if value is not None:
                setattr(post, key, value)

        post.updated_at = timezone.now()
        post.save()

        serializer = PostSerializer(post)

        data = serializer.data.copy()
        data.pop('total_likes', None)

        response_data = {
            "status": status.HTTP_200_OK,
            "message": "Post updated successfully",
            "data": data
        }
        return Response(response_data)

#############################################

# get all post
class PostListAPIView(APIView):
    def get(self, request):
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # posts = Post.objects.filter(Q(is_active=True) & Q(Q(user_id=user) | Q(private=False))).order_by('-id')

        # posts_data = []
        # for post in posts:
        #     likes_count = Like.objects.filter(post=post, like=True).count()

        #     post_data = {
        #         "id": post.id,
        #         "title": post.title,
        #         "description": post.description,
        #         "content": post.content,
        #         "likes_count": likes_count
        #     }

        #     posts_data.append(post_data)
        posts = Post.objects.filter(
            Q(is_active=True) &
            (Q(user_id=user) | Q(private=False))
        ).annotate(likes_count=Count('like__id', filter=Q(like__like=True))).order_by('-id')

        posts_data = list(posts.values('id', 'title', 'description', 'content', 'likes_count'))

        response_data = {
            "status": status.HTTP_200_OK,
            "message": "Posts fetched successfully",
            "total_post": posts.count(),
            "data": posts_data
        }

        response_data = {
            "status": status.HTTP_200_OK,
            "message": "Posts fetched successfully",
            "total_post":posts.count(),
            "data": posts_data
        }
        return Response(response_data)
    

#############################################
#delete user
class UserDeleteAPIView(APIView):
    def delete(self, request):
        # Check if token is present in the request header
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the current user using the token
        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the user is active
        if not user.is_active:
            return Response({
                "status": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Deactivate the user
        user.is_active = False
        user.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "User deleted successfully"
        })

#delete post
class PostDeleteAPIView(APIView):
    def delete(self, request):
        # Check if token is present in the request header
        token = request.headers.get('Token')
        if not token:
            return Response({
                "status": 400,
                "message": "Token is required in the request header"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the current user using the token
        try:
            custom_token = CustomToken.objects.get(token=token)
            user = custom_token.user
        except CustomToken.DoesNotExist:
            return Response({
                "status": 401,
                "message": "Invalid token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                "status": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Get post_id from request data
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({
                "status": 400,
                "message": "Post ID is required in the request data"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the post associated with the current user
        try:
            post = Post.objects.get(id=post_id, user=user)
        except Post.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Post not found or does not belong to the current user"
            }, status=status.HTTP_404_NOT_FOUND)

        # Deactivate the post
        post.is_active = False
        post.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Post deleted successfully"
        })