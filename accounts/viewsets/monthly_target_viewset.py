from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import filters as drf_filters
from django_filters import rest_framework as filters
from accounts.models import MonthlyTarget
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.db import models
from accounts.serializers.monthly_target_serializer import (
    MonthlyTargetSerializer, MonthlyTargetCreateSerializer
)
from lead.custom_pagination import Paginator


class MonthlyTargetViewSet(viewsets.ModelViewSet):
    queryset = MonthlyTarget.objects.all()
    serializer_class = MonthlyTargetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        filters.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    )
    filterset_fields = ['id', 'user', 'user__username', 'month', 'year']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['year', 'month', 'target_amount', 'created_at']
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = Paginator


    def get_queryset(self):
        user = self.request.user
        base_qs = super().get_queryset()
        
        last_3_months_flag = str(self.request.query_params.get('last_3_months', '')).lower() in ('true', '1', 'yes')
        if last_3_months_flag:
            today = timezone.now().date()
            year = today.year
            month = today.month
            q_last3 = Q()
            for _ in range(3):
                q_last3 |= Q(year=year, month=month)
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
            base_qs = base_qs.filter(q_last3)

        def allowed_months_q_for_user(target_user):
            """Build a Q object that matches MonthlyTarget months that fall
            within any active period recorded for `target_user`.
            """
            try:
                from accounts.models import UserActiveHistory
            except Exception:
                return Q()

            histories = list(UserActiveHistory.objects.filter(user=target_user).order_by('changed_at'))
            # If no history, fall back to current user.is_active:
            # - if active, allow all months
            # - if inactive, allow months up to current month
            if not histories:
                if target_user.is_active:
                    return Q()
                now = timezone.now()
                return Q(year__lt=now.year) | Q(year=now.year, month__lte=now.month)

            periods = []
            active_start = None
            
            # If first history is inactive, assume user was active from date_joined until then
            if histories and not histories[0].is_active and target_user.date_joined:
                active_start = target_user.date_joined
            
            for h in histories:
                if h.is_active:
                    if active_start is None:
                        active_start = h.changed_at
                        if h == histories[0] and target_user.date_joined and target_user.date_joined < active_start:
                            active_start = target_user.date_joined
                else:
                    if active_start is not None:
                        periods.append((active_start, h.changed_at))
                        active_start = None

            if active_start is not None:
                if target_user.is_active:
                    periods.append((active_start, None))
                else:
                    periods.append((active_start, timezone.now()))
            elif target_user.is_active:
                # Current user is active, but the history does not contain an open
                # active period. This can happen if the latest active transition was
                # not recorded, so assume the user became active as of now.
                periods.append((timezone.now(), None))

            if not periods:
                return Q(pk__in=[])

            q = Q()
            for start, end in periods:
                sy, sm = start.year, start.month
                
                # Include month if: period_start <= month_end AND period_end >= month_start
                cond_period_starts_before_month_end = (
                    Q(year__gt=sy) | Q(year=sy, month__gte=sm)
                )
                
                if end:
                    ey, em = end.year, end.month
                    # For ended periods, include months BEFORE the end month only
                    # (exclude the end month since user became inactive during that month)
                    cond_period_ends_before_month = (
                        Q(year__lt=ey) | Q(year=ey, month__lt=em)
                    )
                    q |= (cond_period_starts_before_month_end & cond_period_ends_before_month)
                else:
                    # No end date - include all months from start onwards
                    q |= cond_period_starts_before_month_end

            return q
        # If non-admin, restrict to their own targets and apply deactivation cutoff
        if not user.groups.filter(name='Admin').exists():
            qs = base_qs.filter(user=user)
            # apply filtering based on recorded active periods for this user
            q_allowed = allowed_months_q_for_user(user)
            # If q_allowed is empty (no allowed months), return empty queryset
            if q_allowed == Q(pk__in=[]):
                return qs.none()
            if q_allowed:
                qs = qs.filter(q_allowed)
            return qs

        # Admins: if filtering by a single user via query params, apply same cutoff for that user
        user_param = self.request.query_params.get('user')
        if user_param:
            try:
                from django.contrib.auth.models import User as AuthUser
                target_user = AuthUser.objects.filter(pk=int(user_param)).first()
            except Exception:
                target_user = None
            if target_user:
                # Always apply history-based allowed-month filtering for the
                # requested user (if history is present). This ensures admin
                # requests see the same month visibility as regular users.
                q_allowed = allowed_months_q_for_user(target_user)
                if q_allowed == Q(pk__in=[]):
                    return base_qs.none()
                if q_allowed:
                    return base_qs.filter(user=target_user).filter(q_allowed)

        # Default: admins see all, but apply per-user month-visibility
        # so admins don't accidentally see months outside a user's active periods.
        from django.contrib.auth.models import User as AuthUser

        user_ids = base_qs.values_list('user', flat=True).distinct()
        q_all = Q(pk__in=[])
        for uid in user_ids:
            try:
                target_user = AuthUser.objects.get(pk=uid)
            except AuthUser.DoesNotExist:
                continue
            q_allowed = allowed_months_q_for_user(target_user)
            if q_allowed == Q(pk__in=[]):
                # no allowed months for this user, skip
                continue
            q_all |= (Q(user__id=uid) & q_allowed)

        if q_all == Q(pk__in=[]):
            return base_qs.none()
        return base_qs.filter(q_all)

    def perform_create(self, serializer):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            # Admins can create for any user
            serializer.save()
        else:
            # Non-admins can only create for themselves
            serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if user.groups.filter(name='Admin').exists() or instance.user == user:
            # Admins can update any, users can update their own
            serializer.save()
        else:
            # Forbidden
            return Response({"detail": "You do not have permission to update this target."}, status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.groups.filter(name='Admin').exists() or instance.user == user:
            # Admins can delete any, users can delete their own
            instance.delete()
        else:
            # Forbidden
            return Response({"detail": "You do not have permission to delete this target."}, status=status.HTTP_403_FORBIDDEN)

    def get_serializer_class(self):
        if self.action == 'create':
            return MonthlyTargetCreateSerializer
        if self.action in ['update', 'partial_update']:
            return MonthlyTargetCreateSerializer
        return MonthlyTargetSerializer


