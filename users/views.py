from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Q
from .models import User
from .serializers import UserSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response(serializer.data)

class RegisterView(APIView):

    permission_classes = [AllowAny]
    
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=201)

        return Response(serializer.errors, status=400)


class UserSearchView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        query = request.query_params.get('q', '').strip()

        if len(query) < 2:
            return Response([])

        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(
            id=request.user.id
        ).order_by('username')[:20]

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)
