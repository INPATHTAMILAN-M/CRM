
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from lead.models import Note
from ..serializers.note_serializers import *

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return NoteCreateSerializer
        if self.action == 'list':
            return NoteListSerializer
        if self.action in ['update', 'partial_update']:
            return NoteUpdateSerializer
        return NoteRetrieveSerializer  

    def perform_create(self, serializer):
        serializer.save(note_by=self.request.user)

    def get_queryset(self):
        return Note.objects.filter(opportunity__company__created_by=self.request.user)
