from rest_framework import serializers

from main.models import Bb, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('bb', 'author', 'content', 'created_at')


class BbDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'created_at', 'image')


class BbSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='group.name')
    form_of_teaching = serializers.CharField(source='group.super_group')
    author = serializers.CharField(source='author.username')

    class Meta:
        model = Bb
        fields = ('id', 'group', 'form_of_teaching', 'title', 'content', 'image', 'author', 'created_at')
