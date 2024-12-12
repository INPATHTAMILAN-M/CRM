
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..filters.notes_filter import NoteFilter
from lead.models import Note
from ..serializers.note_serializers import *
from django_filters.rest_framework import DjangoFilterBackend

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteCreateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = NoteFilter
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
