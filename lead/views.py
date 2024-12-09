from django.shortcuts import render
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from lead.models import Contact,Opportunity_Stage, Employee, Designation
from lead.serializers.contactserializer import ContactSerializer
from lead.serializers.opportuinityserializer import CurrencySerializer, OpportunitySerializer,PostOpportunitySerializer,LeadNameSerializer,StageNameSerializer,PostNoteSerializer,StageUpdateSerializer,StageGetSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.leadserializer import PostLeadSerializer,  LeadSerializer,MarketSegmentSerializer,FocusSegmentSerializer,CountrySerializer,StateSerializer,EmpSerializer,TagSerializer, VerticalSerializer
from .models import Lead,Employee,Opportunity
from accounts.models import Market_Segment,Focus_Segment,Country,Stage,State,Tag,Vertical,Contact_Status,Lead_Source
from rest_framework.pagination import PageNumberPagination
from .serializers.contactserializer import LeadSourceSerializer,ContactStatusSerializer,PostContactSerializer
from .serializers.noteserializer import PostNoteSerializer
from django.db.models import Min, Max
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group

# get users if user group is TM or BDE

class UsersForLead(APIView):

    def get(self, request):
        target_groups = Group.objects.filter(name__in=["TM", "BDE", "Tele Marketer"])
        users = User.objects.filter(groups__in=target_groups).distinct()

        user_data = []
        for user in users:
            full_name = f"{user.first_name} {user.last_name}"
            group_names = [group.name for group in user.groups.all() if group.name in ["TM", "BDE"]]
            
            user_data.append({
                "id":user.id,
                "full_name": full_name,
                "groups": group_names
            })

        # Return the user data with full name and group names
        return Response(user_data, status=status.HTTP_200_OK)
    
# get users if user group is BDM
class GetLeadOwner(APIView):

    def get(self, request):
        target_groups = Group.objects.filter(name__in=["BDM"])
        users = User.objects.filter(groups__in=target_groups).distinct()

        user_data = []
        for user in users:
            full_name = f"{user.first_name} {user.last_name}"
            group_names = [group.name for group in user.groups.all() if group.name in ["BDM"]]
            
            user_data.append({
                "id":user.id,
                "full_name": full_name,
                "groups": group_names
            })

        # Return the user data with full name and group names
        return Response(user_data, status=status.HTTP_200_OK)
 
#Lead creation and details
class LeadView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
    # Deserialize incoming request data into a lead
     serializer = PostLeadSerializer(data=request.data)
    
     if serializer.is_valid():
        # Save the lead and assign the current logged-in user as the 'created_by'
        lead = serializer.save(created_by=request.user)
        
        # Ensure that the 'lead_owner' is set and is a valid User object
        try:
            lead_owner = lead.lead_owner  # Access the lead_owner from the created lead
            
            if not lead_owner:
                raise ValueError("Lead owner is not set.")
                
            recipient_email = lead_owner.email
             # Get the lead owner's email
            
        except (User.DoesNotExist, ValueError) as e:
            return Response({"error": f"Notification email not set for user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

                    
        contact_data = {
            "lead": lead,
            "name": lead.name,  
            "email_id": lead.company_email,  
            "phone_number": lead.company_number, 
            "created_by": request.user,
            "is_active": True,
            "is_primary": True, 
        }

        # Create the Contact instance
        contact = Contact.objects.create(**contact_data)
        
        # Send an email after the lead is created
        subject = "New Lead Created"
        message = (
            f"A new lead has been created by {request.user.username}.\n\n"
            "Please log in to the CRM system to view more details and take further action:\n"
            "http://crm.decodeschool.com/\n\n"
            
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],  # Use dynamic email from lead_owner
                fail_silently=False,  # Ensure the failure is reported
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return a success response with lead data
        return Response({"message": "Lead Created Successfully!","data": serializer.data}, status=status.HTTP_201_CREATED)
    
     return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, lead_id=None):
        if lead_id:
            try:
                lead=Lead.objects.get(id=lead_id)
                serializer = PostLeadSerializer(lead, data=request.data, partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                    if(request.user!=lead.lead_owner):
                        message = f"The lead '{lead.name}' has been updated by '{request.user}'."
                        Notification.objects.create(
                            receiver=lead.lead_owner,
                            message=message,
                        )
                    if(request.user!=lead.created_by):
                        message = f"The lead '{lead.name}' has been updated by '{request.user}'."
                        Notification.objects.create(
                            receiver=lead.created_by,
                            message=message,
                        )
                    return Response({"message":"Lead Updated Successfully!","data":serializer.data},status=status.HTTP_200_OK)
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'lead_id is required for update'}, status=status.HTTP_400_BAD_REQUEST)


    
    def delete(self, request, lead_id=None):
        if lead_id:
            try:
                lead = Lead.objects.get(id=lead_id)
                lead.is_active = False  # Soft-delete (deactivation)
                lead.save()
                if(request.user!=lead.lead_owner):
                        message = f"The lead '{lead.name}' has been Deactivated."
                        Notification.objects.create(
                            receiver=lead.lead_owner,
                            message=message,
                        )
                if(request.user!=lead.created_by):
                    message = f"The lead '{lead.name}' has been Deactivated."
                    Notification.objects.create(
                        receiver=lead.created_by,
                        message=message,
                    )
                return Response({"message": "Lead deactivated!"}, status=status.HTTP_200_OK)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'lead_id is required for deactivation'}, status=status.HTTP_400_BAD_REQUEST)
    
    class LeadPagination(PageNumberPagination):
        page_size = 10  
        page_size_query_param = 'page_size'
        max_page_size = 1000

    def get(self, request, lead_id=None):
        if lead_id:
            try:
                lead = Lead.objects.get(id=lead_id)
                serializer = LeadSerializer(lead)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Lead.DoesNotExist:
                return Response([], status=status.HTTP_200_OK)
        else:
            # Filter active leads and order by latest created
            user = request.user
            if user.employee.designation.designation=='ADMIN':
                leads=Lead.objects.filter(is_active=True).order_by('-id')
            else:
                leads = Lead.objects.filter(Q(lead_owner=user)|Q(created_by=user)|Q(lead_assignment__assigned_to=user),is_active=True).distinct().order_by('-id')
            min_revenue = leads.aggregate(min_revenue=Min('annual_revenue'))['min_revenue']
            max_revenue = leads.aggregate(max_revenue=Max('annual_revenue'))['max_revenue']
            # Apply pagination using query parameters
            paginator = self.LeadPagination()
            result_page = paginator.paginate_queryset(leads, request)
            
            # Return paginated response
           
            paginated_response = paginator.get_paginated_response(LeadSerializer(result_page, many=True).data)
            paginated_response.data['min_revenue'] = min_revenue
            paginated_response.data['max_revenue'] = max_revenue

            return paginated_response
        
        
    
class FocusSegmentListByVertical(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, vertical_id):
        focus_segments = Focus_Segment.objects.filter(vertical_id=vertical_id, is_active=True)
        serializer = FocusSegmentSerializer(focus_segments, many=True)
        return Response(serializer.data)


class DropdownListView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, country_id=None):
        dropdown_type = request.query_params.get('type')

        if dropdown_type == 'market_segment':
            market_segments=Market_Segment.objects.all()
            serializer=MarketSegmentSerializer(market_segments,many=True)
            return Response(serializer.data)
        elif dropdown_type == 'focus_segment':
            focus_segments=Focus_Segment.objects.all()
            serializer=FocusSegmentSerializer(focus_segments,many=True)
            return Response(serializer.data)
        elif dropdown_type == 'country':
            countries=Country.objects.all()
            serializer=CountrySerializer(countries,many=True)
            return Response(serializer.data)
        elif dropdown_type == 'state' and country_id:
            states=State.objects.filter(country=country_id)
            serializer=StateSerializer(states,many=True)
            return Response(serializer.data)
        elif dropdown_type =='tags':
            tags=Tag.objects.all()
            serializer=TagSerializer(tags,many=True)
            return Response(serializer.data)
        
        elif dropdown_type == 'owner':
            designations = ['BDM']
            employees = Employee.objects.filter(designation__designation__in=designations, is_active=True)
            serializer = EmpSerializer(employees, many=True)
            return Response(serializer.data)
        
        elif dropdown_type=='created_by':
            employees = Employee.objects.all()
            serializer = EmpSerializer(employees, many=True)
            return Response(serializer.data)
        
        elif dropdown_type=='vertical':
            verticals = Vertical.objects.all()
            serializer = VerticalSerializer(verticals, many=True)
            return Response(serializer.data)
        
        elif dropdown_type == 'assigned_to':
            designations = ['TM', 'BDM', 'BDE']
            employees = Employee.objects.filter(designation__designation__in=designations, is_active=True)
            serializer = EmpSerializer(employees, many=True)
            return Response(serializer.data)
        

        else:
            return Response({'error': 'Invalid dropdown type or missing parameters.'}, status=status.HTTP_400_BAD_REQUEST)

from django.db.models import Q, Min, Max
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Lead
from .serializers.leadfilterserializer import LeadFilterSerializer

class LeadPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class LeadFilterView(APIView):
    pagination_class = LeadPagination
    def post(self, request, *args, **kwargs):
        return self.filter_and_paginate(request)

    def get(self, request, *args, **kwargs):
        return self.filter_and_paginate(request)

    def filter_and_paginate(self, request):
        try:
            body = request.data if request.method == 'POST' else request.query_params
            user = request.user
            if user.employee.designation.designation=='ADMIN':
                leads=Lead.objects.filter(is_active=True).order_by('-id')
            else:
                leads = Lead.objects.filter(Q(lead_owner=user)|Q(created_by=user)|Q(lead_assignment__assigned_to=user),is_active=True).distinct().order_by('-id')

            # Apply filters
            if vertical_ids := body.get('vertical_id'):
                leads = leads.filter(focus_segment__vertical__id__in=vertical_ids)
            if focus_segment_ids := body.get('focus_segment'):
                leads = leads.filter(focus_segment__id__in=focus_segment_ids)
            if market_segment_ids := body.get('market_segment'):
                leads = leads.filter(market_segment__id__in=market_segment_ids)
            if state_ids := body.get('state_id'):
                leads = leads.filter(state__id__in=state_ids)
            if country_ids := body.get('country_id'):
                leads = leads.filter(country__id__in=country_ids)
            if created_on_dates := body.get('created_on'):
                leads = leads.filter(created_on__in=created_on_dates)
            if tag_ids := body.get('tags'):
                leads = leads.filter(tags__in=tag_ids).distinct()
            if min_revenue := body.get('min_revenue'):
                leads = leads.filter(annual_revenue__gte=min_revenue).exclude(annual_revenue__isnull=True)
            if max_revenue := body.get('max_revenue'):
                leads = leads.filter(annual_revenue__lte=max_revenue).exclude(annual_revenue__isnull=True)

            if search_key := body.get('key'):
                leads = leads.filter(
                    Q(name__icontains=search_key) |
                    Q(company_email__icontains=search_key) |
                    Q(company_number__icontains=search_key) |
                    Q(fax__icontains=search_key) |
                    Q(tags__tag__icontains=search_key) |
                    Q(lead_owner__username__icontains=search_key) |
                    Q(created_by__username__icontains=search_key) |
                    Q(state__state_name__icontains=search_key) |
                    Q(country__country_name__icontains=search_key) |
                    Q(focus_segment__focus_segment__icontains=search_key) |
                    Q(focus_segment__vertical__vertical__icontains=search_key) |
                    Q(market_segment__market_segment__icontains=search_key)
                ).distinct()

            leads_with_revenue = leads.exclude(annual_revenue__isnull=True)  # Exclude null revenue entries
            min_revenue = leads_with_revenue.aggregate(min_revenue=Min('annual_revenue'))['min_revenue']
            max_revenue = leads_with_revenue.aggregate(max_revenue=Max('annual_revenue'))['max_revenue']

            # Pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(leads, request)
            serializer = LeadSerializer(page, many=True)
            
            # Add min_revenue and max_revenue to paginated response
            response_data = paginator.get_paginated_response(serializer.data)
            response_data.data['min_revenue'] = min_revenue
            response_data.data['max_revenue'] = max_revenue
            return response_data
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

from datetime import datetime, timedelta
from django.db.models import Count, Q, OuterRef, Subquery
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Lead, Contact, Lead_Source  # Import your models here
from rest_framework import status

class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            body = request.data
            leads = Lead.objects.all()
            total_leads_count = leads.count()
            start_date = body.get('start_date')
            end_date = body.get('end_date')
            start_date_obj = None
            end_date_obj = None

            # Initialize filters with an empty Q object
            filters = Q()

            # Extract filters from the request body
            owner_ids = body.get('owner')
            created_by_ids = body.get('created_by')
            vertical_ids = body.get('vertical')
            focus_segments = body.get('focus_segment')
            states = body.get('state')
            countries = body.get('country')
            market_segments = body.get('market_segment')
            lead_source_ids = body.get('lead_source')
            assigned_to_id = body.get('assigned_to')

            # Get the employee object (this assumes the User model is related to Employee)
            employee = request.user.employee  # Assuming Employee model has a OneToOneField with User

            # Role-based filtering
            if employee.designation.designation == 'ADMIN':
                # Admin can see all leads
                pass  # No filtering for admin
            elif employee.designation.designation == 'BDM':
                # BDM can only see the leads they own or manage
                leads = leads.filter(lead_owner=request.user)
            else:
                # Other roles (e.g., DM, TM, BDE) see no leads (or define specific filtering for these roles)
                leads = leads.none()

            # Filtering based on other fields
            if owner_ids:
                leads = leads.filter(lead_owner_id=owner_ids)         
            if created_by_ids:
                leads = leads.filter(created_by_id=created_by_ids)
            if vertical_ids:
                leads = leads.filter(focus_segment__vertical_id=vertical_ids)
            if focus_segments:
                leads = leads.filter(focus_segment_id=focus_segments)
            if states:
                leads = leads.filter(state_id=states)
            if countries:
                leads = leads.filter(country_id=countries)
            if market_segments:
                leads = leads.filter(market_segment_id=market_segments)
            
            if assigned_to_id:
                lead_ids = Lead_Assignment.objects.filter(assigned_to_id=assigned_to_id)
               # print(lead_ids)
                lead_ids = lead_ids.values_list('lead_id', flat=True)
                leads = leads.filter(id__in=lead_ids)
               # print(leads)


            if not start_date and not end_date:
                today = datetime.now()
                start_default = today.replace(year=today.year - 1, month=today.month+1, day=1)
                end_default = today.replace(day=today.day, month=today.month) 
                # print(start_default)
                # print(end_default)
                filters &= Q(created_on__range=(start_default, end_default))
            else:
                if start_date:
                    start_date_obj = datetime.fromisoformat(start_date)
                    filters &= Q(created_on__gte=start_date_obj)
                if end_date:
                    end_date_obj = datetime.fromisoformat(end_date)
                    filters &= Q(created_on__lte=end_date_obj)

            # Apply filters to the leads queryset
          #  print(leads)
            leads = leads.filter(filters)
           # print(leads)
            filtered_leads_count = leads.count()
            
            # Generating chart_data
            current_date = start_date_obj if start_date_obj else datetime.now()
            chart_data = []
            if end_date_obj:
                while current_date <= end_date_obj:
                    chart_data.append(current_date.strftime('%Y-%m'))
                    next_month = current_date.month % 12 + 1
                    next_year = current_date.year + (current_date.month // 12)
                    current_date = current_date.replace(year=next_year, month=next_month)
            else:
                for i in range(12):
                    past_date = (datetime.now() - timedelta(days=30 * i))
                    chart_data.append(past_date.strftime('%Y-%m'))
            chart_data.sort()

            monthly_counts = {month: 0 for month in chart_data}

            # Query for monthly data
            monthly_data = (
                leads
                .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on'))
                .values('year', 'month')
                .annotate(count=Count('id'))
                .order_by('year', 'month')
            )

            # Populate monthly_counts dictionary with actual data
            for entry in monthly_data:
                month_str = f"{entry['year']}-{str(entry['month']).zfill(2)}"
                monthly_counts[month_str] = entry['count']

            # Prepare response data for chart data
            monthly_data = {
                "monthly_data": [{"month": month, "count": count} for month, count in monthly_counts.items()]
            }

            # First contact source query (Subquery to get the lead source of the first contact)
            first_contact_query = Contact.objects.filter(
                lead=OuterRef('pk')
            ).order_by('created_on').values('lead_source')[:1]

            # Get the count of leads grouped by the lead source of the first contact
            lead_counts = Lead.objects.filter(id__in=leads.values('id')).annotate(
                first_contact_source=Subquery(first_contact_query)
            ).values('first_contact_source').annotate(
                lead_count=Count('id')
            ).order_by('-lead_count')

            # Prepare lead source counts based on first contact
            lead_source_counts = {}
            for source in lead_counts:
                lead_source = source.get('first_contact_source')
                if lead_source:
                    try:
                        lead_source_name = Lead_Source.objects.get(id=lead_source).source
                        lead_source_counts[lead_source_name] = source['lead_count']
                    except Lead_Source.DoesNotExist:
                        # Handle the case where the Lead_Source is not found
                        lead_source_counts["Unknown"] = source['lead_count']

            # Return the response with all the data
            return JsonResponse({
                "total_leads_count": total_leads_count,
                "filtered_count": filtered_leads_count,
                "chart_data": monthly_data,  # Ensures chart_data respects start_date and end_date or defaults to 12 months
                "lead_source_counts": lead_source_counts  # Counts based on the lead source of the first contact
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from lead.models import Opportunity, Note
from lead.serializers.noteserializer import NoteSerializer


class OpportunityNotesView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, opportunity_id):
        try:
            user=request.user
            if user.employee.designation.designation=='ADMIN':
                notes = Note.objects.filter(
            opportunity=opportunity_id).order_by('-id')
            else:
                notes = Note.objects.filter(
                opportunity=opportunity_id,  
            ).filter(
                Q(opportunity__lead__lead_owner=user) |  
                Q(opportunity__lead__created_by=user) |  # Filter based on lead creator
                Q(opportunity__created_by=user) |       
                Q(note_by=user)                      
            ).order_by('-id')

            if not notes.exists():
                return Response([])

            serializer = NoteSerializer(notes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            body = request.data
            user=request.user
            opportunity_id = body.get('opportunity_id')
            note_by = user
            note = body.get('note')
            if not opportunity_id or not note or not note_by:
                return Response({"error": "opportunity_id, note, and note_by are required fields."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                opportunity = Opportunity.objects.get(id=opportunity_id)
            except Opportunity.DoesNotExist:
                return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
            # try:
            #     note_by = User.objects.get(id=note_by)
            # except User.DoesNotExist:
            #     return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            new_note = Note.objects.create(
                opportunity=opportunity,
                note=note,
                note_by=note_by
            )
            serializer = NoteSerializer(new_note)
            return Response("Note added successfully", status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error ": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request, note_id):
        try:
            try:
                note = Note.objects.get(id=note_id)
            except Note.DoesNotExist:
                return Response({"error": "Note not found for the specified opportunity"}, status=status.HTTP_404_NOT_FOUND)
            new_note_content = request.data.get("note", None)
            if new_note_content:
                note.note = new_note_content 
                note.save()
                serializer = NoteSerializer(note)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "New note content is required"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetNotesByLeadView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, lead_id):
        try:
            try:
                lead = Lead.objects.get(id=lead_id)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
            opportunities = Opportunity.objects.filter(lead=lead)
            notes = Note.objects.filter(opportunity__in=opportunities).order_by('-id')
            serializer = NoteSerializer(notes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#--------------sumith--------


from .models import Task, Contact, Task_Assignment
from .serializers.taskserializer import TaskSerializer, GetTaskSerializer
from django.utils.timezone import now, timedelta
class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        assigned_by_user = request.user  # User creating the task
        contact_id = request.data.get('contact_id')
        log_id = request.data.get('log_id')
        task_date_time = request.data.get('task_date_time')
        task_detail = request.data.get('task_detail')
        task_type = 'M'  # Task type is manual

        try:
            # Retrieve the Contact object
            contact = Contact.objects.get(id=contact_id)

            # Retrieve the Log object if provided
            log = Log.objects.get(id=log_id) if log_id else None

            # Create a task instance
            task = Task.objects.create(
                contact=contact,
                log=log,
                task_date_time=task_date_time,
                task_detail=task_detail,
                created_by=assigned_by_user,
                tasktype=task_type
            )

            # Prepare the serializer response
            serializer = TaskSerializer(task)

            # Email notification to the lead owner, if they exist
            lead_owner = getattr(contact, 'lead_owner', None)
            

            # Email notification to the task creator (task owner)
            subject_task_owner = "Create New Task"
            message_task_owner = (
                f"Hello {assigned_by_user.username},\n\n"
                f"You have successfully created a new task.\n"
                "Please log in to the CRM system to view more details and take further action:\n"
                "http://crm.decodeschool.com/\n\n"
                
                
            )
            try:
                send_mail(
                    subject_task_owner,
                    message_task_owner,
                    settings.DEFAULT_FROM_EMAIL,
                    [assigned_by_user.email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response({"error": f"Failed to send email to task owner: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "Task created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        except Log.DoesNotExist:
            return Response({'error': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum
from .models import Opportunity 

class OpportunityReportView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            # Get filter parameters from request
            vertical = request.data.get('vertical')
            focus_segment = request.data.get('focus_segment')
            state = request.data.get('state')
            country = request.data.get('country')
            market_segment = request.data.get('market_segment')
            owner_id = request.data.get('owner')
            lead = request.data.get('lead')

            # Start by filtering active opportunities
            opportunities = Opportunity.objects.filter()

            # Apply filters based on the request data
            if vertical:
                opportunities = opportunities.filter(lead__focus_segment__vertical=vertical)
            if focus_segment:
                opportunities = opportunities.filter(lead__focus_segment=focus_segment)
            if state:
                opportunities = opportunities.filter(lead__state=state)
            if country:
                opportunities = opportunities.filter(currency_type_id=country)
            if market_segment:
                opportunities = opportunities.filter(lead__market_segment=market_segment)
            if owner_id:
                opportunities = opportunities.filter(owner_id=owner_id)
            if lead:
                opportunities = opportunities.filter(lead__id=lead)
            

            # Group by stage and calculate count and sum of opportunity values
            stage_data = opportunities.values('stage__id', 'stage__stage').annotate(
                opportunity_count=Count('id'),
                total_value=Sum('opportunity_value')
            ).order_by('stage__id')

            # Prepare the response data
            response_data = [
                {
                    "stage_id": stage['stage__id'],
                    "stage": stage['stage__stage'],
                    "opportunity_count": stage['opportunity_count'],
                    "total_value": stage['total_value']
                }
                for stage in stage_data
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Return error response in case of an issue
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#-----For PUT & DELETE (Is_active=false)-------------------------------------------------

class TaskManagement(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, id):
        try:
            # Get the user object
          #  user = User.objects.get(id=id)
            user=request.user
            # 1. Gather all tasks that are associated with leads owned by the user
            leads_owned_by_user = Lead.objects.filter(lead_owner=user)
            tasks_related_to_leads = Task.objects.filter(contact__lead__in=leads_owned_by_user)

            # 2. Gather all tasks directly associated with the user (created_by or assigned_to)
            tasks_created_by_user = Task.objects.filter(created_by=user)
            tasks_assigned_to_user = Task_Assignment.objects.filter(assigned_to=user).values_list('task', flat=True)
            tasks_assigned_to_user = Task.objects.filter(id__in=tasks_assigned_to_user)

            
            if user.employee.designation.designation=='ADMIN':
                all_tasks=Task.objects.filter(is_active=True).order_by('-id')

            else:
                all_tasks = tasks_related_to_leads | tasks_created_by_user | tasks_assigned_to_user
                all_tasks = all_tasks.distinct()

            # Get current date
            today = now().date()

            # Get all tasks from today onwards
            tasks_from_today_onwards = all_tasks.filter(task_date_time__date__gte=today)

            # Serialize the tasks
            tasks_serialized = GetTaskSerializer(tasks_from_today_onwards, many=True).data

            # Response data
            response_data = {
                'tasks_from_today_onwards': tasks_serialized,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id):
        try:
            # Get the user object
           # user = User.objects.get(id=id)
            user=request.user
            category = request.data.get('category')  # Get category from the body
            page = request.data.get('page', 1)  # Default to the first page if not provided
            
            # Current time and time ranges
            today = now().date()
            tomorrow = today + timedelta(days=1)
            next_7_days = today + timedelta(days=7)

            # Get all tasks related to the user
            leads_owned_by_user = Lead.objects.filter(lead_owner=user)
            tasks_related_to_leads = Task.objects.filter(contact__lead__in=leads_owned_by_user)
            tasks_created_by_user = Task.objects.filter(created_by=user)
            tasks_assigned_to_user = Task_Assignment.objects.filter(assigned_to=user).values_list('task', flat=True)
            tasks_assigned_to_user = Task.objects.filter(id__in=tasks_assigned_to_user)

            if user.employee.designation.designation=='ADMIN':
                all_tasks=Task.objects.filter(is_active=True).order_by('-id')
            else:
                all_tasks = tasks_related_to_leads | tasks_created_by_user | tasks_assigned_to_user
                all_tasks = all_tasks.distinct()






            # Filter tasks based on the category
            if category == "today":
                filtered_tasks = all_tasks.filter(task_date_time__date=today)
            elif category == "tomorrow":
                filtered_tasks = all_tasks.filter(task_date_time__date=tomorrow)
            elif category == "next_7_days":
                filtered_tasks = all_tasks.filter(task_date_time__date__range=[tomorrow + timedelta(days=1), next_7_days])
            else:
                return Response({'error': 'Invalid category'}, status=status.HTTP_400_BAD_REQUEST)

            # Paginate the results
            paginator = CustomPagination()
            paginated_tasks = paginator.paginate_queryset(filtered_tasks, request)

            # Serialize paginated tasks
            tasks_serialized = GetTaskSerializer(paginated_tasks, many=True).data

            # Response data
            response_data = {
                'count': paginator.page.paginator.count,
                'tasks': tasks_serialized
            }
            return paginator.get_paginated_response(response_data)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
       # assigned_by_user = User.objects.get(id=2)  # Static assignment, change if needed
        try:
            # Retrieve the task object
            task = Task.objects.get(id=id)

            # Get data from request body
            contact_id = request.data.get('contact_id')
            log_id = request.data.get('log_id')
            task_date_time = request.data.get('task_date_time')
            task_detail = request.data.get('task_detail')
            task_type = request.data.get('tasktype', 'M')  # Default to 'M' if not provided
            
            log = None
            if log_id:
                try:
                    log = Log.objects.get(id=log_id)
                except Log.DoesNotExist:
                    return Response({"error": "Log not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update task fields
            task.contact = Contact.objects.get(id=contact_id)
            task.log = log
            task.task_date_time = task_date_time
            task.task_detail = task_detail
            task.created_by = request.user  # Or request.user for dynamic assignment
            task.tasktype = task_type

            # Save updated task
            task.save()
            serializer = TaskSerializer(task)
            return Response({"message": "Task updated successfully", "task": serializer.data}, status=status.HTTP_200_OK)

        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the task object
            task = Task.objects.get(id=id)

            if not task.is_active:
                return Response({"message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

            # Delete the task
            task.is_active = False
            task.save()

            return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    

#-------------------VS-----------------------------
from rest_framework.pagination import PageNumberPagination
class OpportunityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
class Opportunity_ByLeadId(APIView):
    pagination_class = OpportunityPagination
    permission_classes=[IsAuthenticated]
    def get(self, request, lead_id):
        if lead_id:
            user=request.user
            if user.employee.designation.designation=='ADMIN':
                opportunities = Opportunity.objects.filter(lead__id=lead_id)
                opportunities=opportunities.filter(is_active=True).order_by('-id')
            else:
                opportunities = Opportunity.objects.filter(Q(lead__id=lead_id),
                Q(lead__lead_owner=user)|Q(lead__created_by=user)|Q(created_by=user)).distinct().order_by('-id')
            if opportunities.exists():
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(opportunities, request)
                if page is not None:
                    serializer = OpportunitySerializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)
                else:
                    serializer = OpportunitySerializer(opportunities, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)

    
class Opportunity_details(APIView):
    permission_classes=[IsAuthenticated]
    class OpportunityPagination(PageNumberPagination):
        page_size = 10
        page_size_query_param="page_size"
        max_page_size = 1000

    def get(self, request, opportunity_id=None):
        if opportunity_id:
            try:
                opportunity = Opportunity.objects.get(id=opportunity_id)
                serializer = OpportunitySerializer(opportunity) 
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Opportunity.DoesNotExist:
                return Response({"detail": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
            if user.employee.designation.designation=='ADMIN':
                opportunities=Opportunity.objects.filter(is_active=True)
            else:
                opportunities = Opportunity.objects.filter(
                    Q(created_by=user) |    Q(owner=user)        |         
                    Q(lead__lead_owner=user) |                
                    Q(lead__created_by=user)                 
                ).distinct().order_by('-created_on', '-id')    

           
            paginator=self.OpportunityPagination()
            Opportunity_pages=paginator.paginate_queryset(opportunities,request)
            serializer = OpportunitySerializer(Opportunity_pages, many=True)
            return paginator.get_paginated_response(serializer.data)
    

    def post(self, request, opportunity_id=None):
        data = request.data.copy()
        data.update(request.FILES)
        
        serializer = PostOpportunitySerializer(data=data)
        
        if serializer.is_valid():
            opportunity = serializer.save(created_by=request.user)
            created_by = request.user

            # Handle the Stage update or stage creation
            stage_data = {
                'opportunity': opportunity.id,  
                'stage': data.get('stage'),   # Assuming stage_id is included in the request data
                'moved_by': created_by.id, 
            }

            serializer1 = StageUpdateSerializer(data=stage_data)
            
            if serializer1.is_valid():
                serializer1.save()  
            else:
                return Response(serializer1.errors, status=status.HTTP_400_BAD_REQUEST) 
            
           

            # Send email to the lead owner
            lead = opportunity.lead  # Assuming 'lead' is a related field on the Opportunity model
            lead_owner = lead.lead_owner  # Assuming 'lead_owner' is a field on Lead
            subject_lead_owner = "Opportunity Linked to Your Lead"
            message_lead_owner = (
                f"Hello {lead_owner.username},\n\n"
                f"The opportunity '{opportunity.name}' has been linked to your lead '{lead.name}'.\n"
                "Please log in to the CRM system to view more details:\n"
                "http://crm.decodeschool.com/\n\n"
                
            )

            try:
                

                # Email to lead owner
                send_mail(
                    subject_lead_owner,
                    message_lead_owner,
                    settings.DEFAULT_FROM_EMAIL,
                    [lead_owner.email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "Opportunity created", "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  

    def put(self, request, opportunity_id=None):
        try:
            # Retrieve the opportunity object
            opportunity = Opportunity.objects.get(id=opportunity_id)
            
            # Store old stage value
            old_stage = opportunity.stage.id if opportunity.stage else None

            # Update opportunity with incoming data
            data = request.data.copy()
            data.update(request.FILES) 
            
            # Create serializer instance for updating the opportunity
            serializer = PostOpportunitySerializer(opportunity, data=data, partial=True)
            
            if serializer.is_valid():
                updated_opportunity = serializer.save()  # Save the updated opportunity

                # Check if the stage has changed
                new_stage = updated_opportunity.stage.id if updated_opportunity.stage else None
                if old_stage != new_stage:
                    # Fetch the new stage object to get its probability
                    stage = Stage.objects.get(id=new_stage)
                    
                    # Update the probability_in_percentage field based on the new stage's probability
                    updated_opportunity.probability_in_percentage = stage.probability
                    updated_opportunity.save()  # Save the updated opportunity with new probability

                    # Create a new entry in the Stage model (this is done when the stage changes)
                    stage_data = {
                        'opportunity': updated_opportunity.id,
                        'stage': new_stage,
                        'moved_by': updated_opportunity.created_by.id,
                    }

                    serializer1 = StageUpdateSerializer(data=stage_data)

                    if serializer1.is_valid():
                        serializer1.save()  # Save the new stage record
                    else:
                        return Response(serializer1.errors, status=status.HTTP_400_BAD_REQUEST)

                # Return a success response
                serializer3 = OpportunitySerializer(updated_opportunity) 
                return Response({"message": "Opportunity updated", "data": serializer3.data}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self, request, opportunity_id=None):
        if not opportunity_id:
            return Response({"error": "Opportunity ID required for delete"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
            opportunity.is_active = False
            opportunity.save()
            return Response({"message": "Opportunity deactivated"}, status=status.HTTP_204_NO_CONTENT)
        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
        
class StageHistory(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, opportunity_id=None):
        if opportunity_id:
            # Fetch stage history for a specific opportunity
            user=request.user
            if user.employee.designation.designation=='ADMIN':
                stage_history = Opportunity_Stage.objects.filter(opportunity_id=opportunity_id).order_by('-id')
           
            else:
                stage_history = Opportunity_Stage.objects.filter(opportunity_id=opportunity_id)
                stage_history &= Opportunity_Stage.objects.filter(Q(opportunity__created_by=user)|
                             Q(opportunity__lead__created_by=user)|Q(opportunity__lead__lead_owner=user)).order_by('-id')


            # contacts = Contact.objects.filter(Q(lead_id=lead_id)&
            #        ( Q(lead__lead_owner=user)|Q(lead__created_by=user)|Q(created_by=user)))
            # logs = Log.objects.filter(contact__in=contacts, is_active=True).order_by('-id')  

            if not stage_history.exists():
                return Response([])

            serializer = StageGetSerializer(stage_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # Fetch all stage histories
            stage_history = Opportunity_Stage.objects.all().order_by( '-id')
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(stage_history, request)
            
            return paginator.get_paginated_response(StageGetSerializer(result_page, many=True).data)



class Opportunity_Dropdown(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        dropdown_type = request.query_params.get("type")
        
        if dropdown_type == 'lead':
            leads = Lead.objects.all()
            serializer = LeadNameSerializer(leads, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif dropdown_type == 'stage':
            stages = Stage.objects.all()
            serializer = StageNameSerializer(stages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif dropdown_type == 'currency_type':
            currencies = Country.objects.all()
            serializer = CurrencySerializer(currencies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
     
        else:
            return Response("error : Invaild field", status=status.HTTP_200_OK)

from django.db.models import Sum, Count, Q

from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime, timedelta

class OpportunityChart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            filters = Q()

            # Extracting filter parameters from the request
            vertical = request.data.get('vertical')
            focus_segment = request.data.get('focus_segment')
            state = request.data.get('state')
            country = request.data.get('country')
            market_segment = request.data.get('market_segment')
            owner_id = request.data.get('owner')
            assigned_to_id = request.data.get('assigned_to')
           # lead_id = request.data.get('lead')

            # Adding filters based on the parameters received
            if vertical:
                filters &= Q(lead__focus_segment__vertical=vertical)
            if focus_segment:
                filters &= Q(lead__focus_segment=focus_segment)
            if state:
                filters &= Q(lead__state=state)
            if country:
                filters &= Q(currency_type_id=country)
            if market_segment:
                filters &= Q(lead__market_segment=market_segment)
            if owner_id:
                filters &= Q(owner_id=owner_id)

            if assigned_to_id:
                assigned_leads = Lead_Assignment.objects.filter(assigned_to_id=assigned_to_id)
                assigned_leads = assigned_leads.values_list('lead_id', flat=True)
                filters &= Q(lead__id__in=assigned_leads)
          #  if lead_id:
             #   filters &= Q(lead__id=lead_id)

            # Date filtering
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            #Set default date range if not provided: 1 year back from today to the end of last month
            
            if not start_date and not end_date:
                today = datetime.now()
                start_default = today.replace(year=today.year - 1, month=today.month+1, day=1)
                end_default = today.replace(day=today.day, month=today.month+1) - timedelta(days=1)
                print(start_default , end_default)
                filters &= Q(created_on__range=(start_default, end_default))
            else:
                if start_date:
                    filters &= Q(created_on__gte=datetime.fromisoformat(start_date))
                if end_date:
                    filters &= Q(created_on__lte=datetime.fromisoformat(end_date))
            
            # Retrieve stage IDs for filtering and aggregation
            closed_won_stage_id = Stage.objects.get(stage='Closed won').id
            closed_lost_stage_id = Stage.objects.get(stage='Closed lost').id
            Negotiation_and_commitment_stage_id = Stage.objects.get(stage='Negotiation and commitment').id
            Proposal_stage_id = Stage.objects.get(stage='Proposal').id
            Perception_analysis_stage_id = Stage.objects.get(stage='Perception analysis').id
            Decision_makers_stage_id = Stage.objects.get(stage='Decision makers').id
            Value_proposition_stage_id = Stage.objects.get(stage='Value proposition').id
            Needs_analysis_stage_id = Stage.objects.get(stage='Needs analysis').id
            Qualification_stage_id = Stage.objects.get(stage='Qualification').id
            Prospecting_stage_id = Stage.objects.get(stage='Prospecting').id


            # Filter opportunities based on the compiled filters
            employee = request.user.employee  # Assuming `Employee` is related to `User` via a OneToOneField

            # Role-based filtering
            if employee.designation.designation == 'ADMIN':
                # Admins can see all opportunities
                opportunities = Opportunity.objects.filter(filters)
            elif employee.designation.designation == 'BDM':
                leads_qs = Lead.objects.filter(lead_owner=request.user)
                opportunities = Opportunity.objects.filter(lead__in=leads_qs).filter(filters)
            else:
                # Other roles (DM, TM, BDE) see no opportunities
                opportunities = Opportunity.objects.none()
            
            # Aggregate values for each stage
            summary = opportunities.aggregate(
                total_opportunities=Count('id'),
                total_value=Sum('opportunity_value'),
                total_recurring_value=Sum('recurring_value_per_year'),
                won_count=Count('id', filter=Q(stage_id=closed_won_stage_id)),
                won_value=Sum('opportunity_value', filter=Q(stage_id=closed_won_stage_id)),
                won_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=closed_won_stage_id)),

                lost_count=Count('id', filter=Q(stage_id=closed_lost_stage_id)),
                lost_value=Sum('opportunity_value', filter=Q(stage_id=closed_lost_stage_id)),
                lost_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=closed_lost_stage_id)),

                Negotiation_and_commitment_count=Count('id', filter=Q(stage_id=Negotiation_and_commitment_stage_id)),
                Negotiation_and_commitment_value=Sum('opportunity_value', filter=Q(stage_id=Negotiation_and_commitment_stage_id)),
                Negotiation_and_commitment_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Negotiation_and_commitment_stage_id)),

                Proposal_count=Count('id', filter=Q(stage_id=Proposal_stage_id)),
                Proposal_value=Sum('opportunity_value', filter=Q(stage_id=Proposal_stage_id)),
                Proposal_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Proposal_stage_id)),

                Perception_analysis_count=Count('id', filter=Q(stage_id=Perception_analysis_stage_id)),
                Perception_analysis_value=Sum('opportunity_value', filter=Q(stage_id=Perception_analysis_stage_id)),
                Perception_analysis_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Perception_analysis_stage_id)),

                Decision_makers_count=Count('id', filter=Q(stage_id=Decision_makers_stage_id)),
                Decision_makers_value=Sum('opportunity_value', filter=Q(stage_id=Decision_makers_stage_id)),
                Decision_makers_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Decision_makers_stage_id)),

                Value_proposition_count=Count('id', filter=Q(stage_id=Value_proposition_stage_id)),
                Value_proposition_value=Sum('opportunity_value', filter=Q(stage_id=Value_proposition_stage_id)),
                Value_proposition_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Value_proposition_stage_id)),

                Needs_analysis_count=Count('id', filter=Q(stage_id=Needs_analysis_stage_id)),
                Needs_analysis_value=Sum('opportunity_value', filter=Q(stage_id=Needs_analysis_stage_id)),
                Needs_analysis_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Needs_analysis_stage_id)),

                Qualification_count=Count('id', filter=Q(stage_id=Qualification_stage_id)),
                Qualification_value=Sum('opportunity_value', filter=Q(stage_id=Qualification_stage_id)),
                Qualification_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Qualification_stage_id)),

                Prospecting_count=Count('id', filter=Q(stage_id=Prospecting_stage_id)),
                Prospecting_value=Sum('opportunity_value', filter=Q(stage_id=Prospecting_stage_id)),
                Prospecting_recurring_value=Sum('recurring_value_per_year', filter=Q(stage_id=Prospecting_stage_id))
            )
            # Parse the dates
            def parse_date(date_str):
                if date_str:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                return None

            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            # Determine the current date or the start date for the range
            current_date = start_date if start_date else datetime.now()

            # Initialize the months list
            months = []

            # If end_date is provided, calculate the months within the range
            if end_date:
                while current_date <= end_date:
                    months.append(current_date.strftime('%Y-%m'))
                    # Move to the next month
                    next_month = current_date.month % 12 + 1
                    next_year = current_date.year + (current_date.month // 12)
                    current_date = current_date.replace(year=next_year, month=next_month)
            else:
                # If no end_date, default to the last 12 months
                months = [(current_date - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(12)]

            # print("Months:", months)
            months.sort()
            monthly_counts = {month: 0 for month in months}

            # Query for monthly data over the last 12 months
            monthly_data = (
                opportunities
                .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on'))
                .values('year', 'month')
                .annotate(count=Count('id'))
                .order_by('year', 'month')
            )

            # Populate monthly_counts dictionary with actual data
            for entry in monthly_data:
                month_str = f"{entry['year']}-{str(entry['month']).zfill(2)}"
                monthly_counts[month_str] = entry['count']

            # Prepare response data
            monthly_data = [{"month": month, "count": count} for month, count in monthly_counts.items()]
            # Prepare response data
            response_data = {
                "total": {
                    "count": summary['total_opportunities'],
                    "value": summary['total_value'] or 0,
                    "recurring_value": summary['total_recurring_value'] or 0
                },
                "won": {
                    "count": summary['won_count'] or 0,
                    "value": summary['won_value'] or 0,
                    "recurring_value": summary['won_recurring_value'] or 0
                },
                "lost": {
                    "count": summary['lost_count'] or 0,
                    "value": summary['lost_value'] or 0,
                    "recurring_value": summary['lost_recurring_value'] or 0
                },
                "Negotiation_and_commitment": {
                    "count": summary['Negotiation_and_commitment_count'] or 0,
                    "value": summary['Negotiation_and_commitment_value'] or 0,
                    "recurring_value": summary['Negotiation_and_commitment_recurring_value'] or 0
                },
                "Proposal": {
                    "count": summary['Proposal_count'] or 0,
                    "value": summary['Proposal_value'] or 0,
                    "recurring_value": summary['Proposal_recurring_value'] or 0
                },
                "Perception_analysis": {
                    "count": summary['Perception_analysis_count'] or 0,
                    "value": summary['Perception_analysis_value'] or 0,
                    "recurring_value": summary['Perception_analysis_recurring_value'] or 0
                },
                "Decision_makers": {
                    "count": summary['Decision_makers_count'] or 0,
                    "value": summary['Decision_makers_value'] or 0,
                    "recurring_value": summary['Decision_makers_recurring_value'] or 0
                },
                "Value_proposition": {
                    "count": summary['Value_proposition_count'] or 0,
                    "value": summary['Value_proposition_value'] or 0,
                    "recurring_value": summary['Value_proposition_recurring_value'] or 0
                },
                "Needs_analysis": {
                    "count": summary['Needs_analysis_count'] or 0,
                    "value": summary['Needs_analysis_value'] or 0,
                    "recurring_value": summary['Needs_analysis_recurring_value'] or 0
                },
                "Qualification": {
                    "count": summary['Qualification_count'] or 0,
                    "value": summary['Qualification_value'] or 0,
                    "recurring_value": summary['Qualification_recurring_value'] or 0
                },
                "Prospecting": {
                    "count": summary['Prospecting_count'] or 0,
                    "value": summary['Prospecting_value'] or 0,
                    "recurring_value": summary['Prospecting_recurring_value'] or 0
                },

                "monthly_data": monthly_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------SANJESH-------------
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

class ContactPagination(PageNumberPagination):
    page_size = 10  # Number of contacts per page
    page_size_query_param = 'page_size'  # Allow client to set page size using URL parameter
    max_page_size = 100  # Maximum limit of page size that can be requested

class ContactView(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class = ContactPagination

    def post(self, request):
        serializer = PostContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, contact_id=None):
        if contact_id:  # Retrieve a specific contact by 'contact_id'
            try:
                contact = Contact.objects.get(id=contact_id)
                serializer = ContactSerializer(contact)
                return Response(serializer.data)
            except Contact.DoesNotExist:
                return Response([])  # Return an empty list if no contact is found
        else:
            contacts = Contact.objects.all()  # Retrieve all contacts if no 'contact_id' is provided
            paginator = self.pagination_class()
            paginated_contacts = paginator.paginate_queryset(contacts, request)
            serializer = ContactSerializer(paginated_contacts, many=True)
            return paginator.get_paginated_response(serializer.data)

    def put(self, request, contact_id=None):
        contact = get_object_or_404(Contact, id=contact_id)
        serializer = ContactSerializer(contact, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id)
        contact.is_active = False
        contact.save()
        return Response({"message": "Contact deactivated successfully."}, status=status.HTTP_200_OK)
    
class LeadContactsPagination(PageNumberPagination):
    page_size = 10  # Number of contacts per page
    page_size_query_param = 'page_size'  # Allow client to set page size using URL parameter
    max_page_size = 100  # Maximum limit of page size that can be requested

class LeadContactsView(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class = LeadContactsPagination

    def get(self, request, lead_id=None):
        if lead_id: 
            user=request.user # Retrieve contacts for a specific lead
            if user.employee.designation.designation=='ADMIN':
                contacts=Contact.objects.filter(lead__id=lead_id,is_active=True).order_by('-id')

            else:
                contacts = Contact.objects.filter(Q(lead__id=lead_id),
                    Q(lead__lead_owner=user)|Q(lead__created_by=user)|Q(created_by=user))
            paginator = self.pagination_class()
            paginated_contacts = paginator.paginate_queryset(contacts, request)
            serializer = ContactSerializer(paginated_contacts, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({"detail": "Lead ID is required."}, status=status.HTTP_400_BAD_REQUEST)

# CountView 
class CountView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return self.get_counts(request)

    def get_counts(self, request):
        try:
            # Load the request body data
            body = request.data

            # Extract filter data from the request body
            owner = body.get('owner')
            vertical = body.get('vertical')
            focus_segment = body.get('focus_segment')
            market_segment = body.get('market_segment')
            country = body.get('country')
            state = body.get('state')
            start_date = body.get('start_date')  # Expected format: 'YYYY-MM-DD'
            end_date = body.get('end_date')
            assigned_to=body.get('assigned_to')      # Expected format: 'YYYY-MM-DD'

            employee = request.user.employee  # Assuming `Employee` is related to `User` via a one-to-one relation

        # Check if the logged-in user's designation is ADMIN or BDM
            if employee.designation.designation == 'ADMIN':  # Check if user is admin
                # Admins can see all leads and opportunities
                leads_qs = Lead.objects.all()
                opportunities_qs = Opportunity.objects.all()
                Negotiation_and_commitment_qs = Opportunity.objects.filter(stage__stage='Negotiation and commitment')
                won_qs = Opportunity.objects.filter(stage__stage='Closed-won')
            elif employee.designation.designation == 'BDM':  # Check if user is a manager (BDM)
                # Managers (BDM) can see only leads they own and their associated opportunities
                leads_qs = Lead.objects.filter(lead_owner=request.user)
                opportunities_qs = Opportunity.objects.filter(lead__in=leads_qs)
                Negotiation_and_commitment_qs = Opportunity.objects.filter(lead__in=leads_qs, stage__stage='Negotiation and commitment')
                won_qs = Opportunity.objects.filter(lead__in=leads_qs, stage__stage='Closed-won')
            else:
                # For other users (DM, TM, BDE), show no data
                leads_qs = Lead.objects.none()  # No leads for other roles
                opportunities_qs = Opportunity.objects.none()  # No opportunities for other roles
                Negotiation_and_commitment_qs = Opportunity.objects.none()
                won_qs = Opportunity.objects.none()


            # Apply filters based on request data to all querysets
            if owner:
                leads_qs = leads_qs.filter(lead_owner=owner)
                opportunities_qs = opportunities_qs.filter(owner=owner)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(owner=owner)
                won_qs = won_qs.filter(owner=owner)

            if vertical:
                leads_qs = leads_qs.filter(focus_segment__vertical=vertical)
                opportunities_qs = opportunities_qs.filter(lead__focus_segment__vertical=vertical)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(lead__focus_segment__vertical=vertical)
                won_qs = won_qs.filter(lead__focus_segment__vertical=vertical)

            if focus_segment:
                leads_qs = leads_qs.filter(focus_segment=focus_segment)
                opportunities_qs = opportunities_qs.filter(lead__focus_segment=focus_segment)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(lead__focus_segment=focus_segment)
                won_qs = won_qs.filter(lead__focus_segment=focus_segment)

            if market_segment:
                leads_qs = leads_qs.filter(market_segment=market_segment)
                opportunities_qs = opportunities_qs.filter(lead__market_segment=market_segment)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(lead__market_segment=market_segment)
                won_qs = won_qs.filter(lead__market_segment=market_segment)

            if country:
                leads_qs = leads_qs.filter(country=country)
                opportunities_qs = opportunities_qs.filter(lead__country=country)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(lead__country=country)
                won_qs = won_qs.filter(lead__country=country)

            if state:
                leads_qs = leads_qs.filter(state=state)
                opportunities_qs = opportunities_qs.filter(lead__state=state)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(lead__state=state)
                won_qs = won_qs.filter(lead__state=state)

            # Apply date range filters
            if start_date:
                start_date_parsed = parse_date(start_date)
                leads_qs = leads_qs.filter(created_on__gte=start_date_parsed)
                opportunities_qs = opportunities_qs.filter(created_on__gte=start_date_parsed)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(created_on__gte=start_date_parsed)
                won_qs = won_qs.filter(created_on__gte=start_date_parsed)

            if end_date:
                end_date_parsed = parse_date(end_date)
                leads_qs = leads_qs.filter(created_on__lte=end_date_parsed)
                opportunities_qs = opportunities_qs.filter(created_on__lte=end_date_parsed)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(created_on__lte=end_date_parsed)
                won_qs = won_qs.filter(created_on__lte=end_date_parsed)

            if assigned_to:
                # Get all the lead IDs assigned to the specified user
                lead_ids = Lead_Assignment.objects.filter(assigned_to_id=assigned_to)
                lead_ids = lead_ids.values_list('lead_id', flat=True)
                # Apply the filtered lead IDs to all relevant querysets
                leads_qs = leads_qs.filter(id__in=lead_ids)
                opportunities_qs = opportunities_qs.filter(lead__id__in=lead_ids)
                Negotiation_and_commitment_qs = Negotiation_and_commitment_qs.filter(lead__id__in=lead_ids)
                won_qs = won_qs.filter(lead__id__in=lead_ids)
            

            # Calculate the counts after applying filters
            leads_count = leads_qs.count()
            opportunities_count = opportunities_qs.count()
            Negotiation_and_commitment_count = Negotiation_and_commitment_qs.count()
            won_count = won_qs.count()

            # Prepare the response data
            response_data = {
                'leads_count': leads_count,
                'opportunities_count': opportunities_count,
                'Negotiation_and_commitment_count': Negotiation_and_commitment_count,
                'won_count': won_count,
            }

            # Return the count data
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any errors and return a 500 error response
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class Contactdropdownlistview(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        dropdown_type = request.query_params.get('type')

        if dropdown_type == 'contactstatus':
            contact_status = Contact_Status.objects.all()
            serializer = ContactStatusSerializer(contact_status, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif dropdown_type == 'lead_source':
            source = Lead_Source.objects.all()
            serializer = LeadSourceSerializer(source, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif dropdown_type=='lead':
            leads = Lead.objects.all()
            serializer=LeadSerializer(leads,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


        return Response({'error': 'Invalid dropdown type'}, status=status.HTTP_400_BAD_REQUEST)

# OpportunityFilterView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Opportunity  # Assuming you have the Opportunity model

class OpportunityFilterView(APIView):
    permission_classes=[IsAuthenticated]
    class OpportunityPagination(PageNumberPagination):
        page_size = 10  # Default page size
        page_size_query_param = 'page_size'
        max_page_size = 1000  # Max limit for page size

    def post(self, request, *args, **kwargs):
        return self.filter_and_paginate(request)

    def get(self, request, *args, **kwargs):
        return self.filter_and_paginate(request)

    def filter_and_paginate(self, request):
        try:
            # Load the body as JSON
            body = request.data if request.method == 'POST' else request.query_params

            # Start by querying all opportunities
            user = request.user
            if user.employee.designation.designation=='ADMIN':
                opportunities=Opportunity.objects.filter(is_active=True)
            else:
                opportunities = Opportunity.objects.filter(
                    Q(created_by=user) |    Q(owner=user)        |         
                    Q(lead__lead_owner=user) |                
                    Q(lead__created_by=user)                 
                ).distinct().order_by('-created_on', '-id')     

            # Filter by vertical IDs through the Lead and Focus_Segment relationships
            focus_segment_ids = body.get('vertical', [])
            if focus_segment_ids:
                opportunities = opportunities.filter(lead__focus_segment__id__in=focus_segment_ids)
            lead_ids = body.get('lead_id', [])
            if lead_ids:
                opportunities = opportunities.filter(lead__id__in=lead_ids)

            owner_ids = body.get('owner_id', [])
            if owner_ids:
                opportunities = opportunities.filter(owner__id__in=owner_ids)

            stage_ids = body.get('stage_id', [])
            if stage_ids:
                opportunities = opportunities.filter(stage__id__in=stage_ids)

            currency_ids = body.get('currency_type', [])
            if currency_ids:
                opportunities = opportunities.filter(currency_type__id__in=currency_ids)

            start_date = body.get('start_date')
            end_date = body.get('end_date')

            # Ensure both dates are provided
            if start_date and end_date:
                
                opportunities = opportunities.filter(closing_date__range=[start_date, end_date])

            opportunity_value_range = body.get('opportunity_value', [])
            
            if len(opportunity_value_range) == 2:
                min_value, max_value = opportunity_value_range
                opportunities = opportunities.filter(opportunity_value__gte=min_value, opportunity_value__lte=max_value)

            search_key = body.get('key', None)
            if search_key:
                opportunities = opportunities.filter(
                    Q(name__icontains=search_key) |
                    Q(owner__username__icontains=search_key) |
                    Q(stage__stage__icontains=search_key) |
                    Q(note__icontains=search_key) |
                    Q(currency_type__currency_full__icontains=search_key) |
                    Q(created_by__username__icontains=search_key) |
                    Q(lead__name__icontains=search_key)
                ).distinct()


            # Additional filters based on other fields can go here, e.g., owner, stage, created_on, etc.

            # Handle pagination
            paginator = self.OpportunityPagination()
            opportunities_page = paginator.paginate_queryset(opportunities, request)

            # Prepare the response data
            opportunity_data = [
                {
                    "id": opportunity.id,
                    "name": opportunity.name,
                    "owner": {
                        "id": opportunity.owner.id,
                        "username": opportunity.owner.username,
                    },
                    "lead": {
                        "id": opportunity.lead.id if opportunity.lead else None,
                        "name": opportunity.lead.name if opportunity.lead else None,
                    },
                    "stage": {
                        "id": opportunity.stage.id,
                        "stage": opportunity.stage.stage
                    },
                    "opportunity_value": opportunity.opportunity_value,
                    "recurring_value_per_year":opportunity.recurring_value_per_year,
                    "currency_type": {
                        "id": opportunity.currency_type.id,
                        "currency_short": opportunity.currency_type.currency_short,
                    },
                    "closing_date": opportunity.closing_date,
                    "probability_in_percentage": opportunity.probability_in_percentage,
                    "created_on": opportunity.created_on,
                    # Add other fields as necessary
                }
                for opportunity in opportunities_page
            ]

            # Return the filtered and paginated opportunity data with pagination links
            return paginator.get_paginated_response(opportunity_data)

        except Exception as e:
            # Return error response in case of an issue
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ***********Afsal******
    
from django.http import JsonResponse
import json
from .models import Log_Stage, Log, Task, Lead_Assignment, Notification
from django.contrib.auth.models import User
from .serializers.logserializer import LogCreateUpdateSerializer, LogReadSerializer
from .serializers.taskserializer import TaskSerializer
from .serializers.employeeserializer import EmployeeSerializer
from .serializers.logstageserializer import LogStageSerializer
from django.utils.dateparse import parse_date


# Pagination
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Employee List View
class EmployeeListView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, id=None):
        if id:
            try:
                user =User.objects.get(id=id)
                serializer = EmployeeSerializer(user)
                return JsonResponse(serializer.data, status=200)
            except User.DoesNotExist:
                return JsonResponse({"message" : "Employee not found"}, status=404)

        search_query = request.data.get('search', '').strip()

        # Filter employees based on the search query if provided
        if search_query:
            employees = User.objects.filter(Q(first_name__istartswith=search_query) | Q(last_name__istartswith=search_query))
        else:
            employees = User.objects.all()
        
        employees = employees.order_by('first_name')

        # Paginate the results
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(employees, request)
        serializer = EmployeeSerializer(result_page, many=True)

        # Return paginated and serialized data
        return paginator.get_paginated_response(serializer.data)
    
# Lead Assignment View
class LeadAssignmentView(APIView):
    def post(self, request, lead_id):
        user = request.user
        assigned_by_user = user

        # Try to get the lead and its owner
        try:
            lead = Lead.objects.get(id=lead_id)
            lead_owner = lead.lead_owner
        except Lead.DoesNotExist:
            return JsonResponse({"message": "Lead not found"}, status=404)
        
        # Parse request data to get the list of assigned users
        data = json.loads(request.body)
        assigned_to_ids = data.get('assigned_to')  # Expecting a list of user IDs

        if not assigned_to_ids:
            return JsonResponse({"message": "No employees selected"}, status=400)

        # Iterate through selected users and create Lead_Assignment records
        for user_id in assigned_to_ids:
            try:
                assigned_user = User.objects.get(id=user_id)
                Lead_Assignment.objects.create(
                    lead=lead, 
                    assigned_to=assigned_user, 
                    assigned_by=assigned_by_user
                )

                # Create a notification for the assigned user
                message = f"A new Lead '{lead.name}' has been assigned to you by {assigned_by_user.username}."
                Notification.objects.create(
                    receiver=assigned_user,
                    message=message
                )

                # Create a notification for the lead owner
                message1 = f"The Lead '{lead.name}' has been assigned to '{assigned_user.username}'."
                Notification.objects.create(
                    receiver=lead_owner,
                    message=message1
                )

                # Send email to the assigned user
                subject_assigned_user = "New Lead Assignment"
                message_assigned_user = (
                    f"Hello {assigned_user.username},\n\n"
                    f"You have been assigned a new lead '{lead.name}' by {assigned_by_user.username}.\n"
                    "Please log in to the CRM system to view more details and take further action:\n"
                    "http://crm.decodeschool.com/\n\n"
                    
                )
                send_mail(
                    subject_assigned_user,
                    message_assigned_user,
                    settings.DEFAULT_FROM_EMAIL,
                    [assigned_user.email],
                    fail_silently=False,
                )

               
            except User.DoesNotExist:
                return JsonResponse({"message": f"User {user_id} not found"}, status=404)

        return JsonResponse({"message": "Lead assigned successfully"}, status=201)
    
# Call the function to get contact detail
class ContactDetailView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)  # Fetch the contact by ID
            serializer = ContactSerializer(contact)
            return JsonResponse(serializer.data, status=200)
        except Contact.DoesNotExist:
            return JsonResponse({"message": "Contact not found"}, status=404)

# Creating, Editing, Deleting Log and Task
class LogManagement(APIView):
    permission_classes=[IsAuthenticated]
     # API for retrieving a specific Log
    def get(self, request, id):
        try:
            log = Log.objects.get(id=id)
            serializer = LogReadSerializer(log)
            return JsonResponse(serializer.data, status = 200)
        except Log.DoesNotExist:
            return JsonResponse({"message" : "Log not found"}, status =404)
    
    # Create Log and Task
    def post(self, request, id):
        try:
            contact = Contact.objects.get(id=id)
            lead = contact.lead  # Get the related lead to retrieve focus_segment
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'Contact not found'}, status=404)

        
        data = request.data
        
        log_stage_id = data.get('log_stage')
        try:
            log_stage = Log_Stage.objects.get(id=log_stage_id)
        except Log_Stage.DoesNotExist:
            return JsonResponse({'message': 'Log stage not found'}, status=404)

        # Hardcoded user for testing purposes
        created_by_user = request.user

        log_data = {
            'contact': contact.id,
            'focus_segment': lead.focus_segment.id,
            'follow_up_date_time': data.get('follow_up_date_time'),
            'log_stage': log_stage.id,
            'details': data.get('details'),
            'file': request.FILES.get('file'),
            'created_by': created_by_user.id,
        }
        log_serializer = LogCreateUpdateSerializer(data=log_data)
        if log_serializer.is_valid():
            log = log_serializer.save()  # Save the log

            if log.follow_up_date_time:
                task_data = {
                    'contact': contact.id,
                    'log': log.id,
                    'task_date_time': log.follow_up_date_time,
                    'task_detail': log.details,
                    'created_by': created_by_user.id,
                    'is_active': True,
                    'tasktype': 'A',
                }
                task_serializer = TaskSerializer(data=task_data)
                if task_serializer.is_valid():
                    task_serializer.save()
                    return JsonResponse({'message': 'Log and Task created successfully'}, status=201)
                else:
                    log.delete()  # Rollback log creation if task fails
                    return JsonResponse(task_serializer.errors, status=400)
            else:
                return JsonResponse({'message': 'Log created successfully'}, status=201)

        return JsonResponse(log_serializer.errors, status=400)

    # Edit Log and Task
    def put(self, request, id):
        try:
            log = Log.objects.get(id=id)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log not found'}, status=404)

        data = request.data
        log_serializer = LogCreateUpdateSerializer(log, data=data, partial=True)

        if log_serializer.is_valid():
            log = log_serializer.save()

            follow_up_date_time = data.get('follow_up_date_time')
            if follow_up_date_time:
                try:
                    task = Task.objects.get(log=log, tasktype = "A")
                except Task.DoesNotExist:
                    task_data = {
                        'contact': log.contact.id,
                        'log': log.id,
                        'task_date_time': follow_up_date_time,
                        'task_detail': log.details,
                        'created_by': log.created_by.id,
                        'is_active': True,
                        'tasktype': 'A',
                    }
                    task_serializer = TaskSerializer(data=task_data)
                    if task_serializer.is_valid():
                        task_serializer.save()
                        return JsonResponse({'message': 'Log updated and new Task created successfully'}, status=200)
                    else:
                        return JsonResponse(task_serializer.errors, status=400)

                task_data = {
                    'task_date_time': follow_up_date_time,
                    'task_detail': log.details,
                }
                task_serializer = TaskSerializer(task, data=task_data, partial=True)
                if task_serializer.is_valid():
                    task_serializer.save()
                    return JsonResponse({'message': 'Log and Task updated successfully'}, status=200)
                return JsonResponse(task_serializer.errors, status=400)

            # If no follow_up_date_time, only update the task detail if the task exists
            try:
                task = Task.objects.get(log=log, tasktype = "A")
                task_data = {
                    'task_detail': log.details
                }
                task_serializer = TaskSerializer(task, data=task_data, partial=True)
                if task_serializer.is_valid():
                    task_serializer.save()
                return JsonResponse({'message': 'Log updated successfully,  task changes'}, status=200)
            except Task.DoesNotExist:
                return JsonResponse({'message': 'Log updated, no task changes'}, status=200)

        return JsonResponse(log_serializer.errors, status=400)

    # Delete Log and Task
    def delete(self, request, id):
        try:
            log = Log.objects.get(id=id)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log not found'}, status=404)

        log.is_active = False
        log.save()

        try:
            task = Task.objects.get(log =log )
            task.is_active = False
            task.save()
        except Task.DoesNotExist:
            return JsonResponse({'message': 'Task not found'}, status=404)

        return JsonResponse({'message': 'Log and Task deleted successfully'}, status=200)

# Calling log_status for creating Log
class LogStageListView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
            log_stages = Log_Stage.objects.filter(is_active=True)  
            serializer = LogStageSerializer(log_stages, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)
        
#Calling all the logs in a Lead
class logsbyLeadsView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, lead_id):
        user=request.user
        try:
            if user.employee.designation.designation=='ADMIN':
                contacts= Contact.objects.filter(lead_id=lead_id)
            else:
                contacts = Contact.objects.filter(Q(lead_id=lead_id)&
                    ( Q(lead__lead_owner=user)|Q(lead__created_by=user)|Q(created_by=user)))
            logs = Log.objects.filter(contact__in=contacts, is_active=True).order_by('-id')  
            
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(logs, request)
            log_serializer = LogReadSerializer(result_page, many=True)

            return paginator.get_paginated_response(log_serializer.data)
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'No contacts found for this lead'}, status=404)
        
#calling all the logs of a Contact
class logsbyContactView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, contact_id):
        try:
            user=request.user
            if user.employee.designation.designation=='ADMIN':
                logs= Log.objects.filter(contact_id=contact_id,is_active=True).order_by('-id')
            else:
                logs = Log.objects.filter(Q(contact_id=contact_id)&(Q(contact__lead__lead_owner=user)|
                Q(contact__lead__created_by=user)| Q(contact__created_by=user)| Q(created_by=user))).order_by('-id')  
            
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(logs, request)
            log_serializer = LogReadSerializer(result_page, many=True)

            return paginator.get_paginated_response(log_serializer.data)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log does not exist'}, status=404)

# Opportunity Report
class OpportunityReportView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        # Get filter parameters from request
        vertical = request.data.get('vertical')
        focus_segment = request.data.get('focus_segment')
        state = request.data.get('state')
        country = request.data.get('country')
        market_segment = request.data.get('market_segment')
        lead = request.data.get('lead')

        # Filter the opportunities
        opportunities = Opportunity.objects.filter(is_active=True)
        
        if vertical:
            opportunities = opportunities.filter(lead__focus_segment__vertical=vertical)
        if focus_segment:
            opportunities = opportunities.filter(lead__focus_segment=focus_segment)
        if state:
            opportunities = opportunities.filter(lead__state=state)
        if country:
            opportunities = opportunities.filter(currency_type_id=country)
        if market_segment:
            opportunities = opportunities.filter(lead__market_segment=market_segment)
        if lead:
            opportunities = opportunities.filter(lead__id=lead)
        
        # Aggregation for count, total value, recurring value
        data = opportunities.aggregate(
            count=Count('id'),
            total_value=Sum('opportunity_value'),
            recurring_value=Sum('recurring_value_per_year')
        )

        return Response(data)

# Task Assignment
class TaskAssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        # Attempt to retrieve the task
        try:
            task = Task.objects.get(id=id)
        except Task.DoesNotExist:
            return JsonResponse({'message': 'Task does not exist'}, status=404)
        
        assigned_to = request.data.get('assigned_to')
        if not assigned_to:
            return JsonResponse({'message': 'No employee selected'}, status=400)
        
        try:
            # Retrieve the user to whom the task is being assigned
            user = User.objects.get(id=assigned_to)
            Task_Assignment.objects.create(
                task=task, 
                assigned_to=user, 
                assigned_by=request.user,  # Using the authenticated user as assigned_by
                
            )
            
            # Email details
            subject = "New Task Assignment"
            message = (
                f"Hello {user.username},\n\n"
                "You have been assigned a new task:\n\n"
                "Please log in to the CRM system to view more details:\n"
                "http://crm.decodeschool.com/\n\n"
                
            )
            
            # Send email to the assigned user
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return JsonResponse({"message": "Task assigned successfully"}, status=201)
        
        except User.DoesNotExist:
            return JsonResponse({'message': f'User {assigned_to} does not exist'}, status=404)
        
#API for all the tasks under a Contact with search with task name and date
class TaskListVIew(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, id):
        try:
            user = request.user

            # Retrieve search parameters from request body
            search_query = request.data.get('task_name', '').strip()
            task_date_str = request.data.get('task_date_time', '').strip()
            task_date = parse_date(task_date_str) if task_date_str else None

            # Build base filter conditions
            filter_conditions = Q()
            if search_query:
                filter_conditions &= Q(task_detail__icontains=search_query)
            if task_date:
                filter_conditions &= Q(task_date_time__date=task_date)

            # Tasks associated with leads owned by the user
            leads_owned_by_user = Lead.objects.filter(lead_owner=user)
            tasks_related_to_leads = Task.objects.filter(contact__lead__in=leads_owned_by_user).filter(filter_conditions)

            # Tasks directly associated with the user
            tasks_created_by_user = Task.objects.filter(created_by=user).filter(filter_conditions)
            tasks_assigned_to_user_ids = Task_Assignment.objects.filter(assigned_to=user).values_list('task', flat=True)
            tasks_assigned_to_user = Task.objects.filter(id__in=tasks_assigned_to_user_ids).filter(filter_conditions)

            # Get tasks from today onwards
            today = now().date()

            # Combine all tasks with categories in a single list
            categorized_tasks = []

            # Add "Owned Task" category if user created the task
            for task in tasks_created_by_user:
                if task.task_date_time.date() >= today:
                    categorized_tasks.append({**GetTaskSerializer(task).data, "category": "Owned Task"})

            # Add "Assigned Task" category if user is assigned the task
            for task in tasks_assigned_to_user:
                if task.task_date_time.date() >= today and task not in tasks_created_by_user:
                    categorized_tasks.append({**GetTaskSerializer(task).data, "category": "Assigned Task"})

            # Add "Others Task" category for other tasks related to leads owned by the user
            for task in tasks_related_to_leads:
                if task.task_date_time.date() >= today and task not in tasks_created_by_user and task not in tasks_assigned_to_user:
                    categorized_tasks.append({**GetTaskSerializer(task).data, "category": "Others Task"})
            
            categorized_tasks.sort(key=lambda x: x['id'], reverse=True)
            #categorized_tasks.order_by('-id')
            # Apply pagination
            paginator = CustomPagination()
            paginated_tasks = paginator.paginate_queryset(categorized_tasks, request)
            return paginator.get_paginated_response(paginated_tasks)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






# API for retrieving a specific note
class NoteDetailView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, note_id):
        try:
            note = Note.objects.get(id = note_id)
            serializer = NoteSerializer(note)
            return JsonResponse(serializer.data, status = 200)
        except Note.DoesNotExist:
            return JsonResponse({"message" : "Note nor found"}, status = 404)
        

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Allow custom page size

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'prev': self.get_previous_link(),
            'next': self.get_next_link(),
            'results': data
        })
        
class TaskListView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            # Retrieve search parameters from request body
            search_key = request.data.get('key', '').strip()
            from_date_str = request.data.get('start_date', '').strip()
            to_date_str = request.data.get('end_date', '').strip()
            lead_id = request.data.get('lead')
            assigned_to_id = request.data.get('assigned_to')
           
            # Parse dates if provided
            from_date = parse_date(from_date_str) if from_date_str else None
            to_date = parse_date(to_date_str) if to_date_str else None

            # Build base filter conditions
            filter_conditions = Q(is_active=True)
            if search_key:
                filter_conditions &= Q(task_detail__icontains=search_key) | Q(contact__name__icontains=search_key)
            if from_date and to_date:
                filter_conditions &= Q(task_date_time__date__range=(from_date, to_date))
            elif from_date:
                filter_conditions &= Q(task_date_time__date__gte=from_date)
            elif to_date:
                filter_conditions &= Q(task_date_time__date__lte=to_date)
            if lead_id:
                filter_conditions &= Q(contact__lead_id=lead_id)
            if assigned_to_id:
                assigned_user = User.objects.filter(id=assigned_to_id).first()
                if not assigned_user:
                    return Response({'error': 'Assigned user not found'}, status=status.HTTP_404_NOT_FOUND)
                assigned_task_ids = Task_Assignment.objects.filter(assigned_to=assigned_user).values_list('task', flat=True)
                filter_conditions &= Q(id__in=assigned_task_ids)

            user = request.user

            leads_owned_by_user = Lead.objects.filter(lead_owner=user)
            tasks_related_to_leads = Task.objects.filter(contact__lead__in=leads_owned_by_user).filter(filter_conditions)
            tasks_created_by_user = Task.objects.filter(created_by=user).filter(filter_conditions)
            tasks_assigned_to_user_ids = Task_Assignment.objects.filter(assigned_to=user).values_list('task', flat=True)
            tasks_assigned_to_user = Task.objects.filter(id__in=tasks_assigned_to_user_ids).filter(filter_conditions)
            today = now().date()
            categorized_tasks=[]
            if user.employee.designation.designation == 'ADMIN':
                # If the user is an ADMIN, show all tasks, not limited to the user's assignments
                tasks = Task.objects.filter(is_active=True).filter(filter_conditions).order_by('-id')
                categorized_tasks = [
                    {**GetTaskSerializer(task).data, "category": "All Tasks"}
                    for task in tasks if task.task_date_time.date() >= today
                ]
            else:
                
                owned_tasks = [
                    {**GetTaskSerializer(task).data, "category": "Owned Task"}
                    for task in tasks_created_by_user if task.task_date_time.date() >= today
                ]
                

                # 2. Categorize tasks as "Assigned Task"
                assigned_tasks = [
                    {**GetTaskSerializer(task).data, "category": "Assigned Task"}
                    for task in tasks_assigned_to_user if task.task_date_time.date() >= today
                ]

                # Combine owned and assigned tasks
                categorized_tasks.extend(owned_tasks)
                categorized_tasks.extend(assigned_tasks)

                owned_task_ids = {task['id'] for task in owned_tasks}
                assigned_task_ids = {task['id'] for task in assigned_tasks}
                # 3. Categorize tasks as "Others Task"
                # We will only add tasks that are not already categorized as owned or assigned
                others_tasks = [
                    {**GetTaskSerializer(task).data, "category": "Others Task"}
                    for task in tasks_related_to_leads if task.task_date_time.date() >= today
                    and task.id not in owned_task_ids and task.id not in assigned_task_ids  # Exclude tasks by ID
    ]
                categorized_tasks.extend(others_tasks)



            categorized_tasks.sort(key=lambda x: x['id'], reverse=True)
            paginator = CustomPagination()
            paginated_tasks = paginator.paginate_queryset(categorized_tasks, request)
            return paginator.get_paginated_response(paginated_tasks)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class StageandProbability(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, id):
        try:
            stage = Stage.objects.get(id=id)
            data = {
                "stage_name": stage.stage,  
                "probability": stage.probability 
            }
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Stage.DoesNotExist:
            return Response({'error': 'Stage not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

from .models import Department,Designation
from .serializers.employeeserializer import DepartmentSerializer, DesignationSerializer
class GetAllDepartment(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        try:
            department = Department.objects.all()
            serializer=DepartmentSerializer(department,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetAllDesignation(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        try:
            designation = Designation.objects.all()
            serializer = DesignationSerializer(designation,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)