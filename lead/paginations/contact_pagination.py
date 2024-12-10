from rest_framework.pagination import PageNumberPagination

class ContactPagination(PageNumberPagination):
    page_size = 10  # Number of contacts per page
    page_size_query_param = 'page_size'  # Allow client to set page size using a URL parameter
    max_page_size = 100  # Maximum limit of page size that can be requested
