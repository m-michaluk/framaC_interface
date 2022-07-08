from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import Http404,HttpResponseNotFound
from django.contrib.auth.decorators import login_required

# Create your views here.
import subprocess
import re
from subprocess import Popen



from .forms import UploadFileModelForm
from .forms import AddDirectoryModelForm
from .models import File
from .models import Directory
from .models import SectionStatus
from .models import SectionCategory
from .models import StatusData
from .models import FileSection
from .models import User

from .forms import VCForm




def get_family_tree(directory):
    children = directory.directory_set.all() # dostaje wszystkie które referensują mój directory
    files_inside = directory.file_set.all()
    if not children:
        # this person has no children, recursion ends here
        return {'dir': directory, 'children': [], 'files': files_inside,}

    # this person has children, get every child's family tree
    return {
        'dir': directory,
        'children': [get_family_tree(child) for child in children],
        'files': files_inside,
    }


def add_sections(obj):
    names = {
        "loop invariant" : "Loop invariant",
        "requires" : "Pre-condition",
        "ensures" : "Post-condition",
        "predicate" : "Predicate",
        "assert" : "Assertion",
    }
    regex_str = "(loop invariant|requires|ensures|predicate|assert)"

    description = ""
    section_object = None
    with obj.file_field.open('r'):
        line_count = 1
        lines = obj.file_field.readlines()
        for line in lines:
            if re.search("@", line):
                match = re.sub("^.*@ ", "", line)
                result = re.search(regex_str, match)
                if result: # match between the line and one of the section categories
                    category = names[result.group(1)]
                    category_object = SectionCategory(
                        category = category,
                    )
                    category_object.save()
                    if section_object is not None:
                        section_object.save()

                    section_object = FileSection(
                        line_nr = line_count,
                        description = line, # cała linijka jest na razie desc, potem będziemy dodawać
                        ref_category = category_object,
                        ref_file = obj,
                        ref_status = SectionStatus.objects.create(),
                        ref_status_data = StatusData.objects.create(),
                    )
                    section_object.save()
                else:
                    if section_object != None:
                        section_object.description += line
            line_count += 1


def file_upload_view(request):
    if request.method == "POST":
        form = UploadFileModelForm(request.POST, request.FILES, owner=request.user)
        if form.is_valid():
            obj = form.save()
            add_sections(obj)
        else:
            print(form.errors)    
    form = UploadFileModelForm(owner=request.user)

    return render(request, 'my_app/upload_file.html', {'form':form})    


def dir_add_view(request):
    if request.method == "POST":
        form = AddDirectoryModelForm(request.POST, owner=request.user)
        if form.is_valid():
            obj = form.save()
            obj.owner = request.user
            obj.save()
        else:
            print(form.errors)    
    form = AddDirectoryModelForm(owner=request.user)

    return render(request, 'my_app/dir_add.html', {'form':form})    


def hide_children(dir):
    child_dirs = Directory.objects.filter(parent=dir)
    for child in child_dirs:
        child.availabilityFlag = False
        child.save()
        hide_children(child)

def file_delete_view(request):
    if request.is_ajax and request.method == "POST":
        to_delete = request.POST.get('to_delete')
        l = to_delete.split()
        if l[0] == "dir":
            p_key = l[1]
            to_delete = get_object_or_404(Directory, pk=p_key)
            to_delete.availabilityFlag = False
            to_delete.save()
            hide_children(to_delete)
        elif l[0] == "file":
            p_key = l[1]
            to_delete = File.objects.get(pk=p_key)
            to_delete.availabilityFlag = False
            to_delete.save()
        root_dir = Directory.objects.filter(owner=request.user).filter(parent=None).first()    
        tree = get_family_tree(root_dir) #root directory
        return render(request, 'my_app/show_files.html', {'tree':tree,})
    return HttpResponseNotFound("Page not found")

def choose_file_view(request):
    context = {}
    if request.is_ajax and request.method == "POST":
        file_id = request.POST.get('file_id')
        current_file = get_object_or_404(File, pk=file_id)
        request.session['file_id'] = file_id
        code_field = render_to_string('my_app/display_file.html', {'file' : current_file, 'text_field': current_file.getlines()})
        right_field = right_field_string(request, file_id)
        if 'tab_nr' in request.session:
            return JsonResponse({'code_field': code_field, 'right_field': right_field, 'result_tab': True, 'result_text': current_file.result_text})
        return JsonResponse({'code_field': code_field, 'result_tab':False, 'right_field': right_field})
    return HttpResponseNotFound("Page not found")


def right_field_string(request, file_id):
    current_file = get_object_or_404(File, pk=file_id)
    context = {'file' : current_file}
    return render_to_string('my_app/focus_on_program_elements.html', context) 


def run_view(request):          
    if request.is_ajax and request.method == "POST" and 'run' in request.POST and 'file_id' in request.session:
        run_frama(request)
        file_id = request.session['file_id']
        current_file = get_object_or_404(File, pk=file_id)
        right_field = right_field_string(request, file_id)
        if 'tab_nr' in request.session:
            return JsonResponse({'right_field': right_field, 'result_tab': True, 'result_text': current_file.result_text})
        return JsonResponse({'result_tab':False, 'right_field': right_field})   
    return HttpResponseNotFound("Page not found")


def safe_file_view(request):
    if request.is_ajax and request.method == "POST" and 'save' in request.POST and 'file_id' in request.session and 'text' in request.POST:
        file_id = request.session['file_id']
        new_text = request.POST['text']
        current_file = get_object_or_404(File, pk=file_id)
        current_file.set_text(new_text)
        return JsonResponse({})

    return HttpResponseNotFound("Page not found")



def set_file(request):
    file_pk = None
    current_file = None
    if request.method == "POST":
        if 'file_id' in request.POST:
            file_pk = request.POST['file_id'] # pk pliku ktory ma byc wyswietlany
        elif 'file_id' in request.session:
            file_pk = request.session['file_id']
    elif request.method == "GET":
        if 'file_id' in request.session:
            file_pk = request.session['file_id']
    if file_pk != None:
        if File.objects.filter(pk=file_pk).exists():
            current_file = File.objects.get(pk=file_pk)

    request.session['file_id'] = file_pk        
    return {'file': current_file}


def run_frama(request):
    file_pk = request.session['file_id']
    if file_pk != None:
        file_obj = File.objects.get(pk=file_pk)
        default_option = ["-wp", "-wp-print", "-wp-log=r:result.txt"]
        prover_option = ["-wp-prover"]+[request.session['prover'].lower()]
        settings = request.session['vcs_settings']+[file_obj.file_field.path]
        args = default_option + prover_option + settings
        p = Popen(["frama-c"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, errors = p.communicate()
        result = open('result.txt', 'r')
        file_obj.result_text = result.read()
        file_obj.save()

        sections = FileSection.objects.filter(ref_file=file_pk)
        matches = re.split("[\-]+\n", output)

        for section in sections:
            section.validity_flag = False

        for m in matches:
            #sprawdzam czy pierwsza linia zaczyna się od Goal
            first_line = re.search("^\nGoal.*\n", m)
            if first_line != None:
                line_nr = re.search("line \d+", first_line.group(0)).group(0)
                if line_nr == None:
                    continue
                line_nr = int(line_nr.split()[1])

                sec = next((x for x in sections if x.line_nr == line_nr), None)
                if sec == None:
                    continue
                m = m.split('\n', 2)[2] # usuwam dwie pierwsze linie (newline na poczatku i ta z Goal)

                status_line = re.findall("Prover ([^ ]*) returns ([a-zA-Z]*).*\n", m)
                if not status_line:
                    continue
                m = m.rsplit("\n", 3)[0] # usuwam 3 ostatnie linie (newliny i z status)
                sec.ref_status_data.status_data = m
                sec.ref_status_data.prover_name = status_line[0][0]
                sec.ref_status_data.save()
                sec.ref_status.status = status_line[0][1].lower()
                sec.ref_status.save()
                sec.validity_flag = True
                sec.save()


def set_tabs_value(request):
    prover = "Alt-Ergo"
    provers_list = ["Alt-Ergo", "Z3", "CVC4"]
    vcs_settings = []
    if request.method == "POST":
        if 'save_prover' in request.POST:
            prover = request.POST['prover']
            request.session['prover'] = prover
        elif 'save_vcs' in request.POST:
            vcs_form = VCForm(request.POST)
            if vcs_form.is_valid():
                vcs_settings = request.POST.getlist('vcs')
                request.session['vcs_settings'] = vcs_settings
            else:
                return HttpResponseBadRequest()

    if 'prover' in request.session:
        prover = request.session['prover']
    if 'vcs_settings' in request.session:
        vcs_settings = request.session['vcs_settings']
    request.session['prover'] = prover
    request.session['vcs_settings'] = vcs_settings

    vcs_form = VCForm()
    vcs_form.fields['vcs'].initial = vcs_settings

    

    ctx = {
        'provers_list': provers_list,
        'vcform' : vcs_form,
    }
    return ctx
    

def set_tabs_nr(request):
    tab_nr = "1"
    if request.method == "POST":
        if 'tab_nr' in request.POST:
            tab_nr = request.POST['tab_nr']
        elif 'tab_nr' in request.session:
            tab_nr = request.session['tab_nr']
    elif request.method == "GET":
        if 'tab_nr' in request.session:
            tab_nr = request.session['tab_nr']
    request.session['tab_nr'] = tab_nr
    return {'tab_nr': tab_nr}


#zwraca dictionary zawierający klucze:
# 'file' - plik który ma być aktualnie wyświetlany
# 'text_field' - lista lini pliku który ma być wyświetlany
# 'tree' dictionary służący do wypisywania drzewa katalogów
# 'tab_nr' - numer tab'a, który ma być wyświetlany
# 'tab_value' - zawartość taba (dictionary)
@login_required
def home_view(request):
    context = {}
    #generowanie drzewa plików i katalogów
    root_dir = Directory.objects.filter(owner=request.user).filter(parent=None).first()
    tree = get_family_tree(root_dir) #root directory
    context.update({'tree' : tree})

    context.update(set_file(request))
    if context['file'] != None:
        context.update(
                        {
                        'text_field': context['file'].getlines(),
                        'result_text' : context['file'].result_text,
                        }
                    )

    context.update(set_tabs_nr(request))
    context.update(set_tabs_value(request))

    return render(request, 'index.html', context)
