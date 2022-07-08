from django.db import models

from django.contrib.auth.models import User

class Directory(models.Model):
    new_flag = models.BooleanField(default=True)
    name = models.CharField(max_length = 255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank=True)
    availabilityFlag = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    creation_date = models.DateField(auto_now_add = True)
    timestamp = models.DateField(auto_now = True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    validity_flag = models.BooleanField(default=True)
    def __str__(self):
        current_dir = self
        parents_list = []
        while current_dir.parent != None:
            parents_list.append(current_dir)
            current_dir = current_dir.parent
        path = ""
        for p in reversed(parents_list):
            path += "/"+p.name
        if path == "":
            path = "/"    
        return path


class File(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_field = models.FileField(upload_to = 'user1')
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add = True)
    timestamp = models.DateField(auto_now = True)
    availabilityFlag = models.BooleanField(default=True)
    result_text = models.TextField(blank=True)
    validity_flag = models.BooleanField(default=True)
    def getlines(self):
        self.file_field.open('r')
        return self.file_field.read()    
    def set_text(self, new_text):
        with open(self.file_field.path, "w") as myfile:
            myfile.write(new_text)


class SectionCategory(models.Model):
    category = models.CharField(max_length=30)
    parent = models.ForeignKey('self', blank=True,  null=True, on_delete=models.CASCADE)
    timestamp = models.DateField(auto_now = True)
    validity_flag = models.BooleanField(default=True)



class SectionStatus(models.Model):
    status = models.CharField(max_length=30, blank=True)
    timestamp = models.DateField(auto_now = True)
    validity_flag = models.BooleanField(default=True)



class StatusData(models.Model):
    validity_flag = models.BooleanField(default=True)
    timestamp = models.DateField(auto_now = True)    
    prover_name = models.CharField(max_length=30, blank=True)
    status_data = models.TextField(blank=True)
    


class FileSection(models.Model):
    name = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add = True)
    timestamp = models.DateField(auto_now = True)
    validity_flag = models.BooleanField(default=True)
    ref_file = models.ForeignKey(File, on_delete=models.CASCADE)
    ref_category = models.OneToOneField(SectionCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    ref_status = models.OneToOneField(SectionStatus, on_delete=models.DO_NOTHING, null=True, blank=True)
    ref_status_data = models.OneToOneField(StatusData, on_delete=models.DO_NOTHING, null=True, blank=True)
    line_nr = models.IntegerField(default=0)
    def delete(self, *args, **kwargs):
        self.ref_category.delete()
        self.ref_status.delete()
        self.ref_status_data.delete()
        return super(self.__class__, self).delete(*args, **kwargs)
