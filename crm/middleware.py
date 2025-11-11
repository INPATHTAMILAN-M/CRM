"""
Custom middleware for CRM project
"""


class CorsMediaMiddleware:
    """
    Middleware to add CORS headers to media file responses.
    This allows media files to be accessed from different origins.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers to media file responses
        if request.path.startswith('/media/'):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Expose-Headers'] = 'Content-Type, Content-Disposition'
            
            # Handle preflight requests
            if request.method == 'OPTIONS':
                response.status_code = 200
        
        return response
