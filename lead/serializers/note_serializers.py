from rest_framework import serializers
from lead.models import Note

class NoteRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'lead', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['lead', 'content']

class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['content']

class NoteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'lead', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']