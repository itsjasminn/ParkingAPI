from http import HTTPStatus

from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, DestroyAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.models import User
from user.permissions import IsAdmin
from user.serializers import RegisterModelSerializer, ForgotSerializer, VerifyOTPSerializer, \
    ChangePasswordSerializer, ProfileModelSerializer
from user.throttling import ForLoginRateThrottle


# Create your views here.

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterModelSerializer
    http_method_names = 'delete',
    permission_classes = IsAuthenticated, IsAdmin,


@extend_schema(tags=['auth'])
class RegisterCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterModelSerializer


@extend_schema(tags=['auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ForLoginRateThrottle]
    pass


@extend_schema(tags=['auth'])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['auth'], request=ForgotSerializer)
class ForgotAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotSerializer(data=data)
        if serializer.is_valid():
            serializer.send_code()
            return JsonResponse({"status": HTTPStatus.ACCEPTED, "message": "Tastiqlash code emailga yuborildi !"})
        return JsonResponse({"status": HTTPStatus.BAD_REQUEST, "message": "Bunday email bazadan topilmadi !"})


@extend_schema(tags=['auth'], request=VerifyOTPSerializer)
class VerifyOTPAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        if serializer.is_valid():
            return JsonResponse({"status": HTTPStatus.ACCEPTED, "message": "Mofaqiyatli tastiqlandi"})
        return JsonResponse(
            {"status": HTTPStatus.BAD_REQUEST, "message": "Tastiqdan o'tmadi", "errors": serializer.errors})


@extend_schema(tags=['auth'], request=ChangePasswordSerializer)
class ChangePasswordAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = ChangePasswordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"status": HTTPStatus.OK, "message": "Mofaqiyatli o'zgartirildi"})
        return JsonResponse({"status": HTTPStatus.BAD_REQUEST, "message": "Xatolik", "errors": serializer.errors})


@extend_schema(tags=["profile"], responses=ProfileModelSerializer)
@permission_classes([IsAuthenticated])
class ProfileAPIView(APIView):

    def get(self, request):
        user = request.user
        serializer = ProfileModelSerializer(instance=user)
        return JsonResponse({"status": HTTPStatus.OK, "user": serializer.data})


@extend_schema(tags=['profile'], request=ProfileModelSerializer)
class ProfileUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileModelSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=['profile'])
class ProfileListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileModelSerializer
    permission_classes = IsAuthenticated, IsAdmin


@extend_schema(tags=['profile'])
class ProfileDestroyAPIView(DestroyAPIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser, FileUploadParser]

    queryset = User.objects.all()
    serializer_class = ProfileModelSerializer
    lookup_url_kwarg = 'pk'
    permission_classes = IsAuthenticated, IsAdmin
