from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm


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
    return render(request, 'simulations.html', {'form': form, 'message': message})


def get_simulation(request, id):
    #Render da simulation_details
    #return render(request, 'simulation_details.html', {'id': id}) test
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

