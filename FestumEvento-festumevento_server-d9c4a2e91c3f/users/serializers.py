from rest_framework import serializers
from rest_framework.authtoken.models import Token
from . import models


class UserSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(min_length=3, required=True)
    # email = serializers.EmailField(
    #     required=True,
    #     validators=[UniqueValidator(queryset=models.User.objects.all())]
    # )
    # email = serializers.EmailField(
    #     required=True,
    #     validators=[UniqueValidator(queryset=models.User.objects.all())]
    # )
    # mobile = serializers.CharField(
    #     required=True,
    #     validators=[UniqueValidator(queryset=models.User.objects.all())]
    # )
    # country_code = serializers.CharField(required=True)
    # role = serializers.CharField(required=True)
    status = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(
        allow_blank=False, write_only=True)

    def create(self, validated_data):
        user = models.User.objects.create_user(
            validated_data['name'],
            validated_data['email'],
            validated_data['mobile'],
            validated_data['country_code'],
            validated_data['role'],
            validated_data['password'],
            validated_data['confirm_password'],
            validated_data["refer_code"],
            validated_data["my_refer_code"],
            validated_data["fcm_token"]
        )
        return user

    def response(self):
        return self.data

    class Meta:
        model = models.User
        fields = ('id', 'name', 'email', 'mobile', 'country_code', 'role', 'active', 'verify', 'created_date', 'password',
                  'confirm_password', 'status', 'refer_code', 'my_refer_code', 'fcm_token', 'about')


class UserUpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, write_only=True, required=False)
    email = serializers.CharField(max_length=255, write_only=True, required=False)
    mobile = serializers.CharField(max_length=20, write_only=True, required=False)
    country_code = serializers.CharField(max_length=10, write_only=True, required=False)
    about = serializers.CharField(max_length=5000, write_only=True, required=False)

    class Meta:
        model = models.User
        fields = ['name', 'email', 'mobile', 'country_code', 'about']

    def validate(self, attrs):
        name = attrs.get('name')
        email = attrs.get('email')
        mobile = attrs.get('mobile')
        country_code = attrs.get('country_code')
        about = attrs.get('about')
        user = self.context.get('user')
        if name:
            user.name = name
        if email:
            user.email = email
        if mobile:
            user.mobile = mobile
        if country_code:
            user.country_code = country_code
        if about:
            user.about = about
        user.save()
        return attrs


class TokenSerializer(serializers.ModelSerializer):

    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user')
