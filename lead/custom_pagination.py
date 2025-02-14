
# from rest_framework.pagination import PageNumberPagination

# class Paginator(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = "page_size"
#     max_page_size = 1000

    # def get_page_size(self, request):
    #     # Get the page_size from query parameters if available, otherwise use the default
    #     page_size = request.query_params.get(self.page_size_query_param)
        
    #     if page_size is not None:
    #         try:
    #             page_size = int(page_size)
    #             if page_size > self.max_page_size:
    #                 return self.max_page_size
    #             return page_size
    #         except ValueError:
    #             # If page_size is not a valid integer, fall back to the default
    #             return self.page_size
    #     return None

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class Paginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_page_size(self, request):
        # Get the page_size from query parameters if available, otherwise use the default
        page_size = request.query_params.get(self.page_size_query_param)

        if page_size is not None:
            try:
                page_size = int(page_size)
                if page_size > self.max_page_size:
                    return self.max_page_size
                return page_size
            except ValueError:
                # If page_size is not a valid integer, fall back to the default
                return self.page_size
        return None  # Return None if page_size is not specified, indicating no pagination

    def paginate_queryset(self, queryset, request, view=None):
        """
        This method is used to paginate the queryset.
        """
        page_size = self.get_page_size(request)

        if page_size is None:
            # If page_size is None, we return the entire dataset (no pagination)
            return queryset  # No pagination, just return the full queryset

        # Call the base method to perform pagination
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """
        This method is responsible for formatting the response including the pagination metadata.
        """
        # If there's no pagination applied (i.e., page_size is None), we set next and previous to None
        if not hasattr(self, 'page') or self.page is None:
            return Response({
                'count': len(data),
                'next': None,
                'previous': None,
                'results': data
            })

        # Get the next and previous page links
        next_link = self.get_next_link()
        previous_link = self.get_previous_link()

        # If the current page is the last one, set the next link to None
        if not next_link:
            next_link = None

        # If the current page is the first one, set the previous link to None
        if not previous_link:
            previous_link = None

        return Response({
            'count': self.page.paginator.count,
            'next': next_link,
            'previous': previous_link,
            'results': data
        })
