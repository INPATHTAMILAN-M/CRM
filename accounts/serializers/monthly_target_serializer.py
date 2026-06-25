from rest_framework import serializers
from accounts.models import MonthlyTarget
from accounts.models import User
from decimal import Decimal
from django.db.models import Sum, Q
from datetime import date
from dateutil.relativedelta import relativedelta

class UserSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'group']

    def get_group(self, obj):
        return {"id": obj.groups.first().id, "name": obj.groups.first().name} if obj.groups.exists() else None

class MonthlyTargetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'target_amount', 'created_at']
        read_only_fields = ['created_at']

class MonthlyTargetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    achieved_amount = serializers.SerializerMethodField()
    remaining_target = serializers.SerializerMethodField()
    original_target_amount = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'original_target_amount', 'target_amount', 'achieved_amount', 'remaining_target', 'created_at']

    def get_achieved_amount(self, obj):
        # Import here to avoid circular imports
        from lead.models import Opportunity

        # Use same logic as AnnualTargetAnalyticsViewSet._sum_achieved
        # Build month start/end range
        start = date(obj.year, obj.month, 1)
        end = (start + relativedelta(months=1)) - relativedelta(days=1)

        qs = Opportunity.objects.filter(
            opportunity_status=34,
            is_active=True,
            closing_date__range=(start, end),
        )

        total = Decimal('0.00')

        # u = obj.user
        # filters_with_weights = [
        #     (Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('1')),
        #     (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), Decimal('1')),
        #     (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), Decimal('0.5')),
        #     (~Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('0.5')),
        # ]
        u = obj.user
        filters_with_weights = [
            (Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('1')),
            (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), Decimal('1')),
            (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), Decimal('0.5')),
            (~Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('0.5')),
        ]

        for condition, weight in filters_with_weights:
            value = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
            total += Decimal(value) * weight

        # Ensure decimal string with two places
        try:
            return str(total.quantize(Decimal('0.00')))
        except Exception:
            return str(Decimal(float(total)).quantize(Decimal('0.00')))

    def get_remaining_target(self, obj):
        # target_amount minus achieved_amount
        try:
            achieved = Decimal(self.get_achieved_amount(obj))
        except Exception:
            achieved = Decimal('0.00')

        try:
            target = Decimal(obj.target_amount or 0)
        except Exception:
            target = Decimal(float(obj.target_amount or 0))

        remaining = target - achieved
        try:
            return str(remaining.quantize(Decimal('0.00')))
        except Exception:
            return str(Decimal(float(remaining)).quantize(Decimal('0.00')))

    def get_original_target_amount(self, obj):
        # Read from UserTarget.target – the user's canonical base target.
        # Falls back to the row's own original_target_amount, then target_amount.
        from accounts.models import UserTarget
        try:
            user_target = UserTarget.objects.filter(user=obj.user).first()
            if user_target is not None:
                val = user_target.target
            elif obj.original_target_amount is not None:
                val = obj.original_target_amount
            else:
                val = obj.target_amount
        except Exception:
            val = obj.target_amount

        try:
            dec = Decimal(val)
        except Exception:
            try:
                dec = Decimal(float(val))
            except Exception:
                dec = Decimal('0.00')
        try:
            return str(dec.quantize(Decimal('0.00')))
        except Exception:
            return str(dec)