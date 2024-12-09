from rest_framework import serializers
from lead.models import Note,Opportunity



class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = 'User'
        fields = ['id', 'username']
    
class NoteSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only = True)
    note_by = serializers.SerializerMethodField() 
    class Meta:
        model = Note
        fields = '__all__'

    def get_note_by(self, obj):
        return {
            'id': obj.note_by.id,
            'username': obj.note_by.username  # Access username directly
        }

class PostNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'