from django.urls import path, include
from .routers import router
from .views import *

urlpatterns = [

    #LEAD LIST
    #-by_SABARIGIRIVASAN
    
    # path('focus_segments/<int:vertical_id>/', FocusSegmentListByVertical.as_view(), name='focus-segments-by-vertical'),
    # path('leaddetails/', LeadView.as_view(),name='lead_details'),              
    # path('leaddetails/<int:lead_id>/', LeadView.as_view(),name='lead_details_by_id'),
    path('dropdown/', DropdownListView.as_view(),name='drop_down'),                   
    path('dropdown/state/<int:country_id>/', DropdownListView.as_view(),name='state_drop_down'),
    

    #-by_SANKARMAHARAJAN
    path('filter_lead/', LeadFilterView.as_view(), name='lead-filter'),
    path('report_lead/',ReportView.as_view(),name='report_leads'),
    path('opportunity/<int:opportunity_id>/notes/', OpportunityNotesView.as_view(), name='opportunity-notes'),
    path('opportunity/add_note/', OpportunityNotesView.as_view(), name = "AddOpportunityNotesView"),
    path('notes/<int:lead_id>', GetNotesByLeadView.as_view(), name="GetNotesByLeadView"),
    path('notes/<int:note_id>/', OpportunityNotesView.as_view(), name='update-opportunity-note'),
    path('stage/<int:id>/',StageandProbability.as_view(), name = 'StageandProbability'),
    path('department/',GetAllDepartment.as_view(), name = 'GetAllDepartment'),
    path('designation/',GetAllDesignation.as_view(), name = 'GetAllDesignation'),

    # *******Sanjesh*******
    path('contactdetails/', ContactView.as_view(),name='contact_details'), # For creating and listing all contacts
    path('contactdetails/<int:contact_id>/', ContactView.as_view(),name='contact_details_by_id'),
    path('contactbylead/<int:lead_id>/', LeadContactsView.as_view(), name='lead-contacts'),
    path('opportunities/', OpportunityFilterView.as_view(), name='opportunity-filter'),
    path('contactdropdown/',Contactdropdownlistview.as_view(),name='drop_down'),
    path('countdetails/', CountView.as_view(), name='lead_opportunity_stage_counts'),

    # ********Afsal********
    path('employees/', EmployeeListView.as_view(), name = "employees"), # Employee dropdown API
    path("employees/<int:id>/", EmployeeListView.as_view(), name = "employees-individual"), # Employee detail x dropdown API
    path('lead/<int:lead_id>/assign/', LeadAssignmentView.as_view(), name = "lead-assignment"),  # Lead assignment API
    path('contact/<int:contact_id>/', ContactDetailView.as_view(), name = "contact-details"),  # API for retrieving a specific 
    # path('log/<int:id>/', LogManagement.as_view(), name='LogManagement'), # API for Creating, Retrieving, Editing, Deleting Log and Task
    path('log_stages/', LogStageListView.as_view(), name='log-stage-list'),  # Log Stages Dropdown API
    path('leadlog/<int:lead_id>/', logsbyLeadsView.as_view(), name='log-stage-list'),  # API for all the Logs under a Lead
    path('contactlog/<int:contact_id>/', logsbyContactView.as_view(), name='log-stage-list'),  # API for all the Logs under a Contact
    path('opportunityreport/', OpportunityReportView.as_view(), name="opportunity-report"), # API for opportunity report
    path('task/<int:id>/assign/', TaskAssignmentView.as_view(), name="task-assignment"),  # API for Task Assignment
    path('gettask/<int:id>/', TaskListVIew.as_view(), name='task'),  # API for all the tasks under a Contact with search with task name and date
    path('note/<int:note_id>/', NoteDetailView.as_view(), name = "note-details"), 
    path('alltask/',TaskListView.as_view(),name="task_view"), # API for retrieving a specific note

 #-----------Sumith---------------
    path('create-task/', CreateTaskView.as_view(), name='create-task'),
    path('task/<int:id>/', TaskManagement.as_view(), name='task'),
    path('report_stage/', OpportunityReportView.as_view(), name='report_stage'),
    path('opportunity/chart/', OpportunityChart.as_view(), name="opportunity-chart"),


#---------vs-------------
    path('opportunity/',Opportunity_details.as_view(), name="Opportunity_create"),
    path('opportunity/<int:opportunity_id>/',Opportunity_details.as_view(), name="Opportunity-details"),
    path('opportunity/lead_id/<int:lead_id>/',Opportunity_ByLeadId.as_view(),name="opportunity_ByLead_Id"),
    path('opportunity/drop-down/',Opportunity_Dropdown.as_view(),name="opportunity_dropdown"),
    path('opportunity/stage_history/', StageHistory.as_view(), name='stage-history'),
    path('opportunity/stage_history/<int:opportunity_id>/', StageHistory.as_view(), name='stage-history'),

# ------------------------mitun-----------------------------
    # path('users_for_lead/', UsersForLead.as_view(), name='users_for_lead'),
    # path('get_lead_owners/', GetLeadOwner.as_view(), name='get_lead_owners'),
    
    
    
]