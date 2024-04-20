import sys

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import spacy
from spacy.training.example import Example
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import UploadedFile
import random
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import subprocess
import json
from .models import ModelName, TrainedModel
from django.core.files import File
from django.contrib import messages
import os
global textotal
global settags
settags =[]
def file_upload(request): ## This function is for unloading file by user
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = FileUploadForm()
    return render(request, 'file_upload.html', {'form': form})

def file_upload2(request): ## This function is for unloading file by user
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['file'].read().decode('utf-8')
            text = file_content
            unique_entity_labels=tags
            settags.extend(unique_entity_labels)
            return render(request, 'display_file_content2.html',
                          {'file_content': file_content, 'unique_entity_labels': unique_entity_labels})

    else:
        form = FileUploadForm()
    return render(request, 'file_upload2.html', {'form': form})
def file_upload3(request): ## This function is for unloading file by user
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['file'].read().decode('utf-8')
            text = file_content
            model_path = f"./nlp/models/{model_name}/model-best"
            original_file_path = f"./nlp/models/{model_name}/annotations.json"
            with open(original_file_path, "r") as f:
                json_data = json.load(f)
            settags = json_data['classes']
            if os.path.exists(model_path):
                print(model_path)
                nlp = spacy.load(model_path)
                doc = nlp(text)
                print("I ma Heir")
                unique_entity_labels = list(set(ent.label_ for ent in doc.ents))
                context = {'file_content': file_content, 'unique_entity_labels': settags }

                return render(request, 'framing.html', context)
            else:
                return render(request, 'display_file_content2.html',
                              {'file_content': file_content, 'unique_entity_labels':settags})

    else:
        form = FileUploadForm()
    return render(request, 'file_upload3.html', {'form': form})
def file_list(request):
    files = UploadedFile.objects.all()
    return render(request, 'file_list.html', {'files': files})


from django.shortcuts import render, HttpResponse
from .models import UploadedFile  # Make sure to import your UploadedFile model


def display_last_file(request):  # This function is for displaying file on the web
    # if file_name is None:
    try:
        file_name = request.GET.get('file_name')
    except:
        pass

    if file_name:
        try:
            # Get the UploadedFile object corresponding to the given file name
            uploaded_file = UploadedFile.objects.get(file=file_name)
            file_content = uploaded_file.file.read().decode('utf-8')
        except UploadedFile.DoesNotExist:
            messages.error(request, f'The file "{file_name}" does not exist.')
    else:
        try:
            uploaded_file = UploadedFile.objects.last()
            file_content = uploaded_file.file.read().decode('utf-8')
        except UploadedFile.DoesNotExist:
            messages.error(request,f'The file does not exist.')
    global text
    text = file_content

    model_path = f"./nlp/models/{model_name}/model-best"
    if os.path.exists(model_path):
        nlp = spacy.load(model_path)
        doc = nlp(text)
        unique_entity_labels = list(set(ent.label_ for ent in doc.ents))
        settags.extend(unique_entity_labels)
        def get_random_color():
            letters = '0123456789ABCDEF'
            color = '#'
            for _ in range(6):
                color += random.choice(letters)
            return color
        def assign_colors_to_tags(tags):
            colored_tags = {}
            for tag in tags:
                colored_tags[tag] = get_random_color()
            return colored_tags
        colors = assign_colors_to_tags(unique_entity_labels)
        options = {"colors": colors}

        # html_paragraphs = spacy.displacy.render(doc, style="ent", options=options).split('\n\n')

        # return render(request, 'display_file_content2.html',
        #               {'file_content': file_content, 'unique_entity_labels': unique_entity_labels},'framing.html')

        context = {'file_content': file_content, 'unique_entity_labels': unique_entity_labels}

        return render(request, 'framing.html', context)
    else:
        return render(request, 'display_file_content.html', {'file_content': file_content})



def delete_file(request): ## Deleting the file which is uploaded previously
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        try:
            # Get the UploadedFile object corresponding to the given file name
            uploaded_file = UploadedFile.objects.get(file=file_name)
            uploaded_file.delete()
            os.remove(f'./{file_name}')
            messages.success(request, f'The file "{file_name}" has been deleted.')
        except UploadedFile.DoesNotExist:
            messages.error(request, f'The file "{file_name}" does not exist.')
    return redirect('file_list')


import os
def trainmodel(request):
    nlp = spacy.blank("hi")
    db = DocBin()
    original_file_path = f"./nlp/models/{model_name}/annotations.json"
    with open(original_file_path, "r") as f:
        TRAIN_DATA = json.load(f)
    for text, annot in tqdm(TRAIN_DATA['annotations']):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot["entities"]:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)

    db.to_disk("./training_data.spacy")

    python_path = sys.executable
    print(f"Python Interpreter Path: {python_path}")
    init_command = [python_path, "-m", "spacy", "init", "config", "config.cfg", "--lang", "en", "--pipeline", "ner", "--optimize", "efficiency"]
    subprocess.run(init_command, shell=False)
    train_command = [python_path, "-m", "spacy", "train", "config.cfg", "--output", f"./nlp/models/{model_name}", "--paths.train", "./training_data.spacy", "--paths.dev", "./training_data.spacy"]
    subprocess.run(train_command, shell=False)

    return render(request, 'train.html')





global classes
global main
classes = []
main = []
def process_data(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        for key, val in data.items():
            classes.append(val)
        print(classes)
        last_file = UploadedFile.objects.last()

        if last_file:
            file_content = last_file.file.read().decode('utf-8')
            # words=file_content.split(' ')

            sentences = file_content.split('.')
            for i in range(0, len(sentences)):
                sentences[i] = sentences[i].split('\r\n')
            fin = ''
            start_idx = 0
            end_idx = 0
            for s in sentences:

                for sentence in s:
                    final = []
                    words = sentence.split(' ')
                    temp = []

                    for word in words:
                        end_idx += len(word) + 1
                        if word in data:
                            # print(word)
                            temp.append([start_idx - 1, end_idx - 1, data[word]])

                        start_idx = end_idx

                    if len(temp) > 0:
                        dic = {"entities": temp}
                        sentence = fin + sentence
                        final.append(sentence)
                        fin = ''
                        start_idx = 0
                        end_idx = 0
                        final.append(dic)
                        main.append(final)
                    else:
                        if len(fin) == 0:
                            fin = fin + sentence
                            start_idx = len(fin)
                            end_idx = len(fin)
                        else:
                            fin = fin + '.' + sentence
                            start_idx = len(fin) + 1
                            end_idx = len(fin) + 1
            #
            # annotations = {'classes': list(set(classes)),
            #                'annotations': main}

            global tags
            tags=list(set(classes))

            existing_model_path = f"nlp/models/{model_name}"
            output_path = os.path.join(existing_model_path, "annotations.json")

            # Create or update the annotations
            if os.path.exists(output_path):
                # Load existing annotations
                with open(output_path, "r") as infile:
                    existing_annotations = json.load(infile)

                # Update existing annotations with new data
                existing_annotations['annotations'].extend(main)
                existing_annotations['classes'] = list(set(existing_annotations['classes'] + classes))

                json_object = json.dumps(existing_annotations)
            else:
                # Create a new annotations file
                annotations = {'classes': list(set(classes)), 'annotations': main}
                json_object = json.dumps(annotations)

                # Create the directory if it doesn't exist
                os.makedirs(existing_model_path, exist_ok=True)

            # Write the JSON to the file
            with open(output_path, "w") as outfile:
                outfile.write(json_object)

        return JsonResponse({'message': 'Data received successfully.'})
    else:
        return JsonResponse({'error':'Invalid request method.'})
    

def showtagstext(request):
    model=f"./nlp/models/{model_name}/model-best"
    nlp = spacy.load(model)
    doc = nlp(text)
    main=[]
    classes=[]

    unique_entity_labels = list(set(ent.label_ for ent in doc.ents))

    def get_random_color():
        letters = '0123456789ABCDEF'
        color = '#'
        for _ in range(6):
            color += random.choice(letters)
        return color

    def assign_colors_to_tags(tags):
        colored_tags = {}
        for tag in tags:
            colored_tags[tag] = get_random_color()
        return colored_tags

    colors = assign_colors_to_tags(unique_entity_labels)
    print(colors)
    options = {"colors": colors}


    html = spacy.displacy.render(doc, style="ent", options=options)
    return render(request, 'tagededtext.html', {'html': html})


def showmodel(request):
    model_names = os.listdir('./nlp/models')
    print(model_names)

    # You can categorize the models if needed
    categorized_models = {'All Models': model_names}

    context = {
                 'model_names': categorized_models,
          }

    return render(request, 'showmodel.html', context)


def storemodelname(request):
    global model_name  # Declare that you are using the global variable
    if request.method == 'GET':
        modelname = request.GET.get('model_name')
        model_name = modelname
        print(model_name)# Assign the value to the global variable
    return redirect('showmodel')
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def check_training_status(request):
    training_status = "Training in progress..."

    return render('train.html')

def fileuploadtoseeresult(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['file'].read().decode('utf-8')
            text = file_content
            return redirect('showtext')
    else:
        form = FileUploadForm()  # Create an instance of the form for GET requests
        return render(request, 'fileuploadtoseereslt.html', {'form': form})