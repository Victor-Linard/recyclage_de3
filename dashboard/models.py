from django.db import models
class Dechet(models.Model):
    ANNEE = models.IntegerField()
    C_REGION = models.IntegerField()
    L_REGION = models.CharField(max_length=255)
    C_DEPT = models.CharField(max_length=255)
    N_DEPT = models.CharField(max_length=255)
    C_TYP_REG_DECHET = models.CharField(max_length=255)
    L_TYP_REG_DECHET = models.CharField(max_length=255)
    TONNAGE_T = models.FloatField()
    VA_POPANNEE = models.IntegerField()
    RATION_KG_HAB = models.FloatField()
