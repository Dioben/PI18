from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import  UploadModelFileForm, UploadDataSetFileForm
from models import *

# Imaginary function to handle model file.
# from somewhere import handle_uploaded_file




def post_sim(request): #probably add a 3rd form to this thing
    form1 = UploadModelFileForm(request.POST, request.FILES)
    form2 = UploadDataSetFileForm(request.POST, request.FILES)
    if form1.is_valid() and form2.is_valid():
        print("Got Model")
        # handle_uploaded_file(request.FILES['model'])
        model = request.FILES['model']
        path_model = model.temporary_file_path()
        print(path_model)

        print("Got Dataset")
        # handle_uploaded_file(request.FILES['dataset'])
        dataset = request.FILES['dataset']
        path_dataset = dataset.temporary_file_path()
        print(str(path_dataset))
        # do something
        print("Simulation Created and Started")
        # return HttpResponseRedirect('/success/url/')
        return redirect('Simulations') #TODO: REPLACE THIS WITH CREATED SIMULATION


@csrf_exempt
def simulations(request):
    if not request.user.is_authenticated: #you could use is_active here for email verification i think
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
            return HttpResponse(sim,200)
        return sim
    else:
        return HttpResponse("Forbidden", 403)


def command_start(request, id): #return the objects you're acting on in these
    pass


def command_stop(request, id):
    pass


@csrf_exempt
def command_simulation(request, command, id):
    if request.method == 'POST':
        if command == "START":
            return command_start(request,id)
        elif command == "STOP":
            return command_stop(request,id)
        else:
            # Do Something
            return None
    else:
        # Do Something
        return None


def signup(request):
    return None