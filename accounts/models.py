from django.db import models
from django.contrib.auth.models import User, Group


class Salutation(models.Model):
    salutation = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.salutation


class Vertical(models.Model):
    vertical = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.vertical


class Focus_Segment(models.Model):
    focus_segment = models.CharField(max_length=255)
    vertical = models.ForeignKey(Vertical, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.focus_segment


class Market_Segment(models.Model):
    market_segment = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.market_segment


class Tag(models.Model):
    tag = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.tag


class Contact_Status(models.Model):
    status = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.status


class Stage(models.Model):
    stage = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    probability = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.stage


class Log_Stage(models.Model):
    stage = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.stage


class Country(models.Model):
    country_name = models.CharField(max_length=255)
    currency_short = models.CharField(max_length=15, null=True, blank=True)
    currency_full = models.CharField(max_length=55, null=True, blank=True)
    currency_active = models.BooleanField(default=False)
    country_code = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.country_name


class State(models.Model):
    state_name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.state_name

class City(models.Model):
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.city_name
    
class Lead_Source(models.Model):
    source = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.source

class Lead_Source_From(models.Model):
    source = models.ForeignKey(Lead_Source, on_delete=models.CASCADE,null=True, blank=True)
    source_from = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.source_from
    
class User_Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.group.name}'
    

class Teams(models.Model):
    bdm_user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="bdm_user")
    bde_user = models.ManyToManyField(User,related_name="bde_user") 

    def __str__(self):
        return f"BDE - {', '.join([user.username for user in self.bde_user.all()])} under BDM - {self.bdm_user.username}"