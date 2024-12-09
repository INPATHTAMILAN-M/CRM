from rest_framework import serializers
from lead.models import Opportunity, User, Lead, Opportunity_Stage, Note
from accounts.models import Stage ,Country

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name']  

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','currency_short']  

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Stage
        fields = ['id', 'stage']

class OppSerializer(serializers.ModelSerializer):
    class Meta:
        model= Opportunity
        fields = ['id', 'name']

class OpportunitySerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
    currency_type= CurrencySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    created_by=OwnerSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = "__all__"

    def get_file_url(self, obj):
        if obj.file:
            file_url = obj.file.url
            domain = "http://121.200.52.133:8000/"
            return f"{domain}{file_url}"
        return None

class PostOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ['lead','name','owner','stage','opportunity_value','currency_type','closing_date','probability_in_percentage',
                  "note","recurring_value_per_year","file"]
        read_only_fields=['created_by']

class LeadNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name'] 

class StageNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage']

class StageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Stage
        fields='__all__'


class PostNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields='__all__'

class StageGetSerializer(serializers.ModelSerializer):
    opportunity = OppSerializer(read_only=True)
    stage = StageNameSerializer(read_only=True)
    moved_by=OwnerSerializer(read_only=True)
    class Meta:
        model = Opportunity_Stage
        fields='__all__'
