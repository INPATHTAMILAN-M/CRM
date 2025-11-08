# authapp/serializers/group.py
from rest_framework import serializers
from django.contrib.auth.models import Group, Permission


# 1️⃣ List Serializer (basic fields)
class GroupListSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']

    def get_user_count(self, obj):
        return obj.user_set.count()


# 2️⃣ Detail Serializer (includes permissions)
class GroupDetailSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    permissions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'users']

    def get_users(self, obj):
        return [
            {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name() or user.email
            }
            for user in obj.user_set.all()
        ]


# 3️⃣ Create Serializer
class GroupCreateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permission_ids']

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        group = Group.objects.create(**validated_data)
        if permission_ids:
            group.permissions.set(permission_ids)
        return group


# 4️⃣ Update Serializer
class GroupUpdateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permission_ids']

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        return instance


# 5️⃣ Add Users to Group
class AddUsersToGroupSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )


# 6️⃣ Remove Users from Group
class RemoveUsersFromGroupSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
