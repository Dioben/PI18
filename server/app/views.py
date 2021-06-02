import json
import sys

from django.contrib import auth
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
from app.forms import UploadModelFileForm, UploadDataSetFileForm, ConfSimForm, CustomUserCreationForm
from app.models import *
from app.serializers import SimulationSerializer, UpdateSerializer


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


@csrf_exempt
def users(request):
    if request.user.is_authenticated and request.user.is_staff:
        if 'give' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_staff = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'remove' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_staff = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'enable' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_active = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'disable' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_active = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'delete' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.delete()
            return HttpResponseRedirect(request.path)
        else:
            users = User.objects.all().exclude(id=request.user.id)
            t_parms = {
                'users': users
            }
            return render(request, 'users.html', t_parms)

    return render(request, 'login.html')


@csrf_exempt
def userinfo(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        if 'give' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_staff = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'remove' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_staff = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'enable' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_active = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'disable' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_active = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'delete' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            user = u[0]
            user.delete()
            return HttpResponseRedirect(request.path)
        else:
            usera = User.objects.filter(id=id)
            print(Simulation.objects.filter(owner=usera[0]).count())
            print(len(Simulation.objects.filter(owner=usera[0])))
            t_parms = {
                'usera': usera[0],
                'simulations': Simulation.objects.filter(owner=usera[0]),
                'simulations_total': Simulation.objects.filter(owner=usera[0]).count(),
                'simulations_run': Simulation.objects.filter(owner=usera[0], isrunning=True).count(),
                'simulations_done': Simulation.objects.filter(owner=usera[0], isdone=True).count(),
            }
            return render(request, 'userInfo.html', t_parms)
    return render(request, 'login.html')


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
        'tags': Tagged.objects.filter(sim__in=response),
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
        'tags': Tagged.objects.filter(sim__in=response),
    }
    return render(request, 'simulations/simulationsContent.html', t_parms)

def simulation_create(request):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", 403)
    if request.method == 'POST':
        response = simulations(request)
        if type(response) is HttpResponse:
            if response.status_code == 400:
                return render(request, 'simulationCreate.html',
                              {'fileForm': UploadModelFileForm(request.POST), 'configForm': ConfSimForm(request.POST)})
            return response
        return redirect('/simulations/' + str(response.id.int))
    return render(request, 'simulationCreate.html', {'fileForm': UploadModelFileForm(), 'configForm': ConfSimForm()})


def simulation_info(request, id):
    if 'deleteTag' in request.POST:
        tag_id = request.POST.get('tag_id')
        t = Tagged.objects.get(id=tag_id)
        t.delete()
        return HttpResponseRedirect(request.path)
    if 'addtag' in request.POST:
        sim_id=request.POST.get('simulation_id')
        tag_name = request.POST.get('tagname')
        tag=Tagged(tag=tag_name,sim=Simulation.objects.get(id=sim_id),tagger=request.user,iskfold=False)
        tag.save()
        return HttpResponseRedirect(request.path)
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
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)],
        'tags': Tagged.objects.filter(sim=response),
    }
    return render(request, 'simulationInfo/simulationInfo.html', t_params)


def simulation_info_content1(request, id):
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
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)],
        'tags': Tagged.objects.filter(sim=response),
    }
    return render(request, 'simulationInfo/simulationInfoContent1.html', t_params)


def simulation_info_content2(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    t_params = {
        'simulation': response,
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)]
    }
    return render(request, 'simulationInfo/simulationInfoContent2.html', t_params)


def simulation_info_context(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", 403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    t_params = {
        'simulation': SimulationSerializer(response).data,
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)]
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
                request.session['notification'] = "Simulation \"" + simName + "\" has been paused."
                request.session.modified = True
                return redirect(request.META.get('HTTP_REFERER'))
            request.session['notification'] = "Simulation \"" + simName + "\" has been resumed."
            request.session.modified = True
            return redirect(request.META.get('HTTP_REFERER'))
        request.session['notification'] = "Simulation \"" + simName + "\" has been deleted."
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
                         learning_rate=confForm.cleaned_data["learning_rate"],
                         metrics=confForm.cleaned_data["metrics"])
        sim.save()

        k_fold_ids = []
        if 'tag' in confForm.cleaned_data:
            tagged = Tagged(tag=confForm.cleaned_data['tag'],
                            sim=sim,
                            tagger=request.user)
            tagged.save()
            if confForm.cleaned_data['k_fold_validation'] > 0:
                for i in range(int(confForm.cleaned_data['k_fold_validation'])):
                    ksim = Simulation(owner=request.user,
                                      isdone=False,
                                      isrunning=True,
                                      model=modeltext,
                                      name=str(confForm.cleaned_data["name"])+" ("+str(i+2)+")",
                                      layers=len(modeljson['config']['layers']),
                                      biases=bytes(biastext, 'utf-8'),
                                      epoch_interval=confForm.cleaned_data["logging_interval"],
                                      goal_epochs=confForm.cleaned_data["max_epochs"],
                                      learning_rate=confForm.cleaned_data["learning_rate"],
                                      metrics=confForm.cleaned_data["metrics"])
                    ksim.save()
                    ktagged = Tagged(tag=confForm.cleaned_data['tag'],
                                     sim=ksim,
                                     tagger=request.user,
                                     iskfold=True)
                    ktagged.save()
                    k_fold_ids.append(ksim.id.int)

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
                "optimizer": confForm.cleaned_data['optimizer'],
                "loss_function": confForm.cleaned_data['loss_function'],
                "from_logits": True,
                "validation_split": 0.3,
                "learning_rate": sim.learning_rate,
                "k-fold_validation": confForm.cleaned_data['k_fold_validation'],
                "k-fold_ids": k_fold_ids,
                "metrics": confForm.cleaned_data['metrics'],
            },
            "model": json.loads(sim.model)
        }
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
