from django.db import models

# Create your models here.
class Project(models.Model):

    class Meta:
        db_table = 'project'

    name = models.CharField(max_length=30, unique=True)
    root = models.TextField(max_length=1024)


class Blob(models.Model):

    class Meta:
        db_table = 'blob'

    path = models.TextField(max_length=1024, unique=True)
    checksum = models.CharField(max_length=64)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Ident(models.Model):

    class Meta:
        db_table = 'ident'

    value = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Def(models.Model):

    class Meta:
        db_table = 'def'

    ident = models.ForeignKey(Ident, on_delete=models.CASCADE)
    blob = models.ForeignKey(Blob, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    line = models.IntegerField()


class Ref(models.Model):

    class Meta:
        db_table = 'ref'

    ident = models.ForeignKey(Ident, on_delete=models.CASCADE)
    blob = models.ForeignKey(Blob, on_delete=models.CASCADE)
    line = models.IntegerField()
