from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PetProfile

User = get_user_model()


class Petprofileserializer(serializers.ModelSerializer):
    veterinarian = serializers.StringRelatedField(read_only=True)
    client = serializers.StringRelatedField(read_only=True)



    class Meta:
        model = PetProfile
        fields =  "__all__"

        read_only_fields = ['name', 'breed', 'age', 'gender']


    def __init__(self, *args, **kwargs):
        #Customizes fields dynamically based on user role
        super().__init__(*args, **kwargs)
        request = self.context.get('request')    

        if request:
            if request.user.role == 'client':
                self.fields['status'].read_only = True

            elif request.user.role == 'veterinarian':
                self.fields['reason'].read_only = True


#For creating petprofile
class Petprofilecreateserializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=PetProfile.objects.all())

    class Meta:
        model = PetProfile
        fields = "__all__"
