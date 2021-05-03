from django.shortcuts import render, redirect

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def simulations(request):
    return render(request, 'simulations.html')


def simulation_create(request):
    return render(request, 'simulationCreate.html')


def simulation_info(request, id):
    return render(request, 'simulationInfo.html')


# Imaginary function to handle model file.
# from somewhere import handle_uploaded_file
def simulation_view(request, id=None):
    message = 'Upload Json!'
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # handle_uploaded_file(request.FILES['file'])
            print("Simulation Created and Started")
            # return HttpResponseRedirect('/success/url/')
            return redirect('Simulations')
        else:
            message = 'Error'
    elif request.method == 'DELETE':  # É passado o Argumento id para realizar delete
        return None
    else:
        form = UploadFileForm()
    return render(request, 'simulation_create_api.html', {'form': form, 'message': message})


def get_simulation(request, id):
    #Render da simulation_details
    #return render(request, 'simulation_details_api.html', {'id': id}) test
    return None


def command_simulation(request, command, id):
    if request.method == 'POST':
        if command == "START":
            # Do something
            return None
        elif command == "STOP":
            # Do Something
            return None
        else:
            # Do Something
            return None
    else:
        # Do Something
        return None

