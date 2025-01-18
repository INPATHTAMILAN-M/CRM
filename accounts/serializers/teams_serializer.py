from rest_framework import serializers
from accounts.models import Teams
from django.contrib.auth.models import User


class TeamsCreateSerializer(serializers.ModelSerializer):
    bde_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Teams
        fields = ['id', 'bdm_user', 'bde_user']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id','username', 'full_name','email' ]

class TeamsListSerializer(serializers.ModelSerializer):
    bdm_user = UserSerializer()  # Nested serializer for BDM
    bde_user = UserSerializer(many=True)  # Nested serializer for multiple BDEs

    class Meta:
        model = Teams
        fields = ['id', 'bdm_user', 'bde_user']

class TeamsUpdateSerializer(serializers.ModelSerializer):
    bde_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Teams
        fields = ['id', 'bdm_user', 'bde_user']

    def update(self, instance, validated_data):
        instance.bdm_user = validated_data.get('bdm_user', instance.bdm_user)

        bde_users = validated_data.get('bde_user', None)
        if bde_users is not None:
            instance.bde_user.clear()
            instance.bde_user.add(*bde_users)

        instance.save()
        return instance