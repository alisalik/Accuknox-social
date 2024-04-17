from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import User,FriendRequest
from rest_framework import status
from .serializer import UserRegisterationSerializer,CustomTokenRefreshSerializer,UserLoginSerializer,FriendRequestSerializer,UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination



# Create your views here.



class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class UsersAPIView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterationSerializer
    permission_classes = (AllowAny,)
    # serializer_action_classes = {
    #    "sign_in" : UserLoginSerializer
    # }
    def create(self, request, *args, **kwargs):
        
        email = request.data.get('email').lower()
        serializer = self.get_serializer(data=request.data)
        user = User.objects.filter(email=email).first()
        if user:
            response_data = {
            'data': {'user_exists' : True},
            'error': {
                'message': "User with this email or mobile already exists"
            }
            }
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        if serializer.is_valid(raise_exception=True):
          serializer.save()
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        data["message"] = "Signed up successfully"
        response_data = {'data': data}
        return Response(response_data, status=status.HTTP_201_CREATED)
    

    @action(methods=['post'],detail= False,url_path='login')
    def login(self, request, *args, **kwargs):
      permission_classes = (AllowAny,)
      email = request.data.get('email')
      password = request.data.get('password')
      try:
        email = email.lower()
        # user = User.objects.get(email=email)
        user = User.objects.filter(email=email).first()
        if (not user):
          response_data = {'error': {'message': "This email address doesn't exist! Would you like to Sign up?"}}
          return Response(response_data, status=status.HTTP_404_NOT_FOUND)  
      except User.DoesNotExist:
        response_data = {'error': {'message': "This email address or phone number doesn't exist! Would you like to Sign up?"}}
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)      
      if check_password(password,user.password): 
        #   serializer = self.get_serializer(user)
          serializer = UserLoginSerializer(user)
          token = RefreshToken.for_user(user)
          data = serializer.data
          data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
          data["message"] = "Login successful"
          response_data = {'data': data}
          return Response(response_data, status=status.HTTP_200_OK)
      else:
          response_data = {'error': {'message': "Invalid credentials"}}
          return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False,methods=['post'],url_path='logout')
    def logout(self, request):
      try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
          token = RefreshToken(refresh_token)
          token.blacklist()
          response_data = {'data': {'message': "Logged out successfully"}}
          return Response(response_data, status=status.HTTP_205_RESET_CONTENT)
        else:
          response_data = {'error': {'message': "Token is invalid or empty"}}
          return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
        response_data = {'error': {'message': "Something went wrong"}}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
      


class UserSearchAPIView(APIView):
   permission_classes = (IsAuthenticated,)
   def get(self,request):
        try: 
            search_keyword = request.query_params.get('search','')
            if search_keyword:
                print(search_keyword)
                users = User.objects.filter(Q(username__icontains=search_keyword) | Q(email__icontains=search_keyword)).exclude(id=request.user.id)
                if users:
                    paginator = PageNumberPagination() # need to move to pagination.py
                    paginator.page_size = 10  
                    result_page = paginator.paginate_queryset(users, request)
                    serializer = UserLoginSerializer(result_page, many=True)
                
                    # Return paginated response
                    return paginator.get_paginated_response(serializer.data)
                # Serialize paginated data
                else:
                   response_data={'message':'No users exist with this name and email'}
                   return Response(response_data,status=status.HTTP_204_NO_CONTENT)
            else:
               return Response({'error':'No search keyword provided'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           response_data={'error':{'message':'Something went wrong'}}
           print(e)
           return Response(response_data,status=status.HTTP_400_BAD_REQUEST)
        

class Requests(ModelViewSet):
    permission_classes=(IsAuthenticated,)
    queryset = FriendRequest.objects.all()
    serializer_class=FriendRequestSerializer

    def list(self, request, *args, **kwargs):
        try:
            request_stat = request.query_params.get('status')
            if request_stat:
                list_friend = FriendRequest.objects.filter(Q(to_user=self.request.user.id) & Q(status=request_stat)).values('from_user')
                if list_friend:
                    friend_list = User.objects.filter(id__in=list_friend).values('username','email')
                    if friend_list:
                        response_data = {'results': list(friend_list)}
                        return Response(response_data)
                return Response({f'No {request_stat} requests found'},status=status.HTTP_404_NOT_FOUND)
            return Response({f'Please select valid option accepted/pending'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           print(e)
           return Response({'something went wrong'},status=status.HTTP_400_BAD_REQUEST)




    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            if email:
                user = User.objects.filter(email=email).first()
                if user:
                    to_user = user.id
                    from_user = self.request.user.id
                    data={
                    'to_user':to_user,
                    'from_user':from_user
                    }
                    serializer = self.get_serializer(data=data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                    return Response({'message':f'request sent to user {user.email}'},status=status.HTTP_201_CREATED)
                else:
                    return Response({'error':'No such user exists'},status=status.HTTP_404_NOT_FOUND)
            else:
               return Response({'error':'provide valid email'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error':'Something wrong'},status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False,methods=['post'],url_path='action_request')
    def action_request(self,request):
        try:
            actions = request.query_params.get('action')
            email = request.data.get('email')
            if actions and email:
                req_status=FriendRequest.objects.filter(from_user__email=email).values('status','from_user')
                if req_status and req_status[0]['status']=='pending':
                    if actions=='accept':
                        req_status = FriendRequest.objects.filter(from_user__email=email).values('status','from_user').update(status='accepted')
                        return Response({'data':'request accepted'},status=status.HTTP_201_CREATED)
                    elif actions=='reject':
                        req_status = FriendRequest.objects.filter(from_user__email=email).values('status','from_user').update(status='rejected')
                        return Response({'data':'request rejected'},status=status.HTTP_201_CREATED)
                    return Response({'error':'unknown status please accept or reject'},status=status.HTTP_400_BAD_REQUEST)
                return Response({f'request already {req_status[0]['status']}'},status=status.HTTP_400_BAD_REQUEST)
            return Response({'please enter valid email and select accept or reject option'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           print(e)
           return Response({'something went wrong'},status=status.HTTP_400_BAD_REQUEST)

        

    
            
                
            
               
         
        


    