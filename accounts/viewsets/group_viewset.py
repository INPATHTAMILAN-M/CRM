from rest_framework import viewsets, status
from rest_framework.decorators import action
# from common.viewset import BaseViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import Group
from accounts.serializers.group import (
    GroupListSerializer,GroupCreateSerializer,GroupUpdateSerializer,
    GroupDetailSerializer, AddUsersToGroupSerializer,RemoveUsersFromGroupSerializer)

from lead.custom_pagination import Paginator
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Django Groups (User Roles)
    
    Provides CRUD operations and additional actions for:
    - Adding users to groups
    - Removing users from groups
    - Viewing group members
    """
    queryset = Group.objects.all().order_by('name')
    permission_classes = [IsAuthenticated]  # Only admins can manage groups
    pagination_class = Paginator
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GroupListSerializer
        elif self.action == 'create':
            return GroupCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GroupUpdateSerializer
        elif self.action == 'add_users':
            return AddUsersToGroupSerializer
        elif self.action == 'remove_users':
            return RemoveUsersFromGroupSerializer
        return GroupDetailSerializer
    
    @action(detail=True, methods=['post'], url_path='add-users')
    def add_users(self, request, pk=None):
        """Add users to this group"""
        group = self.get_object()
        serializer = AddUsersToGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data['user_ids']
        users = CustomUser.objects.filter(id__in=user_ids)
        
        # Add users to the group
        added_count = 0
        already_in_group = []
        
        for user in users:
            if not group.user_set.filter(id=user.id).exists():
                group.user_set.add(user)
                added_count += 1
            else:
                already_in_group.append(user.email)
        
        response_data = {
            'message': f'Successfully added {added_count} user(s) to group "{group.name}"',
            'added_count': added_count,
            'group_id': group.id,
            'group_name': group.name,
            'total_users_in_group': group.user_set.count()
        }
        
        if already_in_group:
            response_data['already_in_group'] = already_in_group
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='remove-users')
    def remove_users(self, request, pk=None):
        """Remove users from this group"""
        group = self.get_object()
        serializer = RemoveUsersFromGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = serializer.validated_data['user_ids']
        users = CustomUser.objects.filter(id__in=user_ids)
        
        # Remove users from the group
        removed_count = 0
        not_in_group = []
        
        for user in users:
            if group.user_set.filter(id=user.id).exists():
                group.user_set.remove(user)
                removed_count += 1
            else:
                not_in_group.append(user.email)
        
        response_data = {
            'message': f'Successfully removed {removed_count} user(s) from group "{group.name}"',
            'removed_count': removed_count,
            'group_id': group.id,
            'group_name': group.name,
            'total_users_in_group': group.user_set.count()
        }
        
        if not_in_group:
            response_data['not_in_group'] = not_in_group
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        """Get all members (users) in this group"""
        group = self.get_object()
        users = group.user_set.all()
        
        # Paginate the results
        page = self.paginate_queryset(users)
        if page is not None:
            user_data = [
                {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.get_full_name() or user.email,
                    'phone': user.phone,
                    'is_active': user.is_active,
                    'account_status': user.account_status,
                    'user_type': user.user_type,
                    'created_at': user.created_at
                }
                for user in page
            ]
            return self.get_paginated_response(user_data)
        
        user_data = [
            {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name() or user.email,
                'phone': user.phone,
                'is_active': user.is_active,
                'account_status': user.account_status,
                'user_type': user.user_type,
                'created_at': user.created_at
            }
            for user in users
        ]
        
        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'total_members': users.count(),
            'members': user_data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Get statistics about groups"""
        groups = self.get_queryset()
        
        stats_data = {
            'total_groups': groups.count(),
            'groups': [
                {
                    'id': group.id,
                    'name': group.name,
                    'user_count': group.user_set.count(),
                    'permission_count': group.permissions.count()
                }
                for group in groups
            ]
        }
        
        return Response(stats_data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a group with confirmation"""
        group = self.get_object()
        user_count = group.user_set.count()
        
        if user_count > 0:
            return Response({
                'error': f'Cannot delete group "{group.name}" because it has {user_count} user(s). Remove all users first.',
                'user_count': user_count
            }, status=status.HTTP_400_BAD_REQUEST)
        
        group_name = group.name
        self.perform_destroy(group)
        
        return Response({
            'message': f'Group "{group_name}" deleted successfully'
        }, status=status.HTTP_200_OK)