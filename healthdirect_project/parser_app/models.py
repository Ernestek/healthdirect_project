from django.db import models


class Info(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=512, null=True, blank=True)
    phone = models.CharField(max_length=256, null=True, blank=True)
    practitioner_name = models.CharField(max_length=256, null=True, blank=True)
    practitioner_profession = models.CharField(max_length=256, null=True, blank=True)
    practitioner_sex = models.CharField(max_length=256, null=True, blank=True)
    practitioner_lang = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = 'Info'
        verbose_name_plural = 'Info'
        unique_together = ['name', 'practitioner_name']
