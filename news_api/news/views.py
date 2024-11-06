from django.contrib.auth import authenticate, logout
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Story
from .serializers import StoryWriteSerializer, StoryReadSerializer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.db.models import Q
from datetime import datetime


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        # Login successful
        token, created = Token.objects.get_or_create(user=user)
        # Prepare the welcome message including the token
        welcome_message = f"Welcome! Your token is {token.key}"
        # Return the welcome message with the token as a plain text response
        return HttpResponse(welcome_message, status=status.HTTP_200_OK, content_type='text/plain')
        # return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        # Login failed
        return HttpResponse("Invalid username or password.", status=status.HTTP_401_UNAUTHORIZED,
                            content_type='text/plain')


@api_view(['POST'])
def logout_view(request):
    # Django's logout function doesn't require the user to be specified as it uses the user from request
    logout(request)
    # You could also perform additional cleanup here if needed
    return HttpResponse("Goodbye!", status=status.HTTP_200_OK, content_type='text/plain')


class StoriesView(APIView):
    permission_classes = [
        IsAuthenticatedOrReadOnly]  # Allow anyone to read stories, but posting requires authentication

    def get(self, request):

        story_cat = request.query_params.get('story_cat')
        story_region = request.query_params.get('story_region')
        story_date = request.query_params.get('story_date')

        # Build the filter criteria
        filters = Q()
        if story_cat != "*":
            filters &= Q(category=story_cat)
        if story_region != "*":
            filters &= Q(region=story_region)
        if story_date != "*":
            try:
                date_obj = datetime.strptime(story_date, '%Y-%m-%d').date()
                filters &= Q(date__gte=date_obj)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Query the database
        stories = Story.objects.filter(filters)

        if stories:
            serializer = StoryReadSerializer(stories, many=True)
            return Response({'stories': serializer.data}, status=status.HTTP_200_OK)
        else:
            return HttpResponse("No stories found matching the criteria.", status=status.HTTP_404_NOT_FOUND,
                                content_type='text/plain')

    def post(self, request):
        serializer = StoryWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Automatically set the author to the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class DeleteStoryView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, key, format=None):
        try:
            story = Story.objects.get(pk=key)
            if story.author != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN, data="You do not have permission to delete this story.")
            story.delete()
            return Response(status=status.HTTP_200_OK)
        except Story.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data="Story not found.")
        except Exception as e:
            # Log the error for server-side debugging
            print(e)
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE, data="Unable to process the request.")


