from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'student_id']
        read_only_fields = ['id', 'role']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Allows students to update their push_token and phone_number for notifications."""

    class Meta:
        model = User
        fields = ['phone_number', 'push_token', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'student_id']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            student_id=validated_data.get('student_id'),
            role=User.STUDENT,
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds role and student_id claims to the JWT token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['student_id'] = user.student_id
        return token
