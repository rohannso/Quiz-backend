from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Quiz, Question, Option
class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True}
        }
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Passwords must match'
            })
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Username already exists'
            })
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Email already exists'
            })
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=True,  # Make user admin/staff
            is_active=True
        )
        
        return user
    
from rest_framework import serializers
from .models import Quiz
from django.utils import timezone


class QuizSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        max_length=200,
        min_length=3,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            'required': 'Quiz title is required.',
            'blank': 'Quiz title cannot be blank.',
            'max_length': 'Quiz title cannot exceed 200 characters.',
            'min_length': 'Quiz title must be at least 3 characters long.'
        }
    )
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_title(self, value):
        """
        Custom validation for title field
        """
        # Remove extra whitespace
        value = value.strip()
        
        # Check if title is only whitespace
        if not value or value.isspace():
            raise serializers.ValidationError("Quiz title cannot contain only whitespace.")
        
        # Check for minimum meaningful length (after stripping)
        if len(value) < 3:
            raise serializers.ValidationError("Quiz title must be at least 3 characters long.")
        
        # Check if title already exists (case-insensitive)
        if self.instance is None:  # Only check on creation, not update
            if Quiz.objects.filter(title__iexact=value).exists():
                raise serializers.ValidationError("A quiz with this title already exists.")
        else:  # On update, exclude current instance
            if Quiz.objects.filter(title__iexact=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("A quiz with this title already exists.")
        
        # Check for special characters only (no alphanumeric)
        if not any(c.isalnum() for c in value):
            raise serializers.ValidationError("Quiz title must contain at least one alphanumeric character.")
        
        return value
    
    def validate(self, data):
        """
        Object-level validation
        """
        return data
    
class QuizDetailSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'created_at', 'questions_count',]
        read_only_fields = ['id', 'created_at', 'questions_count']

class OptionSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        max_length=200,
        min_length=1,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            'required': 'Option text is required.',
            'blank': 'Option text cannot be blank.',
            'max_length': 'Option text cannot exceed 200 characters.',
            'min_length': 'Option text must be at least 1 character long.'
        }
    )
    is_correct = serializers.BooleanField(required=True)
    
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['id']
    
    def validate_text(self, value):
        """Validate option text"""
        value = value.strip()
        
        if not value or value.isspace():
            raise serializers.ValidationError("Option text cannot contain only whitespace.")
        
        if not any(c.isalnum() for c in value):
            raise serializers.ValidationError("Option text must contain at least one alphanumeric character.")
        
        return value


class QuestionCreateSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=True)
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            'required': 'Question text is required.',
            'blank': 'Question text cannot be blank.'
        }
    )
    quiz = serializers.PrimaryKeyRelatedField(
        queryset=Quiz.objects.all(),
        required=True,
        error_messages={
            'required': 'Quiz ID is required.',
            'does_not_exist': 'Quiz with this ID does not exist.'
        }
    )
    
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'options', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_text(self, value):
        """Validate question text"""
        value = value.strip()
        
        if not value or value.isspace():
            raise serializers.ValidationError("Question text cannot contain only whitespace.")
        
        if len(value) < 5:
            raise serializers.ValidationError("Question text must be at least 5 characters long.")
        
        if not any(c.isalnum() for c in value):
            raise serializers.ValidationError("Question text must contain at least one alphanumeric character.")
        
        return value
    
    def validate_options(self, value):
        """Validate options list"""
        if not value:
            raise serializers.ValidationError("At least 2 options are required.")
        
        if len(value) < 2:
            raise serializers.ValidationError("At least 2 options are required.")
        
        if len(value) > 6:
            raise serializers.ValidationError("Maximum 6 options are allowed.")
        
        # Check for duplicate option texts (case-insensitive)
        option_texts = [opt['text'].strip().lower() for opt in value]
        if len(option_texts) != len(set(option_texts)):
            raise serializers.ValidationError("Duplicate options are not allowed.")
        
        # Count correct answers
        correct_count = sum(1 for opt in value if opt.get('is_correct', False))
        
        if correct_count == 0:
            raise serializers.ValidationError("At least one option must be marked as correct.")
        
        if correct_count > 1:
            raise serializers.ValidationError("Only one option can be marked as correct.")
        
        return value
    
    def validate(self, data):
        """Object-level validation"""
        quiz = data.get('quiz')
        text = data.get('text', '').strip()
        
        # Check if question with same text already exists in this quiz
        if Question.objects.filter(quiz=quiz, text__iexact=text).exists():
            raise serializers.ValidationError({
                'text': 'A question with this text already exists in this quiz.'
            })
        
        return data
    
    def create(self, validated_data):
        """Create question with options"""
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        
        return question


class QuestionDetailSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'quiz_title', 'text', 'options', 'created_at']
        read_only_fields = ['id', 'created_at']

    
# Add these at the end of serializers.py

class QuizTakeSerializer(serializers.ModelSerializer):
    """Serializer for taking quiz - excludes correct answers"""
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'options']
    
    def get_options(self, obj):
        """Return options without is_correct field"""
        options = obj.options.all()
        return [{'id': opt.id, 'text': opt.text} for opt in options]


class AnswerSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers"""
    answers = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'Answers are required.',
            'empty': 'Answer list cannot be empty.'
        }
    )
    
    def validate_answers(self, value):
        """Validate answer format"""
        if not value:
            raise serializers.ValidationError("At least one answer is required.")
        
        for answer in value:
            if 'question_id' not in answer:
                raise serializers.ValidationError("Each answer must have 'question_id'.")
            
            if 'option_id' not in answer:
                raise serializers.ValidationError("Each answer must have 'option_id'.")
            
            # Validate that they are integers
            try:
                int(answer['question_id'])
                int(answer['option_id'])
            except (ValueError, TypeError):
                raise serializers.ValidationError("question_id and option_id must be integers.")
        
        return value