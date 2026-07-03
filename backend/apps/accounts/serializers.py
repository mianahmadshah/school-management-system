"""
Serializers for the accounts app.

Serializers convert complex data (Django models) to/from JSON.
Think of them as a translation layer between Python and the API client.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# JWT CUSTOMIZATION
# Add extra fields to the JWT token payload
# ─────────────────────────────────────────────────────────────
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT token to include user info in the payload.
    This way, the frontend doesn't need an extra API call to get
    the user's role and name after login.
    """

    @classmethod
    def get_token(cls, user):
        # Get the standard token
        token = super().get_token(user)

        # Add custom claims to the token payload
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['role'] = user.role
        token['profile_picture'] = (
            user.profile_picture.url if user.profile_picture else None
        )

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Also return user info in the response body (not just in the token)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role,
            'profile_picture': (
                self.user.profile_picture.url
                if self.user.profile_picture else None
            ),
        }

        return data


# ─────────────────────────────────────────────────────────────
# USER SERIALIZERS
# ─────────────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for displaying user information.
    Used when returning user data in responses.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'profile_picture',
            'address', 'date_of_birth', 'gender', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.full_name


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    Validates password strength and ensures email uniqueness.
    """
    password = serializers.CharField(
        write_only=True,            # Password is never returned in response
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'phone', 'address', 'date_of_birth', 'gender',
            'password', 'password_confirm',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """Ensure passwords match."""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password': 'Password fields do not match.'}
            )
        return attrs

    def create(self, validated_data):
        """Create user with hashed password."""
        # Use create_user() to ensure password hashing via Django
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Email and role cannot be changed through this serializer.
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'address', 'date_of_birth', 'gender', 'profile_picture',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'new_password': 'Password fields do not match.'}
            )
        return attrs
