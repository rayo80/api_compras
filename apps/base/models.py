from django.db import models

from simple_history.models import HistoricalRecords


# Create your models here.
class BaseModel(models.Model):
    """Model definition for BaseModel."""
    id = models.AutoField(primary_key=True)
    state = models.BooleanField('Estado', default=True)
    created_date = models.DateField('Fecha de creacion', auto_now=False, auto_now_add=True)
    modified_date = models.DateField('Fecha de Modificacion', auto_now=True, auto_now_add=False)
    deleted_date = models.DateField('Fecha de Eliminacion', auto_now=True, auto_now_add=False)
    historical = HistoricalRecords(user_model="users.User", inherit=True)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        """Meta definition for BaseModel."""
        abstract = True
        verbose_name = 'BaseModel'
        verbose_name_plural = 'BaseModels'
