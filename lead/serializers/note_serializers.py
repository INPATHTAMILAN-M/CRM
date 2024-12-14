from rest_framework import serializers
from lead.models import Note, Opportunity
from django.contrib.auth.models import User
# NoteRetrieveSerializer: For retrieving a single note with full details.
class NoteRetrieveSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    note_by_username = serializers.CharField(source='note_by.username', read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'opportunity_name', 'note', 'note_by_username', 'note_on']
        read_only_fields = ['note_on']

# NoteCreateSerializer: For creating a new note related to an opportunity.
class NoteCreateSerializer(serializers.ModelSerializer):
    opportunity = serializers.PrimaryKeyRelatedField(queryset=Opportunity.objects.all())
    note_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    
    class Meta:
        model = Note
        fields = ['opportunity', 'note', 'note_by']

# NoteUpdateSerializer: For updating an existing note's content.
class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['note']

# NoteListSerializer: For listing all notes with basic information.
class NoteListSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    note_by_username = serializers.CharField(source='note_by.username', read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'opportunity_name', 'note', 'note_by_username', 'note_on']
        read_only_fields = ['note_on']