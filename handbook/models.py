from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from address.models import AddressField

from enum import Enum

class TriageLevel (Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True
 
    def _create_user(self, device_id, password, **extra_fields):
    # def _create_user(self, email, password, **extra_fields):
        # if not email:
        #     raise ValueError('The given email must be set')
        # email = self.normalize_email(email)
        # user = self.model(email=email, **extra_fields)

        user = self.model(device_id=device_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
 
    def create_user(self, device_id, password, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(device_id, password, **extra_fields)
 
    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
 
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
 
        return self._create_user(email, password, **extra_fields)
 
 
class User(AbstractBaseUser, PermissionsMixin):
    # enumデカ期待
    triage_level = (
        (0, 'red'),
        (1, 'yellow'),
        (2, 'green'),
    )
    """カスタムユーザーモデル."""
    device_id = models.CharField(_('device id'), max_length=150, blank=True, unique=True)
    email = models.EmailField(_('email address'), blank=True, unique=True, null=True)
    enable_location_sharing = models.NullBooleanField('位置情報の共有', default=False)

    triage_level = models.IntegerField(
        'triage level',
        choices=triage_level,
        null=True,
    )

    is_pregnant = models.BooleanField(
        default=True,
        help_text=_(
            'if user is a pregnant, pregnancy  et. al. is created'
            'else pregnancy record is not created and connected to other user\'s record'
        ),
    )
 
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
 
    objects = UserManager()
    full_name = models.CharField(_('full name'), max_length=150, blank=True)
 
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'device_id'
    REQUIRED_FIELDS = []
 
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
 
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
 
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
 
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
 
    @property
    def username(self):
        """username属性のゲッター
 
        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    full_name = models.CharField(_('full name'), max_length=150, blank=True)

    birthday = models.DateField(_('birthday'), null=True, )
    job = models.TextField(blank=True)
    tel = PhoneNumberField(blank=True) # https://github.com/stefanfoulis/django-phonenumber-field

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    postal_code = models.CharField(blank=True, max_length=1024)
    prefecture = models.CharField(blank=True, max_length=1024)
    city = models.CharField(blank=True, max_length=1024)
    street = models.CharField(blank=True, max_length=1024)
    building = models.CharField(blank=True, max_length=1024)

class Health(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField('date created')
    updated = models.DateTimeField('date updated')

    height = models.IntegerField(null=True)
    weight_before_pregnancy = models.FloatField(null=True)

    allergy = models.TextField(null=True)
    medicine_in_medication = models.TextField(null=True)

# GPAC(妊娠歴)
class GPAC(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gravidity = models.IntegerField('妊娠回数', null=True)
    parity = models.IntegerField('出産回数', null=True)
    abortion = models.IntegerField('自然/人工流産の回数', null=True)
    caesarean_section = models.IntegerField('帝王切開の回数', null=True)

# 今回の妊娠に関するデータ
class Pregnancy(models.Model):
    REASON_CHOICES = (
        (0, 'その他'),
        (1, '骨盤位'),
        (2, '既往帝王切開'),
        (3, '胎盤位E異常'),
        (4, '希望'),
    )
    CHANGE_CHOICES = (
        (0, '不明'),
        (1, 'あり'),
        (2, 'なし'),
    )

    PLACENTA_ATTACHMENT_SITES = (
        (0, 'unknown'), #不明
        (1, 'normal site'), #正常
        (2, 'margin site'), # 辺縁
        (3, 'back site'), #後壁
    )

    DELIVERY_METHODS = (
        (0, '不明'),
        (1, '経膣分娩'),
        (2, '帝王切開'),
    )

    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    last_menstruation_start_date = models.DateField('最終月経開始日', null=True)
    expected_delivery_date = models.DateField('分娩予定日', null=True)
    will_caesarean_section = models.NullBooleanField('帝王切開の予定', null=True)

    birth_already = models.BooleanField('出産済み', default=False)
    birthday = models.DateField('出産日', null=True)
    delivery_method = models.IntegerField(
        '分娩方法',
        choices=DELIVERY_METHODS,
        null = True,
    )


    reason_for_caesarean_section = models.IntegerField(
        '帝王切開の理由',
        choices=REASON_CHOICES,
        null=True,
    )
    possibility_of_change_delivery_date = models.IntegerField(
        '予定日修正',
        choices=CHANGE_CHOICES,
        null=True,
    )
    placenta_attachment_site = models.IntegerField(
        '胎盤付着部位',
        choices=PLACENTA_ATTACHMENT_SITES,
        null=True,
    )
    risk_of_threatened_abortion = models.IntegerField(
        '切迫流早産の危険性', 
        choices=CHANGE_CHOICES,
        null=True,
    )


## 毎回の診察に伴うデータ
class ConsultationRecord(models.Model):
    DETECTION_CHOICES = (
        (0, '-'),
        (1, '+'),
        (2, '++'),
        (3, '+++'),
        (4, '++++'),
    )
    CERVICAL_CHOICES = (
        (0, '不明'),
        (1, '正常'),
        (2, '短い'),
    )

    pregnancy = models.ForeignKey(Pregnancy,default=None, on_delete=models.CASCADE)
    consultation_date = models.DateField('検診日')
    uterotome_length = models.FloatField('子宮底長', null=True)
    weight = models.FloatField(null=True)
    systolic_blood_pressure = models.FloatField('収縮期血圧/最高血圧', null=True)
    diastolic_blood_pressure = models.FloatField('拡張期血圧/最低血圧', null=True)
    abdominal_circumference = models.FloatField('腹囲', null=True)
    edema = models.IntegerField(
        '浮腫',
        choices=DETECTION_CHOICES,
        null=True,
    )
    urinary_protein = models.IntegerField(
        '尿蛋白',
        choices=DETECTION_CHOICES,
        null=True,
    )
    urinary_sugar = models.IntegerField(
        '尿糖',
        choices=DETECTION_CHOICES,
        null=True,
    )
    cervical_length = models.IntegerField(
        '頸管長',
        choices=CERVICAL_CHOICES,
        null=True,
    )


class Child(models.Model):
    CHANGE_CHOICES = (
        (0, '不明'),
        (1, 'あり'),
        (2, 'なし'),
    )
    UNKNOWN = 0

    CEPHALIC_PRESENTATION = 1
    BREECH_PRESENTATION = 2
    SHOULDER_PRESENTATION = 3

    PRESENTATIONS = (
        (UNKNOWN, 'unknown'),
        (CEPHALIC_PRESENTATION, '頭位'), 
        (BREECH_PRESENTATION, '骨盤位'), 
        (SHOULDER_PRESENTATION, '横位'), 
    )

    pregnancy = models.ForeignKey(Pregnancy, on_delete=models.CASCADE)
    estimated_weight = models.FloatField(null=True,)
    presentation = models.IntegerField(
        '胎位',
        choices=PRESENTATIONS,
        null=True,
    )

class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accuracy = models.FloatField('位置情報の精度', null=True,)
    latitude = models.FloatField('緯度')
    longitude = models.FloatField('経度')
    timestamp = models.DateTimeField('タイムスタンプ')

class AccessControl(models.Model):
    TRIGGER_CHOICES = (
        (0,'地震'),
    )

    PLACE_CHOICES = (
        (0, '現在地'),
        (1, '自宅'),
    )

    ROLE_CHOICES = (
        (0, '特定のアカウント'),
        (1, '主治医'),
        (2, '災害医療コーディネーター'),
        (3, '小児周産期リエゾン'),
        (4, '医療班のメンバー'),
    )

    ALLOW_CHOICES = (
        (0, 'いかなる場合も共有しない'),
        (1, '大規模災害時のみ'),
        (2, '中規模以上の災害時'),
        (3, '小規模以上の災害時'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # title = models.CharField(_('title'), max_length=150, blank=True)

    # trigger = models.TypedMultipleChoiceField(
    #     'トリガー',
    #     choices=TRIGGER_CHOICES,
    # )

    # 実験用
    subject_no = models.CharField(_('被験者番号'), max_length=30, blank=True)
    experiment_no = models.CharField(_('実験番号'), max_length=30, blank=True)
    is_assisted = models.NullBooleanField('アシストの有無', null=True)
    change_num = models.IntegerField('手動で変更した回数', null=True)

    suggest_history = models.TextField(blank=True)


    # plcae = models.IntegerField(
    #     'トリガーの場所',
    #     choices=PLACE_CHOICES,
    #     null=True,
    # )

    # role = models.IntegerField(
    #     'アクセスを許すロール',
    #     choices=ROLE_CHOICES,
    #     null=True,
    # )

    # 基本情報
    full_name = models.IntegerField(
        'フルネーム',
        choices=ALLOW_CHOICES,
        null=True,
    )

    birthday = models.IntegerField(
        '生年月日',
        choices=ALLOW_CHOICES,
        null=True,
    )

    job = models.IntegerField(
        '現在の就労状況(就労の有無・仕事内容・通勤時間・就労時間など)',
        choices=ALLOW_CHOICES,
        null=True,
    )

    tel = models.IntegerField(
        '電話番号',
        choices=ALLOW_CHOICES,
        null=True,
    )

    address = models.IntegerField(
        '住所',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # 妊産婦の健康情報
    height = models.IntegerField(
        '身長',
        choices=ALLOW_CHOICES,
        null=True,
    )
    weight_before_pregnancy = models.IntegerField(
        '妊娠前体重',
        choices=ALLOW_CHOICES,
        null=True,
    )

    medical_history = models.IntegerField(
        '既往歴',
        choices=ALLOW_CHOICES,
        null=True,
    )

    allergy_key = models.IntegerField(
        'アレルギー情報',
        choices=ALLOW_CHOICES,
        null=True,
    )

    taking_drugs = models.IntegerField(
        '服用中の薬',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # Gpac
    gravidity = models.IntegerField(
        '妊娠回数',
        choices=ALLOW_CHOICES,
        null=True,
    )

    parity = models.IntegerField(
        '出産回数',
        choices=ALLOW_CHOICES,
        null=True,
    )

    abortion = models.IntegerField(
        '自然/人工流産の回数',
        choices=ALLOW_CHOICES,
        null=True,
    )

    caesarean_section = models.IntegerField(
        '帝王切開の回数',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # Pregnancy
    last_menstruation_start_date = models.IntegerField(
        '最終月経開始日',
        choices=ALLOW_CHOICES,
        null=True,
    )

    expected_delivery_date = models.IntegerField(
        '分娩予定日',
        choices=ALLOW_CHOICES,
        null=True,
    )

    num_of_children = models.IntegerField(
        '分娩予定日',
        choices=ALLOW_CHOICES,
        null=True,
    )

    will_caesarean_section = models.IntegerField(
        '帝王切開の予定',
        choices=ALLOW_CHOICES,
        null=True,
    )

    reason_for_caesarean_section = models.IntegerField(
        '帝王切開の理由',
        choices=ALLOW_CHOICES,
        null=True,
    )

    scheduled_date_correction = models.IntegerField(
        '予定日修正',
        choices=ALLOW_CHOICES,
        null=True,
    )

    placenta_attachment_site = models.IntegerField(
        '胎盤付着部位',
        choices=ALLOW_CHOICES,
        null=True,
    )

    risk_of_threatened_abortion = models.IntegerField(
        '切迫流早産の危険性',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # Consultation Record
    uterotome_length = models.IntegerField(
        '子宮底長',
        choices=ALLOW_CHOICES,
        null=True,
    )

    weight = models.IntegerField(
        '体重',
        choices=ALLOW_CHOICES,
        null=True,
    )

    blood_pressure = models.IntegerField(
        '最高/最低血圧',
        choices=ALLOW_CHOICES,
        null=True,
    )

    edema = models.IntegerField(
        '浮腫',
        choices=ALLOW_CHOICES,
        null=True,
    )

    urinary_protein = models.IntegerField(
        '尿蛋白',
        choices=ALLOW_CHOICES,
        null=True,
    )

    urinary_sugar = models.IntegerField(
        '尿糖',
        choices=ALLOW_CHOICES,
        null=True,
    )

    cervical_length = models.IntegerField(
        '頚管長',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # Child
    estimated_weight = models.IntegerField(
        '推定体重',
        choices=ALLOW_CHOICES,
        null=True,
    )

    presentation = models.IntegerField(
        '胎位',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # Location
    location_24h = models.IntegerField(
        '発災の24時間負けら現在までの位置情報',
        choices=ALLOW_CHOICES,
        null=True,
    )

    location_after_occurrence = models.IntegerField(
        '発災後から現在までの位置情報',
        choices=ALLOW_CHOICES,
        null=True,
    )

    location_all = models.IntegerField(
        '過去記録されたすべての位置情報',
        choices=ALLOW_CHOICES,
        null=True,
    )

    # 共有相手
    prefecture_disaster_medical_coordinator = models.IntegerField(
        '都道府県災害医療コーディネーター',
        choices=ALLOW_CHOICES,
        null=True,
    )

    area_disaster_medical_coordinator = models.IntegerField(
        '地域災害医療コーディネーター',
        choices=ALLOW_CHOICES,
        null=True,
    )

    insurance_medical_activity_team = models.IntegerField(
        '保険医療活動チーム',
        choices=ALLOW_CHOICES,
        null=True,
    )

    disaster_medical_volunteer_team = models.IntegerField(
        '災害医療ボランティアチーム',
        choices=ALLOW_CHOICES,
        null=True,
    )

    local_government_stuff = models.IntegerField(
        '地方自治体の職員など',
        choices=ALLOW_CHOICES,
        null=True,
    )

    obstetric_medical_support_liaison_member = models.IntegerField(
        '小児周産期リエゾンメンバー',
        choices=ALLOW_CHOICES,
        null=True,
    )
