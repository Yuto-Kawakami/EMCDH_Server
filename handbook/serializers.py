from .models import User, Health, Pregnancy, ConsultationRecord, Child, GPAC, Location, Address, AccessControl
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'url', 'device_id', 'email', 'id', 'password', 'enable_location_sharing', 'triage_level')
        # fields = '__all__'
    
    def create(self, validated_data):
        return User.objects.create_user(
            device_id=validated_data['device_id'],
            # email=validated_data['email'],
            password=validated_data['password'],
        )

class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class HealthSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Health
        fields = '__all__'

class PregnancySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pregnancy
        fields = '__all__'

class GPACSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GPAC
        fields = '__all__'

class PregnancySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pregnancy
        fields = ('url', 'id','user', 'last_menstruation_start_date', 'expected_delivery_date', 'will_caesarean_section', 'birth_already', 'birthday', 'delivery_method', 'placenta_attachment_site')

class ChildSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'

class ConsultationRecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ConsultationRecord
        fields = '__all__'

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class AccessControlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessControl
        fields = '__all__'