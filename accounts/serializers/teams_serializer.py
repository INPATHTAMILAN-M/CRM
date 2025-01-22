from rest_framework import serializers
from accounts.models import Teams
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

class TeamsCreateSerializer(serializers.ModelSerializer):
    bde_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Teams
        fields = ['id', 'bdm_user', 'bde_user']

    def validate(self, data):
            # Ensure there's no duplicate bdm_user
            bdm_user = data.get('bdm_user')
            if Teams.objects.filter(bdm_user=bdm_user).exists():
                raise ValidationError({'error': 'This BDM user is already assigned to another team.'})

            return data
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id','username', 'full_name','email' ]

class TeamsListSerializer(serializers.ModelSerializer):
    bdm_user = UserSerializer()
    bde_user = UserSerializer(many=True)

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

class TeamsFilterSerializer(serializers.ModelSerializer):
    bde_user = UserSerializer(many=True)

    class Meta:
        model = Teams
        fields = ['bde_user']