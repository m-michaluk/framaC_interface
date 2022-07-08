from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.test import Client
from django.db.models import FileField

# Create your tests here.

from . import models

from . import views

from . import forms


# tests for all models:
# 1. Directory
# 2. File
# 3. SectionCategory
# 4. SectionStatus
# 5. StatusData
# 6. FileSection
# 7. User

def create_temp_file(content):
    temp = models.Directory.objects.create(name="temp", parent=None)
    simple_file = SimpleUploadedFile("test.txt", content)
    file_obj = models.File.objects.create(name="TestFile", parent=temp, file_field=simple_file)
    return file_obj, simple_file

def create_test_user():
    test_user = models.User(username='hOoqi9nZY3rSSru', password='Password1234')
    test_user.save()
    return test_user

class DirectoryModelTests(TestCase):
    def test_correct_to_string_root_dir(self):
        root_dir = models.Directory(name="root", parent=None)
        self.assertEquals(str(root_dir), "/")


class FileModelTests(TestCase):
    def test_getlines(self):
        temp, simple_file = create_temp_file(b'Ala ma kota\na kot ma Ale\n')
        self.assertEquals(temp.getlines(), 'Ala ma kota\na kot ma Ale\n')
        os.remove(temp.file_field.path)


class SectionCategoryModelTests(TestCase):
    def test_category_exists_with_correct_name(self):
        temp, simple_file = create_temp_file(b'/* @ ensures Sorted(t,0,n-1); */ \n')
        views.add_sections(temp)
        self.assertEquals(models.SectionCategory.objects.count(), 1)
        self.assertEquals(models.SectionCategory.objects.first().category, "Post-condition")
        os.remove(temp.file_field.path)


    # usunięcie filesection usuwa section category
    def test_cascade_delete_section_category(self):
        temp, simple_file = create_temp_file(b'/* @ ensures Sorted(t,0,n-1); */ \n')
        views.add_sections(temp)
        self.assertEquals(models.SectionCategory.objects.count(), 1)
        self.assertEquals(models.FileSection.objects.count(), 1)
        sec = models.FileSection.objects.first()
        sec.delete()
        self.assertEquals(models.SectionCategory.objects.exists(), False)
        os.remove(temp.file_field.path)


class SectionStatusModelTests(TestCase):
   
   # nowododane FileSection referensuje puste (i nie None) SectionStatus 
    def test_new_file_section_has_empty_section_status(self):
        temp, simple_file = create_temp_file(b'/* @ ensures Sorted(t,0,n-1); */ \n')
        views.add_sections(temp)
        self.assertEquals(models.FileSection.objects.count(), 1)
        sec = models.FileSection.objects.first()
        self.assertIsNotNone(sec.ref_status)
        self.assertEquals(sec.ref_status.status, "")
        os.remove(temp.file_field.path)


class StatusDataModelTests(TestCase):
    # usunięcie filesection usuwa status data
    def test_on_delete_filesection_delete_status_data(self):
        temp, simple_file = create_temp_file(b'/* @ ensures Sorted(t,0,n-1); */ \n')
        views.add_sections(temp)
        self.assertEquals(models.FileSection.objects.count(), 1)
        self.assertEquals(models.StatusData.objects.exists(), True)
        sec = models.FileSection.objects.first()
        self.assertIsNotNone(sec.ref_status_data)
        sec.delete()
        self.assertEquals(models.StatusData.objects.exists(), False)
        os.remove(temp.file_field.path)


class FileSectionModelTests(TestCase):
    def test_no_filesections_for_not_ACSL_file(self):
        temp, simple_file = create_temp_file(b'Na pewno nie ACSL\nAla ma kota\nKot')
        views.add_sections(temp)
        filesections = models.FileSection.objects.exists()
        self.assertEquals(filesections, False)
        os.remove(temp.file_field.path)

    # usunięcie pliku usuwa jego file sections
    def test_cascade_delete_filesection(self):
        temp, simple_file = create_temp_file(b'/* @ ensures Sorted(t,0,n-1); */ \n')
        views.add_sections(temp)
        self.assertEquals(models.FileSection.objects.exists(), True)
        temp.delete()
        self.assertEquals(models.FileSection.objects.exists(), False)
        os.remove(temp.file_field.path)      
    


class UserModelTests(TestCase):
    def test_adding_root_dir_after_create(self):
        test_user = create_test_user()
        root_dir = models.Directory.objects.filter(owner=test_user)
        self.assertEquals(root_dir.count(), 1) # po zapisaniu usera istnieje jeden jego folder
        self.assertEquals(root_dir.first().parent, None) # ten folder nie ma rodzica
    def test_login(self):
        user = models.User.objects.create(username='testuser')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testuser', password='12345')
        self.assertTrue(logged_in)  


# Tests for Forms :
# 1. UploadFileModelForm
# 2. UploadDirectoryModelForm
# 3. VCForm

class UploadFileModelFormTests(TestCase):
    def test_upload_file_is_valid(self):
        test_user = create_test_user()
        file, field = create_temp_file(b'aaaaaaa')
        test_dir = models.Directory.objects.filter(owner=test_user).first()
        test_data = {
            'name' : 'test_file',
            'description' : 'ghgh',
            'parent' : test_dir,

        }
        form_data = forms.UploadFileModelForm(test_data, {'file_field': field}, owner = test_user)
        self.assertTrue(form_data.is_valid())
        os.remove(file.file_field.path)      


    # Podany folder nie jest folderem usera
    def test_upload_file_is_not_valid(self):
        test_user = create_test_user()
        file, field = create_temp_file(b'aaaaaaa')
        test_dir = models.Directory.objects.create(name="test_dir", parent=None, owner=None)
        test_data = {
            'name' : 'test_file',
            'description' : 'test',
            'parent' : test_dir,
        }
        form_data = forms.UploadFileModelForm(test_data, {'file_field': field}, owner = test_user)
        self.assertFalse(form_data.is_valid())
        os.remove(file.file_field.path)      



class AddDirectoryModelFormTests(TestCase):
    def test_add_directory_is_valid(self):
        test_user = create_test_user()
        test_dir = models.Directory.objects.filter(owner=test_user).first()
        test_data = {
            'name' : "Test Dir",
            'description' : 'test',
            'parent' : test_dir,
        }
        form = forms.AddDirectoryModelForm(test_data, owner=test_user)
        self.assertTrue(form.is_valid())

    # parent_directory nie może być None
    def test_add_directory_is_not_valid(self):
        test_user = create_test_user()
        test_data = {
            'name' : "Test Dir",
            'description' : 'test',
            'parent' : None,
        }
        form = forms.AddDirectoryModelForm(test_data, owner=test_user)
        self.assertFalse(form.is_valid())



class VCFormTests(TestCase):
    def test_vc_form_is_valid(self):
        form = forms.VCForm({'-wp-rte' : '-wp-rte'})
        self.assertTrue(form.is_valid())

    def test_vc_form_is_valid_no_choices(self):
        form = forms.VCForm({})
        self.assertTrue(form.is_valid())


# Tests for all Views :
# 1. file_upload_view
# 2. dir_add_view
# 3. file_delete_view
# 4. choose_file_view
# 5. run_view
# 6. home_view

def create_logged_in_client():
    user = models.User.objects.create(username='testuser')
    user.set_password('12345')
    user.save()
    c = Client()
    c.login(username='testuser', password='12345')
    return c, user

class FileUploadViewTests(TestCase):
    def test_basic(self):
        test_client = create_logged_in_client()
        response = test_client[0].get(reverse('upload_file'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_post(self):
        test_client, test_user = create_logged_in_client()
        file, field = create_temp_file(b'test')
        test_dir = models.Directory.objects.filter(owner=test_user).first()
        response = test_client.post(
            reverse('upload_file'),
            data={
                'name': 'test_file',
                'file_field': file.file_field,
                'parent': test_dir.pk,
                'content_type' :'multipart/form-data'
            },
        )
        self.assertEqual(response.status_code, 200)
        # sprawdz czy plik zostal poprawnie dodany
        added_files = test_dir.file_set.all()
        self.assertEquals(added_files.count(), 1)
        added_file = added_files.first()
        self.assertEquals(added_file.name, 'test_file')
        self.assertEquals(added_file.parent, test_dir)
        os.remove(file.file_field.path)    
        os.remove(added_file.file_field.path)  




class DirAddViewTests(TestCase):
    def test_basic(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.get(reverse('add_dir'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_post(self):
        test_client, test_user = create_logged_in_client()
        test_dir = models.Directory.objects.filter(owner=test_user).first()
        response = test_client.post(
            reverse('add_dir'),
            data={
                'name': 'test_dir',
                'parent': test_dir.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        # sprawdz czy folder zostal poprawnie dodany
        dirs = models.Directory.objects.all()
        self.assertEquals(dirs.count(), 2)
        test_dirs = models.Directory.objects.filter(name='test_dir')
        self.assertEquals(test_dirs.count(), 1)
        added_dir = test_dirs.first()
        self.assertTrue(added_dir.name, 'test_file')
        self.assertEquals(added_dir.parent, test_dir)


# JQuery
class FileDeleteView(TestCase):
    def test_request_must_be_post(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.get(reverse('delete_file'))
        self.assertEquals(response.status_code, 404)

    def test_post_file_not_visible(self):
        test_client, test_user = create_logged_in_client()
        temp_file_pk = create_temp_file(b'TestContent')[0].pk
        # usuwam plik temp_file
        response = test_client.post(
            reverse('delete_file'),
            data={
                'to_delete': 'file '+str(temp_file_pk),
            },
        )
        self.assertEquals(response.status_code, 200)
        temp_file = models.File.objects.get(pk=temp_file_pk)
        self.assertFalse(temp_file.availabilityFlag)
        os.remove(temp_file.file_field.path)


# Jquery
class ChooseFileView(TestCase):
    def test_request_must_be_post(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.get(reverse('choose_file'))
        self.assertEquals(response.status_code, 404)

    def test_post(self):
        test_client, test_user = create_logged_in_client()
        temp_file_pk = create_temp_file(b'TestContent')[0].pk
        response = test_client.post(
            reverse('choose_file'),
            data={
                'file_id': str(temp_file_pk),
            },
        )
        self.assertEquals(response.status_code, 200)
        self.assertIn('file_id', test_client.session)
        temp_file = models.File.objects.get(pk=temp_file_pk)
        os.remove(temp_file.file_field.path)      



# Jquery
class RunView(TestCase):
    def test_request_must_be_post(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.get(reverse('run_frama'))
        self.assertEquals(response.status_code, 404)


    def test_post(self):
        test_client, test_user = create_logged_in_client()
        temp_file, simple_file = create_temp_file(b'TestContent')
        views.add_sections(temp_file)
        s = test_client.session
        s.update({
            "file_id": temp_file.pk,
            "prover" : "Alt-Ergo",
            "vcs_settings" : []
        })
        s.save()
        response = test_client.post(
            reverse('run_frama'),
            data={
                'run': "Run",
            },
        )
        self.assertEquals(response.status_code, 200)
        os.remove(temp_file.file_field.path)      



class HomeView(TestCase):
    def test_basic_get(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.get(reverse('home'))
        self.assertEquals(response.status_code, 200)

    def test_context_get(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.get(reverse('home'))
        self.assertIn('tree', response.context)
        self.assertIn('file', response.context)
        self.assertIn('provers_list', response.context)
        self.assertIn('vcform', response.context)
        self.assertIn('vcs_settings', test_client.session)
        self.assertIn('prover', test_client.session)
   
    def test_post_tabs_prover(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.post(
            reverse('home'),
            data={
                'save_prover': "Save",
                'prover' : "Alt-Ergo",
            },
        )
        self.assertEquals(response.status_code, 200)
        self.assertIn('prover', test_client.session)


    def test_post_tabs_vcs(self):
        test_client, test_user = create_logged_in_client()
        response = test_client.post(
            reverse('home'),
            data={
                'save_vcs': "Save",
                'vcs' : ['-wp-rte'],
            },
        )
        self.assertEquals(response.status_code, 200)
        self.assertIn('vcs_settings', test_client.session)   
        self.assertIn('-wp-rte', test_client.session['vcs_settings'])


