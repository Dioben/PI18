import json

from django.contrib import auth
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
from app.forms import UploadModelFileForm, UploadDataSetFileForm, ConfSimForm, CustomUserCreationForm
from app.models import *


def index(request):
    if request.user.is_authenticated:
        return redirect('/simulations/')
    return render(request, 'index.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('/simulations/')
    return render(request, 'login.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('/simulations/')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return redirect('/simulations/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def simulation_list(request):
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = simulations(request)
    if type(response) == HttpResponse:
        return response
    t_parms = {
        'simulations': response,
        'notification': notification,
    }
    return render(request, 'simulations/simulations.html', t_parms)


def simulation_list_content(request):
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = simulations(request)
    if type(response) == HttpResponse:
        return response
    t_parms = {
        'simulations': response,
        'notification': notification,
    }
    return render(request, 'simulations/simulationsContent.html', t_parms)

def simulation_create(request):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", 403)
    if request.method == 'POST':
        response = simulations(request)
        if type(response) is HttpResponse:
            return response
        return redirect('/simulations/' + str(response.id.int))
    return render(request, 'simulationCreate.html', {'fileForm': UploadModelFileForm(), 'configForm': ConfSimForm()})


def simulation_info(request, id):
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    t_params = {
        'simulation': response,
        'notification': notification,
        'updates': Update.objects.filter(sim_id=id)
    }
    return render(request, 'simulationInfo/simulationInfo.html', t_params)


def simulation_info_content(request, id):
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    t_params = {
        'simulation': response,
        'notification': notification,
        'updates': Update.objects.filter(sim_id=id)
    }
    return render(request, 'simulationInfo/simulationInfoContent.html', t_params)


def simulation_info_context(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    # this is a mess but it works
    t_params = {
        'simulation': json.loads(django.core.serializers.serialize('json', [response, ]))[0],
        'updates': json.loads(django.core.serializers.serialize('json', Update.objects.filter(sim_id=id)))
    }
    return HttpResponse(json.dumps(t_params), 200)


def simulation_command(request, id, command):
    simName = Simulation.objects.get(id__exact=id).name
    response = command_simulation(request, command, id)
    if response.status_code == 200:
        sim = Simulation.objects.filter(id__exact=id, owner=request.user)
        if sim.exists():
            sim = sim.get()
            if not sim.isrunning:
                request.session['notification'] = "Simulation \""+simName+"\" has been paused."
                request.session.modified = True
                return redirect(request.META.get('HTTP_REFERER'))
            request.session['notification'] = "Simulation \""+simName+"\" has been resumed."
            request.session.modified = True
            return redirect(request.META.get('HTTP_REFERER'))
        request.session['notification'] = "Simulation \""+simName+"\" has been deleted."
        request.session.modified = True
        return redirect('/simulations/')
    return response


def post_sim(request):  # TODO: add a version that allows file upload for Dataset
    modelForm = UploadModelFileForm(request.POST, request.FILES)
    confForm = ConfSimForm(request.POST, request.FILES)
    if modelForm.is_valid() and confForm.is_valid():
        model = request.FILES['model']
        modeltext = b''
        for chunk in model.chunks():
            modeltext += chunk
        modeljson = json.loads(modeltext)
        # TODO: This is probably not what Silva wants
        biastext = "["
        for layer in modeljson['config']:
            if 'bias_initializer' in layer:
                biastext += f"{{{layer['bias_initializer']}}},"
            else:
                biastext += f"{{ }},"
        biastext += "]"

        sim = Simulation(owner=request.user,
                         isdone=False,
                         isrunning=True,
                         model=modeltext,
                         name=confForm.cleaned_data["name"],
                         layers=len(modeljson['config']['layers']),
                         biases=bytes(biastext, 'utf-8'),
                         epoch_interval=confForm.cleaned_data["logging_interval"],
                         goal_epochs=confForm.cleaned_data["max_epochs"],
                         learning_rate=confForm.cleaned_data["learning_rate"])
        sim.save()

        trainset = '/all_datasets/' + str(sim.id) + '-dataset_train.npz'
        if "test_dataset" in request.FILES:
            testset = '/all_datasets/' + str(sim.id) + '-dataset_test.npz'
            f = open(testset, 'wb+')
            for chunk in request.FILES['test_dataset'].chunks():
                f.write(chunk)
            f.close()
        else:
            testset = trainset
        f = open(trainset, 'wb+')
        for chunk in request.FILES['train_dataset'].chunks():
            f.write(chunk)
        f.close()

        valset = '/all_datasets/' + str(sim.id) + '-dataset_val.npz'
        f = open(valset, 'wb+')
        for chunk in request.FILES['val_dataset'].chunks():
            f.write(chunk)
        f.close()

        postdata = {
            "conf": {
                "id": str(sim.id.int),
                "dataset_train": trainset,
                "dataset_test": testset,
                "dataset_val": valset,
                "dataset_url": False,
                "batch_size": confForm.cleaned_data['batch_size'],
                "epochs": sim.goal_epochs,
                "epoch_period": sim.epoch_interval,
                "train_feature_name": "x_train",
                "train_label_name": "y_train",
                "test_feature_name": "x_test",
                "test_label_name": "y_test",
                "val_feature_name": "x_val",
                "val_label_name": "y_val",
                "optimizer": "rmsprop",
                "loss_function": "SparseCategoricalCrossentropy",
                "from_logits": True,
                "validation_split": 0.3,
                "learning_rate": sim.learning_rate,
                "k-fold_validation": 0,
            },
            "model": json.loads(sim.model)
        }
        # print(postdata)
        # resp = requests.post("http://127.0.0.1:7000/simulations", json=postdata)
        resp = requests.post("http://tracker-deployer:7000/simulations", json=postdata)
        if resp.ok:
            return sim
        sim.delete()
        return HttpResponse("Failed to reach deployer", 500)
    else:
        return HttpResponse("Bad request", 400)


@csrf_exempt
def simulations(request):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", 403)
    if request.method == 'POST':
        return post_sim(request)
    elif request.method == 'GET':
        return Simulation.objects.filter(owner=request.user)
    return HttpResponse("Bad request", 400)


@csrf_exempt
def get_simulation(request, id):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", 403)

    sim = Simulation.objects.get(pk=id)

    if sim.owner == request.user:
        if request.method == "DELETE":
            sim.delete()
            return HttpResponse(sim, 200)
        return sim
    else:
        return HttpResponse("Forbidden", 403)


def command_start(request, id):  # return the objects you're acting on in these
    sim = Simulation.objects.get(id=id)
    requests.post(f'http://tracker-deployer:7000/simulations/{id}/START')
    sim.isrunning = True
    sim.save()
    return HttpResponse(sim, 200)


def command_stop(request, id):
    sim = Simulation.objects.get(id=id)
    requests.delete(f'http://tracker-deployer:7000/simulations/{id}')
    sim.delete()
    return HttpResponse(sim, 200)


def command_pause(request, id):
    sim = Simulation.objects.get(id=id)
    requests.post(f'http://tracker-deployer:7000/simulations/{id}/PAUSE')
    sim.isrunning = False
    sim.save()
    return HttpResponse(sim, 200)


@csrf_exempt
def command_simulation(request, command, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please log in", 403)
    if not Simulation.objects.filter(id__exact=id, owner=request.user).exists():
        return HttpResponse("You do not own this simulation", 403)
    if command == "START":
        return command_start(request, id)
    elif command == "STOP":
        return command_stop(request, id)
    elif command == "PAUSE":
        return command_pause(request, id)
    else:
        return HttpResponse("Unknown command", 400)
