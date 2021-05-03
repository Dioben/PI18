from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import  UploadModelFileForm, UploadDataSetFileForm


# Imaginary function to handle model file.
# from somewhere import handle_uploaded_file

def simulation_view(request, id=None):
    message = 'Upload Json!'
    if request.method == 'POST':
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
            return redirect('Simulations')
        else:
            message = 'Error'
    elif request.method == 'DELETE':  # É passado o Argumento id para realizar delete
        return None
    else:
        form1 = UploadModelFileForm()
        form2 = UploadDataSetFileForm()
    return render(request, 'simulations.html', {'form_model': form1, 'form_data':form2, 'message': message})


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

