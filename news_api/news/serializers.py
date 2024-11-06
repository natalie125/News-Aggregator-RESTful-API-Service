from rest_framework import serializers
from .models import Story
from django.utils.timezone import localtime


class StoryWriteSerializer(serializers.ModelSerializer):
    story_date = serializers.DateTimeField(source='date', format="%Y-%m-%d", required=False)

    class Meta:
        model = Story
        fields = ['id', 'headline', 'category', 'region', 'author', 'story_date', 'details']
        read_only_fields = ['id', 'author', 'date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.name if instance.author else None
        return representation


class StoryReadSerializer(serializers.ModelSerializer):
    key = serializers.CharField(source='id', read_only=True)
    story_cat = serializers.CharField(source='category')
    story_region = serializers.CharField(source='region')
    author = serializers.CharField(source='author.name')
    story_date = serializers.DateField(source='date', format="%Y-%m-%d")
    story_details = serializers.CharField(source='details')
    story_date = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['key', 'headline', 'story_cat', 'story_region', 'author', 'story_date', 'story_details']
        read_only_fields = ['key', 'author', 'story_date']

    def get_story_date(self, obj):
        return localtime(obj.date).strftime("%Y-%m-%d") if obj.date else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Customize the author representation
        representation['author'] = instance.author.name if instance.author else None
        return representation
