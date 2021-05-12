from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
from .forms import UploadModelFileForm, UploadDataSetFileForm
from app.models import *


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def simulation_list(request):
    return render(request, 'simulations.html')


def simulation_create(request):
    return render(request, 'simulationCreate.html')


def simulation_info(request, id):
    return render(request, 'simulationInfo.html')


# Imaginary function to handle model file.
# from somewhere import handle_uploaded_file


def post_sim(request):  # probably add a 3rd form to this thing
    #TODO: ENABLE SENDING URLS INSTEAD OF FILES AS WELL
    form1 = UploadModelFileForm(request.POST, request.FILES)
    form2 = UploadDataSetFileForm(request.POST, request.FILES)
    if form1.is_valid() and form2.is_valid():
        # handle_uploaded_file(request.FILES['model'])
        model = request.FILES['model']
        path_model = model.temporary_file_path()
        print(path_model)
        # handle_uploaded_file(request.FILES['dataset'])
        dataset = request.FILES['dataset']
        path_dataset = dataset.temporary_file_path()
        print(str(path_dataset))
        # TODO: read model into db, count layers into db, copy raw bias bytes, epoch interval, name, goal epochs
        sim = Simulation(owner=request.user, isdone=False, isrunning=False, model="read model file onto this i guess?", name="sample text",
                         biases=b'sample text', epoch_interval=10, goal_epochs=100)
        sim.save()
        #TODO: DISTINCT TRAIN AND TEST DATASETS MAYBE
        postdata = {"conf": {"id": sim.id,
                             "dataset_train": path_dataset,
                             "dataset_test": path_dataset,
                             "dataset_url": True,
                             "epochs": sim.goal_epochs,
                             "interval": sim.epoch_interval},
                    "model": {sim.model}
                    }
        resp = requests.post("http://tracker-deployer:7000/simulations", postdata)
        if resp.ok:
            return sim
        sim.delete()
        return HttpResponse("Failed to reach deployer", 500)


@csrf_exempt
def simulations(request):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", 403)
    if request.method == 'POST':
        return post_sim(request)
    else:
        return Simulation.objects.filter(owner=request.user)


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
    sim = Simulation.objects.get(id)
    requests.post(f'http://tracker-deployer:7000/simulations/{id}/START')
    sim.isrunning = True
    return HttpResponse(sim,200)

def command_stop(request, id):
    sim = Simulation.objects.get(id)
    requests.delete(f'http://tracker-deployer:7000/simulations/{id}')
    sim.delete()
    return HttpResponse(sim, 200)


def command_pause(request, id):
    sim = Simulation.objects.get(id)
    requests.post(f'http://tracker-deployer:7000/simulations/{id}/PAUSE')
    sim.isrunning = False
    sim.save()
    return HttpResponse(sim, 200)


@csrf_exempt
def command_simulation(request, command, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please log in",403)
    if not Simulation.objects.filter(id__exact=id,owner=request.user).exists():
        return HttpResponse("You do not own this simulation",403)
    if command == "START":
        return command_start(request, id)
    elif command == "STOP":
        return command_stop(request, id)
    elif command == "PAUSE":
        return command_pause(request, id)
    else:
        return HttpResponse("Unknown command", 400)
