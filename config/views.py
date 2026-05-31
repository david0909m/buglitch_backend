from django.http import JsonResponse


def home(request):
    return JsonResponse({
        'message': 'Buglitch API',
        'status': 'online',
        'developer': 'david0909m',
    })