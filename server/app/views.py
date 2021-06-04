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
from app.forms import SimCreationForm, CustomUserCreationForm, ConfigFileSimCreationForm
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
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", status=403)
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
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
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", status=403)
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
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
        return HttpResponse("Please Log In", status=403)
    if request.method == 'POST':
        response = simulations(request)
        if type(response) is HttpResponse:
            if response.status_code == 400:
                return render(request, 'simulationCreate.html',
                              {'fieldForm': SimCreationForm(request.POST), 'fileForm': ConfigFileSimCreationForm(request.POST)})
            return response
        return redirect('/simulations/' + str(response.id.int))
    return render(request, 'simulationCreate.html', {'fieldForm': SimCreationForm(), 'fileForm': ConfigFileSimCreationForm()})


def simulation_info(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", status=403)
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
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
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", status=403)
    if 'deleteTag' in request.POST:
        tag_id = request.POST.get('tag_id')
        t = Tagged.objects.get(id=tag_id)
        t.delete()
        return HttpResponseRedirect(request.path)
    if 'addTag' in request.POST:
        sim_id = request.POST.get('simulation_id')
        tag_name = request.POST.get('tagname')
        tag = Tagged(tag=tag_name, sim=Simulation.objects.get(id=sim_id), tagger=request.user, iskfold=False)
        tag.save()
        return HttpResponseRedirect(request.path)
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
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
        return HttpResponse("Please Log In", status=403)
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
        return HttpResponse("Please Log In", status=403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    t_params = {
        'simulation': SimulationSerializer(response).data,
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)]
    }
    return HttpResponse(json.dumps(t_params), status=200)


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


def post_sim(request):
    fieldForm = SimCreationForm(request.POST, request.FILES)
    fileForm = ConfigFileSimCreationForm(request.POST, request.FILES)
    if fieldForm.is_valid():
        model = request.FILES['model']
        modeltext = b''
        for chunk in model.chunks():
            modeltext += chunk
        modeljson = json.loads(modeltext)
        biastext = "["
        for layer in modeljson['config']:
            if 'bias_initializer' in layer:
                biastext += f"{{{layer['bias_initializer']}}},"
            else:
                biastext += f"{{ }},"
        biastext += "]"

        k_fold_ids = []
        if not fieldForm.cleaned_data['is_k_fold']:
            sim = Simulation(owner=request.user,
                             isdone=False,
                             isrunning=True,
                             model=modeltext,
                             name=fieldForm.cleaned_data["name"],
                             layers=len(modeljson['config']['layers']),
                             biases=bytes(biastext, 'utf-8'),
                             epoch_interval=fieldForm.cleaned_data["logging_interval"],
                             goal_epochs=fieldForm.cleaned_data["max_epochs"],
                             learning_rate=fieldForm.cleaned_data["learning_rate"],
                             metrics=fieldForm.cleaned_data["metrics"])
            sim.save()
        else:
            for i in range(int(fieldForm.cleaned_data['k_fold_validation'])):
                sim = Simulation(owner=request.user,
                                 isdone=False,
                                 isrunning=True,
                                 model=modeltext,
                                 name=str(fieldForm.cleaned_data["name"]) + " (" + str(i + 1) + ")",
                                 layers=len(modeljson['config']['layers']),
                                 biases=bytes(biastext, 'utf-8'),
                                 epoch_interval=fieldForm.cleaned_data["logging_interval"],
                                 goal_epochs=fieldForm.cleaned_data["max_epochs"],
                                 learning_rate=fieldForm.cleaned_data["learning_rate"],
                                 metrics=fieldForm.cleaned_data["metrics"])
                sim.save()
                tagged = Tagged(tag=fieldForm.cleaned_data['tag'],
                                sim=sim,
                                tagger=request.user,
                                iskfold=True)
                tagged.save()
                k_fold_ids.append(sim.id.int)

        trainset = '/all_datasets/' + str(sim.id) + '-dataset_train.npz'
        f = open(trainset, 'wb+')
        for chunk in request.FILES['train_dataset'].chunks():
            f.write(chunk)
        f.close()

        testset = '/all_datasets/' + str(sim.id) + '-dataset_test.npz'
        f = open(testset, 'wb+')
        for chunk in request.FILES['test_dataset'].chunks():
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
                "batch_size": fieldForm.cleaned_data['batch_size'],
                "epochs": sim.goal_epochs,
                "epoch_period": sim.epoch_interval,
                "train_feature_name": "x_train",
                "train_label_name": "y_train",
                "test_feature_name": "x_test",
                "test_label_name": "y_test",
                "val_feature_name": "x_val",
                "val_label_name": "y_val",
                "optimizer": fieldForm.cleaned_data['optimizer'],
                "loss_function": fieldForm.cleaned_data['loss_function'],
                "from_logits": True,
                "learning_rate": sim.learning_rate,
                "k-fold_validation": 0 if fieldForm.cleaned_data['k_fold_validation'] is None else fieldForm.cleaned_data['k_fold_validation'],
                "k-fold_ids": k_fold_ids,
                "metrics": sim.metrics,
            },
            "model": json.loads(sim.model)
        }
        resp = requests.post("http://tracker-deployer:7000/simulations", json=postdata)
        if resp.ok:
            return sim
        sim.delete()
        return HttpResponse("Failed to reach deployer", status=500)
    elif fileForm.is_valid():
        model = request.FILES['model']
        modeltext = b''
        for chunk in model.chunks():
            modeltext += chunk
        modeljson = json.loads(modeltext)
        biastext = "["
        for layer in modeljson['config']:
            if 'bias_initializer' in layer:
                biastext += f"{{{layer['bias_initializer']}}},"
            else:
                biastext += f"{{ }},"
        biastext += "]"

        config = request.FILES['config']
        configtext = b''
        for chunk in config.chunks():
            configtext += chunk
        configjson = json.loads(configtext)

        k_fold_ids = []
        if configjson['k-fold_validation'] < 2:
            sim = Simulation(owner=request.user,
                             isdone=False,
                             isrunning=True,
                             model=modeltext,
                             name=configjson["name"],
                             layers=len(modeljson['config']['layers']),
                             biases=bytes(biastext, 'utf-8'),
                             epoch_interval=configjson['epoch_period'],
                             goal_epochs=configjson['total_epochs'],
                             learning_rate=configjson["learning_rate"],
                             metrics=configjson["extra-metrics"])
            sim.save()
        else:
            for i in range(int(configjson['k-fold_validation'])):
                sim = Simulation(owner=request.user,
                                 isdone=False,
                                 isrunning=True,
                                 model=modeltext,
                                 name=str(configjson["name"]) + " (" + str(i + 1) + ")",
                                 layers=len(modeljson['config']['layers']),
                                 biases=bytes(biastext, 'utf-8'),
                                 epoch_interval=configjson['epoch_period'],
                                 goal_epochs=configjson['total_epochs'],
                                 learning_rate=configjson["learning_rate"],
                                 metrics=configjson["extra-metrics"])
                sim.save()
                tagged = Tagged(tag=configjson['k-fold_tag'],
                                sim=sim,
                                tagger=request.user,
                                iskfold=True)
                tagged.save()
                k_fold_ids.append(sim.id.int)

        trainset = '/all_datasets/' + str(sim.id) + '-dataset_train.npz'
        f = open(trainset, 'wb+')
        for chunk in request.FILES['train_dataset'].chunks():
            f.write(chunk)
        f.close()

        testset = '/all_datasets/' + str(sim.id) + '-dataset_test.npz'
        f = open(testset, 'wb+')
        for chunk in request.FILES['test_dataset'].chunks():
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
                "batch_size": configjson['batch_size'],
                "epochs": sim.goal_epochs,
                "epoch_period": sim.epoch_interval,
                "train_feature_name": "x_train",
                "train_label_name": "y_train",
                "test_feature_name": "x_test",
                "test_label_name": "y_test",
                "val_feature_name": "x_val",
                "val_label_name": "y_val",
                "optimizer": configjson['optimizer'],
                "loss_function": configjson['loss_function'],
                "from_logits": True,
                "learning_rate": sim.learning_rate,
                "k-fold_validation": configjson['k-fold_validation'],
                "k-fold_ids": k_fold_ids,
                "metrics": sim.metrics,
            },
            "model": json.loads(sim.model)
        }
        resp = requests.post("http://tracker-deployer:7000/simulations", json=postdata)
        if resp.ok:
            return sim
        sim.delete()
        return HttpResponse("Failed to reach deployer", status=500)
    else:
        return HttpResponse("Bad request", status=400)


@csrf_exempt
def simulations(request):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", status=403)
    if request.method == 'POST':
        return post_sim(request)
    elif request.method == 'GET':
        return Simulation.objects.filter(owner=request.user)
    return HttpResponse("Bad request", status=400)


@csrf_exempt
def get_simulation(request, id):
    if not request.user.is_authenticated:  # you could use is_active here for email verification i think
        return HttpResponse("Please Log In", status=403)

    sim = Simulation.objects.get(pk=id)

    if sim.owner == request.user:
        if request.method == "DELETE":
            sim.delete()
            return HttpResponse(sim, status=200)
        return sim
    else:
        return HttpResponse("Forbidden", status=403)


def command_start(request, id):  # return the objects you're acting on in these
    sim = Simulation.objects.get(id=id)
    requests.post(f'http://tracker-deployer:7000/simulations/{id}/START')
    sim.isrunning = True
    sim.save()
    return HttpResponse(sim, status=200)


def command_stop(request, id):
    sim = Simulation.objects.get(id=id)
    requests.delete(f'http://tracker-deployer:7000/simulations/{id}')
    sim.delete()
    return HttpResponse(sim, status=200)


def command_pause(request, id):
    sim = Simulation.objects.get(id=id)
    requests.post(f'http://tracker-deployer:7000/simulations/{id}/PAUSE')
    sim.isrunning = False
    sim.save()
    return HttpResponse(sim, status=200)


@csrf_exempt
def command_simulation(request, command, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please log in", status=403)
    if not Simulation.objects.filter(id__exact=id, owner=request.user).exists():
        return HttpResponse("You do not own this simulation", status=403)
    if command == "START":
        return command_start(request, id)
    elif command == "STOP":
        return command_stop(request, id)
    elif command == "PAUSE":
        return command_pause(request, id)
    else:
        return HttpResponse("Unknown command", status=400)
