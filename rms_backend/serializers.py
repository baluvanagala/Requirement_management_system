from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Employee

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
        ]


class EmployeeSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"


class RegisterSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=False, default="")
    last_name = serializers.CharField(required=False, default="")
    role = serializers.ChoiceField(
        choices=Employee.ROLE_CHOICES,
        default="employee",
    )
    department = serializers.CharField(required=False, default="")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data.get("role", "employee"),
        )

        employee = Employee.objects.create(
            user=user,
            role=validated_data.get("role", "employee"),
            department=validated_data.get("department", ""),
        )

        return employee

    def to_representation(self, instance):
        """Return user details after registration."""
        return {
            "id": instance.user.id,
            "username": instance.user.username,
            "email": instance.user.email,
            "role": instance.role,
            "department": instance.department,
        }