"""
Custom middleware for LakChogo Connect
"""

import re
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoggingMiddleware(MiddlewareMixin):
    """Middleware to log requests"""
    
    def process_request(self, request):
        """Log incoming request"""
        if request.path.startswith('/api/'):
            # Log API requests
            print(f"[API] {request.method} {request.path}")
        
        return None


class TimezoneMiddleware(MiddlewareMixin):
    """Middleware to set timezone based on user preference"""
    
    def process_request(self, request):
        """Set timezone from user session or IP"""
        # Implementation would use geolocation or user preference
        pass


class APIAuthenticationMiddleware(MiddlewareMixin):
    """Middleware to handle API authentication"""
    
    def process_request(self, request):
        """Check API authentication for API routes"""
        if request.path.startswith('/api/'):
            # Skip authentication for certain endpoints
            skip_paths = ['/api/v1/auth/login/', '/api/v1/auth/register/']
            for path in skip_paths:
                if request.path.startswith(path):
                    return None
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                # Allow token authentication through DRF
                pass
        
        return None


class CorsMiddleware(MiddlewareMixin):
    """Middleware to handle CORS"""
    
    def process_response(self, request, response):
        """Add CORS headers"""
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers"""
    
    def process_response(self, request, response):
        """Add security headers to all responses"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if not request.path.startswith('/api/'):
            response['Content-Security-Policy'] = "default-src 'self'"
        
        return response
