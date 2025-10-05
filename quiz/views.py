from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import AdminRegistrationSerializer  # Add this import



@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Admin registration endpoint
    """
    serializer = AdminRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Create token for the new user
        token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Admin user created successfully',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Admin login endpoint
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user is staff/admin
    if not user.is_staff:
        return Response(
            {'error': 'Only admin users can login'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Admin logout endpoint
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Quiz, Question, Option
from .serializers import (
    QuizSerializer, QuestionDetailSerializer, QuestionCreateSerializer,QuizDetailSerializer,
    QuizTakeSerializer, AnswerSubmissionSerializer
)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy','retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['take', 'submit']:
            return [AllowAny()] 
        return [IsAuthenticatedOrReadOnly()]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new quiz with validation
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    'message': 'Quiz created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update quiz with validation
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {
                    'message': 'Quiz updated successfully',
                    'data': serializer.data
                }
            )
        
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete quiz
        """
        instance = self.get_object()
        quiz_title = instance.title
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': f'Quiz "{quiz_title}" deleted successfully'
            },
            status=status.HTTP_200_OK
        )
    
    def list(self, request, *args, **kwargs):
        """
        List all quizzes
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response(
                {
                    'message': 'No quizzes found',
                    'data': []
                },
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'message': 'Quizzes retrieved successfully',
                'count': queryset.count(),
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve single quiz with details
        """
        try:
            instance = self.get_object()
            serializer = QuizDetailSerializer(instance)
            return Response(
                {
                    'message': 'Quiz retrieved successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Quiz.DoesNotExist:
            return Response(
                {
                    'error': 'Quiz not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def take(self, request, pk=None):
        """Endpoint to fetch quiz questions without correct answers - Public"""
        try:
            quiz = self.get_object()
            questions = quiz.questions.all()
            
            if not questions.exists():
                return Response(
                    {
                        'error': 'This quiz has no questions yet'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = QuizTakeSerializer(questions, many=True)
            return Response(
                {
                    'message': 'Quiz questions retrieved successfully',
                    'quiz_title': quiz.title,
                    'total_questions': questions.count(),
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Quiz.DoesNotExist:
            return Response(
                {
                    'error': 'Quiz not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def submit(self, request, pk=None):
        """Endpoint to submit answers and get score - Public"""
        try:
            quiz = self.get_object()
            serializer = AnswerSubmissionSerializer(data=request.data)
            
            if serializer.is_valid():
                answers = serializer.validated_data['answers']
                score = 0
                total = len(answers)
                
                if total == 0:
                    return Response(
                        {
                            'error': 'No answers provided'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                for answer in answers:
                    question_id = answer.get('question_id')
                    option_id = answer.get('option_id')
                    
                    try:
                        option = Option.objects.get(id=option_id, question_id=question_id)
                        if option.is_correct:
                            score += 1
                    except Option.DoesNotExist:
                        pass
                
                return Response({
                    'message': 'Quiz submitted successfully',
                    'score': score,
                    'total': total,
                    'percentage': round((score / total) * 100, 2)
                })
            
            return Response(
                {
                    'error': 'Validation failed',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Quiz.DoesNotExist:
            return Response(
                {
                    'error': 'Quiz not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'retrieve' or self.action == 'list':
            return QuestionDetailSerializer
        return QuestionCreateSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new question with options"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            response_serializer = QuestionDetailSerializer(serializer.instance)
            return Response(
                {
                    'message': 'Question created successfully',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request, *args, **kwargs):
        """List all questions"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Optional: Filter by quiz_id
        quiz_id = request.query_params.get('quiz_id', None)
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        
        if not queryset.exists():
            return Response(
                {
                    'message': 'No questions found',
                    'data': []
                },
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'message': 'Questions retrieved successfully',
                'count': queryset.count(),
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single question with details"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    'message': 'Question retrieved successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Question.DoesNotExist:
            return Response(
                {
                    'error': 'Question not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete question"""
        instance = self.get_object()
        question_text = instance.text[:50]
        self.perform_destroy(instance)
        
        return Response(
            {
                'message': f'Question deleted successfully'
            },
            status=status.HTTP_200_OK
        )

