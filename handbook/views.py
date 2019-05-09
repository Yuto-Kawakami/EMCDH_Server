from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import  PermissionDenied
from rest_framework import viewsets, authentication, permissions, generics, status, filters, request
from rest_framework.response import Response
from django.db import transaction
from handbook.serializers import UserSerializer, HealthSerializer, PregnancySerializer, ConsultationRecordSerializer, ChildSerializer, GPACSerializer, LocationSerializer, AddressSerializer, AccessControlSerializer
from handbook.models import User, Health, Pregnancy, ConsultationRecord, Child, GPAC, Location, Address, AccessControl
from django_filters import rest_framework as filters 
from rest_framework import generics
from rest_framework.views import APIView
from sklearn import linear_model
import pickle
import os
import pandas as pd


# Create your views here.
class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ['device_id'] 

class UserViewSet(viewsets.ModelViewSet):
# class UserViewSet(LoginRequiredMixin, PermissionRequiredMixin, viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_class = UserFilter

class HealthSet(viewsets.ModelViewSet):
    queryset = Health.objects.all()
    serializer_class = HealthSerializer
    permission_required = 'models.rules_view_item'

class GpacFilter(filters.FilterSet):
    class Meta:
        model=GPAC
        fields = ['user']

class GPACSet(viewsets.ModelViewSet):
    queryset = GPAC.objects.all()
    serializer_class = GPACSerializer
    filter_class = GpacFilter
    # permission_required = 'models.rules_view_item'

class PregnancyFilter(filters.FilterSet):
    class Meta:
        model = Pregnancy
        fields = ['user']

class PregnancySet(viewsets.ModelViewSet):
    queryset = Pregnancy.objects.all()
    serializer_class = PregnancySerializer
    filter_class = PregnancyFilter
    # permission_required = 'handbooks.rules_view_item'

class ConsultationRecordFilter(filters.FilterSet):
    class Meta:
        model = ConsultationRecord
        fields = ['pregnancy']

class ConsultationRecordSet(viewsets.ModelViewSet):
    queryset = ConsultationRecord.objects.all().order_by('-consultation_date')
    serializer_class = ConsultationRecordSerializer
    filter_class = ConsultationRecordFilter

class ChildFilter(filters.FilterSet):
    class Meta:
        model = Child
        fields = ['pregnancy']

class ChildSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    filter_class = ChildFilter

class AccessControlFilter(filters.FilterSet):
    class Meta:
        model = AccessControl
        fields = ['user']

class AccessControlSet(viewsets.ModelViewSet):
    queryset = AccessControl.objects.all()
    serializer_class = AccessControlSerializer
    # filter_class = AccessControl

class LocationFilter(filters.FilterSet):
    class Meta:
        model = Location
        fields = ['user']

class LocationSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('-timestamp')
    serializer_class = LocationSerializer
    filter_class = LocationFilter

class AddressSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class UserSummary(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        res = {'data':[]}
        for user in User.objects.all().values():
            if not user['enable_location_sharing']:
                continue
            data = {}

            data['user'] = user
            if Location.objects.filter(user=user['id']).count() >0 :
                data['location'] = Location.objects.all().order_by('-timestamp').filter(user=user['id']).values()[0]
            else:
                continue
            if Pregnancy.objects.filter(user=user['id']).count() >0 :
                data['pregnancy'] = Pregnancy.objects.filter(user=user['id']).values()[0]
                if ConsultationRecord.objects.filter(pregnancy=data['pregnancy']['id']).count()>0:
                    records = []
                    for record in ConsultationRecord.objects.filter(pregnancy=data['pregnancy']['id']).values():
                        records.append(record)
                    data['consultationRecords'] = records

                if Child.objects.filter(pregnancy=data['pregnancy']['id']).count()>0:
                    children = []
                    for child in Child.objects.filter(pregnancy=data['pregnancy']['id']).values():
                        children.append(child)
                    data['children'] = children
            if GPAC.objects.filter(user=user['id']).count() > 0:
                data['gpac'] = GPAC.objects.filter(user=user['id']).values()[0]

            res['data'].append(data)

        return Response(res)

class PredictAccessControl(APIView):
    def get(self, request, format=None):
        input_num = int(request.GET.get('input_num'))

        # input_array = []
        input_dict = {}
        for i in range(input_num):
            key = 'q' + str(i)
            # input_array.append(request.GET.get(key))
            input_key_val = request.GET.get(key).split('-')
            input_dict[input_key_val[0]] = [int(input_key_val[1])]

        res = {'data': []}
        res['data'].append(self.predict(input_dict))
        # predictする操作書く ほんとは他のところに書いて呼び出したほうが良い

        return Response(res)

    # def predict(self,input_array):
    def predict(self, input_dict):
        # 実際の質問順に応じた並べ替えが必要
        columns = [
            '19',
            '26',
            '36',
            '8',
            '9',
            '10',
            '11',
            '12',
            '13',
            '14',
            '15',
            '16',
            '17',
            '18',
            '20',
            '21',
            '22',
            '23',
            '24',
            '25',
            '27',
            '28',
            '29',
            '32',
            '33',
            '35',
            '37',
            '38',
            '39',
            '40',
            '41',
            '42',
            '43',
            '44',
            '45',
            '46',
            '48',
            '50',
            '47',
        ]
        # inputとしてえた回答の長さに応じて、predictし、入力されていない値群のデータをkey: valueで返す

        # モデルのロード
        # num = len(input_array)
        num = len(input_dict)
        base = os.path.dirname(os.path.abspath(__file__))
        print(base)
        path = os.path.normpath(os.path.join(base, './models/model_' + str(num) + '.sav'))

        lrs = pickle.load(open(path, 'rb'))

        # inputのdf作成
        # input_dict = {}
        # for i in range(len(input_array)):
        #     input_dict[columns[i]] = [input_array[i]]

        print(input_dict)
        input_df = pd.DataFrame.from_dict(input_dict)

        # predict
        res = {}
        for i in range(len(columns) - num):
            # inputに使っている値は予測しない
            column_idx = i + num
            column = columns[column_idx]
            
            res[column] = lrs[column].predict(input_df)[0]

        return res