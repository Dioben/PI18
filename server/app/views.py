import csv
import json
import os
import sys
import zipfile
from datetime import datetime
from io import StringIO, BytesIO

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


DEPLOYER_BASE_URL = 'http://tracker-deployer:7000' if 'DEPLOYER_BASE_URL' not in os.environ else os.environ.get('DEPLOYER_BASE_URL')
GRAFANA_BASE_URL = 'http://localhost:3000' if 'GRAFANA_BASE_URL' not in os.environ else os.environ.get('GRAFANA_BASE_URL')


def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


@csrf_exempt
def users(request):
    if request.user.is_authenticated:
        if not request.user.is_staff:
            return HttpResponse("Forbidden", status=403)
        if 'give' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            if not u.exists():
                return HttpResponse("Not found", status=404)
            user = u[0]
            user.is_staff = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'remove' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            if not u.exists():
                return HttpResponse("Not found", status=404)
            user = u[0]
            user.is_staff = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'enable' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            if not u.exists():
                return HttpResponse("Not found", status=404)
            user = u[0]
            user.is_active = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'disable' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            if not u.exists():
                return HttpResponse("Not found", status=404)
            user = u[0]
            user.is_active = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'delete' in request.POST:
            id = request.POST.get('user_id')
            u = User.objects.filter(id=id)
            if not u.exists():
                return HttpResponse("Not found", status=404)
            user = u[0]
            user.delete()
            return HttpResponseRedirect(request.path)
        else:
            users = User.objects.all().exclude(id=request.user.id)
            t_parms = {
                'users': users
            }
            return render(request, 'users.html', t_parms)
    return redirect('/accounts/login/')


@csrf_exempt
def userinfo(request, id):
    if request.user.is_authenticated:
        if not request.user.is_staff:
            return HttpResponse("Forbidden", status=403)
        if not User.objects.filter(id=id).exists():
            return HttpResponse("Not found", status=404)
        if 'give' in request.POST:
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_staff = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'remove' in request.POST:
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_staff = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'enable' in request.POST:
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_active = True
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'disable' in request.POST:
            u = User.objects.filter(id=id)
            user = u[0]
            user.is_active = False
            user.save()
            return HttpResponseRedirect(request.path)
        elif 'delete' in request.POST:
            u = User.objects.filter(id=id)
            user = u[0]
            user.delete()
            return HttpResponseRedirect(request.path)
        else:
            usera = User.objects.filter(id=id)
            stats = requests.get(DEPLOYER_BASE_URL+'/simulations_statistics', timeout=100)
            if stats.ok:
                stats = json.loads(stats.content)
            else:
                stats = dict()
            t_parms = {
                'usera': usera[0],
                'simulations': Simulation.objects.filter(owner=usera[0]),
                'simulations_total': Simulation.objects.filter(owner=usera[0]).count(),
                'simulations_run': Simulation.objects.filter(owner=usera[0], isrunning=True).count(),
                'simulations_done': Simulation.objects.filter(owner=usera[0], isdone=True).count(),
                'tags': Tagged.objects.filter(tagger=usera[0]),
                'stats': stats,
            }
            return render(request, 'userInfo.html', t_parms)
    return redirect('/accounts/login/')


def simulation_list(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if 'deleteError' in request.POST:
        sim = Simulation.objects.filter(id=request.POST.get('deleteErrorSimId'))
        if sim.exists():
            sim = sim.get()
            if sim.owner == request.user or request.user.is_staff:
                sim.error_text = ""
                sim.save()
        request.method = 'GET'
    response = simulations(request)
    if type(response) == HttpResponse:
        return response
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    t_parms = {
        'simulations': response,
        'notification': notification,
        'tags': Tagged.objects.filter(sim__in=response),
    }
    return render(request, 'simulations/simulations.html', t_parms)


def simulation_list_content(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    response = simulations(request)
    if type(response) == HttpResponse:
        return response
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    t_parms = {
        'simulations': response,
        'notification': notification,
        'tags': Tagged.objects.filter(sim__in=response),
    }
    return render(request, 'simulations/simulationsContent.html', t_parms)


def simulation_create(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
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
        return redirect('/accounts/login/')
    if 'downloadData' in request.POST:
        HEADER = []
        id = request.POST.get('simulationIdInput')
        general = request.POST.get('optiongeneralInfo')
        weight = request.POST.get('optionWeight')
        sim = Simulation.objects.filter(id=id)

        if not sim.exists():
            return HttpResponse("Not found", status=404)

        sim = sim.get()
        if sim.owner == request.user or request.user.is_staff:
            if general:
                HEADER.append('GeneralInfo')
                extra_metrics = ExtraMetrics.objects.filter(sim=sim)

            if weight:
                HEADER.append('Weights')
                weights = Weights.objects.filter(sim=sim)

            zipped_file = BytesIO()
            # Construir File
            with zipfile.ZipFile(zipped_file, 'a', zipfile.ZIP_DEFLATED) as zipped:
                for h in HEADER:  # determines which csv file to write
                    rs = StringIO()
                    csv_data = StringIO()
                    if h == 'Weights':
                        fieldnames = ['Epoch',
                                      'Layer Index',
                                      'Layer Name',
                                      'Weight',
                                      ]
                        writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
                        writer.writeheader()
                        for w in weights:
                            writer.writerow({'Epoch': w.epoch,
                                             'Layer Index': w.layer_index,
                                             'Layer Name': w.layer_name,
                                             'Weight': w.weight})
                        for r in rs:
                            writer.writerow(r)
                        csv_data.seek(0)
                        zipped.writestr("{}.csv".format(h), csv_data.read())

                    if h == 'GeneralInfo':
                        fieldnames = ['Name',
                                      'Owner',
                                      'Learning Rate',
                                      'Model',
                                      'Layers',
                                      'Epoch Interval',
                                      'Goal Epoch',
                                      'Metrics',
                                      'Error Text',
                                      ]
                        dic={'Name': sim.name,
                             'Owner': sim.owner,
                             'Learning Rate': sim.learning_rate,
                             'Model': sim.model,
                             'Layers': sim.layers,
                             'Epoch Interval': sim.epoch_interval,
                             'Goal Epoch': sim.goal_epochs,
                             'Metrics': sim.metrics,
                             'Error Text': sim.error_text,
                             }
                        for metric in extra_metrics:
                            fieldnames.append("Extra Metric - " + metric.metric)
                            dic["Extra Metric - " + metric.metric]=metric.value
                        writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerow(dic)
                        for r in rs:
                            writer.writerow(r)
                        csv_data.seek(0)
                        zipped.writestr("{}.csv".format(h), csv_data.read())

            zipped_file.seek(0)
            response = HttpResponse(zipped_file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + sim.name + 'Data.zip'
            return response
        return HttpResponse("Forbidden", status=403)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    if 'deleteError' in request.POST:
        response.error_text = ""
        response.save()
        request.method = "GET"
    responseList = simulations(request)
    if type(responseList) == HttpResponse:
        return responseList
    extraMetrics = ExtraMetrics.objects.filter(sim_id=id)
    extraMetricsEpochs = extraMetrics.values("epoch").distinct()
    extraMetricsMetrics = extraMetrics.values("metric").distinct()
    extraMetricsDict = {epoch.get('epoch'): [] for epoch in extraMetricsEpochs}
    for epoch in extraMetricsEpochs:
        for metric in extraMetricsMetrics:
            extraMetricsDict.get(epoch.get('epoch')).append(
                {"metric": metric.get('metric'),
                 "value": extraMetrics.filter(epoch=epoch.get('epoch'), metric=metric.get('metric')).values("value").get().get('value')})
    extraMetricsDict = {key: sorted(value, key=lambda x: x['metric']) for key, value in extraMetricsDict.items()}
    t_params = {
        'simulation': response,
        'notification': notification,
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)],
        'tags': Tagged.objects.filter(sim=response),
        'simulationList': responseList,
        'extra_metrics': dict(sorted(extraMetricsDict.items())),
        'grafana_base_url': GRAFANA_BASE_URL
    }
    return render(request, 'simulationInfo/simulationInfo.html', t_params)


def simulation_info_content1(request, id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if 'deleteTag' in request.POST:
        tag_id = request.POST.get('tag_id')
        t = Tagged.objects.filter(id=tag_id)
        if t.exists():
            t = t.get()
            if t.tagger == request.user or request.user.is_staff:
                t.delete()
        return HttpResponseRedirect(request.path)
    if 'addTag' in request.POST:
        sim_id = request.POST.get('simulation_id')
        sim = Simulation.objects.filter(id=sim_id)
        if sim.exists():
            sim = sim.get()
            if sim is not None and (sim.owner == request.user or request.user.is_staff):
                tag_name = request.POST.get('tagname')
                tag = Tagged(tag=tag_name, sim=sim, tagger=request.user, iskfold=False)
                tag.save()
        return HttpResponseRedirect(request.path)
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    notification = None
    if 'notification' in request.session:
        notification = request.session['notification']
        del request.session['notification']
        request.session.modified = True
    t_params = {
        'simulation': response,
        'notification': notification,
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)],
        'tags': Tagged.objects.filter(sim=response),
    }
    return render(request, 'simulationInfo/simulationInfoContent1.html', t_params)


def simulation_info_content2(request, id):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    response = get_simulation(request, id)
    if type(response) == HttpResponse:
        return response
    extraMetrics = ExtraMetrics.objects.filter(sim_id=id)
    extraMetricsEpochs = extraMetrics.values("epoch").distinct()
    extraMetricsMetrics = extraMetrics.values("metric").distinct()
    extraMetricsDict = {epoch.get('epoch'): [] for epoch in extraMetricsEpochs}
    for epoch in extraMetricsEpochs:
        for metric in extraMetricsMetrics:
            extraMetricsDict.get(epoch.get('epoch')).append(
                {"metric": metric.get('metric'),
                 "value": extraMetrics.filter(epoch=epoch.get('epoch'), metric=metric.get('metric')).values("value").get().get('value')})
    extraMetricsDict = {key: sorted(value, key=lambda x: x['metric']) for key, value in extraMetricsDict.items()}
    t_params = {
        'simulation': response,
        'updates': [UpdateSerializer(update).data for update in Update.objects.filter(sim_id=id)],
        'extra_metrics': dict(sorted(extraMetricsDict.items()))
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
    sim = Simulation.objects.filter(id__exact=id)
    if not sim.exists():
        return HttpResponse("Not found", status=404)
    simName = sim.get().name
    response = command_simulation(request, command, id)
    if response.status_code == 200:
        sim = Simulation.objects.filter(id__exact=id)
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
        if 'user' in request.META.get('HTTP_REFERER'):
            return redirect(request.META.get('HTTP_REFERER'))
        return redirect('/simulations/')
    return response


def post_sim(request):
    fieldForm = SimCreationForm(request.POST, request.FILES)
    fileForm = ConfigFileSimCreationForm(request.POST, request.FILES)
    if fieldForm.is_valid():
        cleaned_data = fieldForm.cleaned_data

        model = cleaned_data['model']
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

        if not cleaned_data['use_url_datasets']:
            trainext = cleaned_data['train_dataset'].name.split('.')[-1]
            testext = cleaned_data['test_dataset'].name.split('.')[-1]
            valext = cleaned_data['val_dataset'].name.split('.')[-1]
            if trainext != testext or testext != valext or trainext != valext:
                return HttpResponse("Bad request", status=400)
            if trainext != cleaned_data['dataset_format']:
                return HttpResponse("Bad request", status=400)

        metric_conf = dict()
        for x in cleaned_data['metrics_conf']:
            x = x.split(':')
            if x[0] not in metric_conf:
                metric_conf[x[0]] = dict()
            metric_conf[x[0]][x[1]] = x[2]

        optimizer_conf = dict()
        for x in cleaned_data['optimizer_conf']:
            x = x.split(':')
            if x[0] not in optimizer_conf:
                optimizer_conf[x[0]] = dict()
            optimizer_conf[x[0]][x[1]] = x[2]

        loss_function_conf = dict()
        for x in cleaned_data['loss_function_conf']:
            x = x.split(':')
            if x[0] not in loss_function_conf:
                loss_function_conf[x[0]] = dict()
            loss_function_conf[x[0]][x[1]] = x[2]

        firstPass = True
        allRespOk = True
        simList = []
        for optimizer_i in range(len(cleaned_data['optimizer'])):
            for loss_function_i in range(len(cleaned_data['loss_function'])):
                for learning_rate_i in range(len(cleaned_data['learning_rate'])):
                    if not allRespOk:
                        break
                    optimizer = cleaned_data['optimizer'][optimizer_i]
                    loss_function = cleaned_data['loss_function'][loss_function_i]
                    learning_rate = float(cleaned_data['learning_rate'][learning_rate_i])
                    name = cleaned_data['name']
                    if len(cleaned_data['optimizer']) > 1:
                        name += ' (O' + str(optimizer_i+1) + ')'
                    if len(cleaned_data['loss_function']) > 1:
                        name += ' (LF' + str(loss_function_i+1) + ')'
                    if len(cleaned_data['learning_rate']) > 1:
                        name += ' (LR' + str(learning_rate_i+1) + ')'

                    k_fold_ids = []
                    if not cleaned_data['is_k_fold']:
                        sim = Simulation(owner=request.user,
                                         isdone=False,
                                         isrunning=True,
                                         model=modeltext,
                                         name=name,
                                         layers=len(modeljson['config']['layers']),
                                         biases=bytes(biastext, 'utf-8'),
                                         epoch_interval=cleaned_data["logging_interval"],
                                         goal_epochs=cleaned_data["max_epochs"],
                                         learning_rate=learning_rate,
                                         metrics=cleaned_data["metrics"])
                        sim.save()
                        simList.append(sim)
                        if 'extra_tags' in cleaned_data:
                            for tag in cleaned_data['extra_tags']:
                                tagged = Tagged(tag=tag,
                                                sim=sim,
                                                tagger=request.user,
                                                iskfold=False)
                                tagged.save()
                    else:
                        for i in range(int(cleaned_data['k_fold_validation'])):
                            sim = Simulation(owner=request.user,
                                             isdone=False,
                                             isrunning=True,
                                             model=modeltext,
                                             name=name + " (" + str(i + 1) + ")",
                                             layers=len(modeljson['config']['layers']),
                                             biases=bytes(biastext, 'utf-8'),
                                             epoch_interval=cleaned_data["logging_interval"],
                                             goal_epochs=cleaned_data["max_epochs"],
                                             learning_rate=learning_rate,
                                             metrics=cleaned_data["metrics"])
                            sim.save()
                            tagged = Tagged(tag=cleaned_data['tag'],
                                            sim=sim,
                                            tagger=request.user,
                                            iskfold=True)
                            tagged.save()
                            k_fold_ids.append(sim.id.int)
                            simList.append(sim)
                            if 'extra_tags' in cleaned_data:
                                for tag in cleaned_data['extra_tags']:
                                    tagged = Tagged(tag=tag,
                                                    sim=sim,
                                                    tagger=request.user,
                                                    iskfold=False)
                                    tagged.save()

                    if not cleaned_data['use_url_datasets']:
                        trainset = '/all_datasets/' + str(simList[0].id) + '-dataset_train.' + trainext
                        testset = '/all_datasets/' + str(simList[0].id) + '-dataset_test.' + testext
                        valset = '/all_datasets/' + str(simList[0].id) + '-dataset_val.' + valext
                        if firstPass:
                            f = open(trainset, 'wb+')
                            for chunk in cleaned_data['train_dataset'].chunks():
                                f.write(chunk)
                            f.close()
                            f = open(testset, 'wb+')
                            for chunk in cleaned_data['test_dataset'].chunks():
                                f.write(chunk)
                            f.close()
                            f = open(valset, 'wb+')
                            for chunk in cleaned_data['val_dataset'].chunks():
                                f.write(chunk)
                            f.close()
                    else:
                        trainset = cleaned_data['url_train_dataset']
                        testset = cleaned_data['url_test_dataset']
                        valset = cleaned_data['url_val_dataset']

                    postdata = {
                        "conf": {
                            "id": str(sim.id.int),
                            "dataset_train": trainset,
                            "dataset_test": testset,
                            "dataset_val": valset,
                            "dataset_url": cleaned_data['use_url_datasets'],
                            "batch_size": cleaned_data['batch_size'],
                            "epochs": sim.goal_epochs,
                            "epoch_period": sim.epoch_interval,
                            "train_feature_name": cleaned_data['train_feature_name'] if cleaned_data['train_feature_name'] else '',
                            "train_label_name": cleaned_data['train_label_name'] if cleaned_data['train_label_name'] else '',
                            "test_feature_name": cleaned_data['test_feature_name'] if cleaned_data['test_feature_name'] else '',
                            "test_label_name": cleaned_data['test_label_name'] if cleaned_data['test_label_name'] else '',
                            "val_feature_name": cleaned_data['val_feature_name'] if cleaned_data['val_feature_name'] else '',
                            "val_label_name": cleaned_data['val_label_name'] if cleaned_data['val_label_name'] else '',
                            "optimizer": optimizer,
                            "optimizer_conf": optimizer_conf[optimizer] if optimizer in optimizer_conf else dict(),
                            "loss_function": loss_function,
                            "loss_function_conf": loss_function_conf[loss_function] if loss_function in loss_function_conf else dict(),
                            "learning_rate": learning_rate,
                            "k-fold_validation": 0 if not cleaned_data['k_fold_validation'] else cleaned_data['k_fold_validation'],
                            "k-fold_ids": k_fold_ids,
                            "metrics": [{'metric': metric, 'conf': metric_conf[metric] if metric in metric_conf else dict()} for metric in cleaned_data["metrics"]],
                            "label_column": cleaned_data['label_column'] if cleaned_data['label_column'] else ''
                        },
                        "model": modeljson
                    }
                    resp = requests.post(DEPLOYER_BASE_URL+"/simulations", json=postdata)
                    if not resp.ok:
                        allRespOk = False
                    firstPass = False
        if allRespOk:
            return sim
        for sim in simList:
            sim.delete()
        return HttpResponse("Failed to reach deployer", status=500)
    elif fileForm.is_valid():
        cleaned_data = fileForm.cleaned_data

        model = cleaned_data['model']
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

        config = cleaned_data['config']
        configtext = b''
        for chunk in config.chunks():
            configtext += chunk
        configjson = json.loads(configtext)

        if not cleaned_data['use_url_datasets']:
            trainext = cleaned_data['train_dataset'].name.split('.')[-1]
            testext = cleaned_data['test_dataset'].name.split('.')[-1]
            valext = cleaned_data['val_dataset'].name.split('.')[-1]
            if trainext != testext or testext != valext or trainext != valext:
                return HttpResponse("Bad request", status=400)
            if trainext == 'csv' and 'label_column' not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'pickle' and 'label_column' not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'zip' and 'label_column' not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'arff' and 'label_column' not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'json' and 'label_column' not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'npz' and "train_feature_name" not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'npz' and "train_label_name" not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'npz' and "test_feature_name" not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'npz' and "test_label_name" not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'npz' and "val_feature_name" not in configjson:
                return HttpResponse("Bad request", status=400)
            if trainext == 'npz' and "val_label_name" not in configjson:
                return HttpResponse("Bad request", status=400)

        firstPass = True
        allRespOk = True
        simList = []
        for optimizer_i in range(len(configjson['optimizers'])):
            for loss_function_i in range(len(configjson['loss_functions'])):
                for learning_rate_i in range(len(configjson['learning_rates'])):
                    if not allRespOk:
                        break
                    optimizer = configjson['optimizers'][optimizer_i]
                    loss_function = configjson['loss_functions'][loss_function_i]
                    learning_rate = configjson['learning_rates'][learning_rate_i]
                    name = configjson['name']
                    if len(configjson['optimizers']) > 1:
                        name += ' (O' + str(optimizer_i+1) + ')'
                    if len(configjson['loss_functions']) > 1:
                        name += ' (LF' + str(loss_function_i+1) + ')'
                    if len(configjson['learning_rates']) > 1:
                        name += ' (LR' + str(learning_rate_i+1) + ')'

                    k_fold_ids = []
                    if configjson['k-fold_validation'] < 2:
                        sim = Simulation(owner=request.user,
                                         isdone=False,
                                         isrunning=True,
                                         model=modeltext,
                                         name=name,
                                         layers=len(modeljson['config']['layers']),
                                         biases=bytes(biastext, 'utf-8'),
                                         epoch_interval=configjson['epoch_period'],
                                         goal_epochs=configjson['total_epochs'],
                                         learning_rate=learning_rate,
                                         metrics=[metric['metric'] for metric in configjson["extra-metrics"]])
                        sim.save()
                        simList.append(sim)
                        if 'tags' in configjson:
                            for tag in configjson['tags']:
                                tagged = Tagged(tag=tag,
                                                sim=sim,
                                                tagger=request.user,
                                                iskfold=False)
                                tagged.save()
                    else:
                        for i in range(int(configjson['k-fold_validation'])):
                            sim = Simulation(owner=request.user,
                                             isdone=False,
                                             isrunning=True,
                                             model=modeltext,
                                             name=name + " (" + str(i + 1) + ")",
                                             layers=len(modeljson['config']['layers']),
                                             biases=bytes(biastext, 'utf-8'),
                                             epoch_interval=configjson['epoch_period'],
                                             goal_epochs=configjson['total_epochs'],
                                             learning_rate=learning_rate,
                                             metrics=[metric['metric'] for metric in configjson["extra-metrics"]])
                            sim.save()
                            tagged = Tagged(tag=configjson['k-fold_tag'],
                                            sim=sim,
                                            tagger=request.user,
                                            iskfold=True)
                            tagged.save()
                            k_fold_ids.append(sim.id.int)
                            simList.append(sim)
                            if 'tags' in configjson:
                                for tag in configjson['tags']:
                                    tagged = Tagged(tag=tag,
                                                    sim=sim,
                                                    tagger=request.user,
                                                    iskfold=False)
                                    tagged.save()

                    if not cleaned_data['use_url_datasets']:
                        trainset = '/all_datasets/' + str(simList[0].id) + '-dataset_train.' + trainext
                        testset = '/all_datasets/' + str(simList[0].id) + '-dataset_test.' + testext
                        valset = '/all_datasets/' + str(simList[0].id) + '-dataset_val.' + valext
                        if firstPass:
                            f = open(trainset, 'wb+')
                            for chunk in cleaned_data['train_dataset'].chunks():
                                f.write(chunk)
                            f.close()
                            f = open(testset, 'wb+')
                            for chunk in cleaned_data['test_dataset'].chunks():
                                f.write(chunk)
                            f.close()
                            f = open(valset, 'wb+')
                            for chunk in cleaned_data['val_dataset'].chunks():
                                f.write(chunk)
                            f.close()
                    else:
                        trainset = configjson['dataset_train']
                        testset = configjson['dataset_test']
                        valset = configjson['dataset_val']

                    postdata = {
                        "conf": {
                            "id": str(sim.id.int),
                            "dataset_train": trainset,
                            "dataset_test": testset,
                            "dataset_val": valset,
                            "dataset_url": cleaned_data['use_url_datasets'],
                            "batch_size": configjson['batch_size'],
                            "epochs": sim.goal_epochs,
                            "epoch_period": sim.epoch_interval,
                            "train_feature_name": configjson['train_feature_name'] if configjson['train_feature_name'] else '',
                            "train_label_name": configjson['train_label_name'] if configjson['train_label_name'] else '',
                            "test_feature_name": configjson['test_feature_name'] if configjson['test_feature_name'] else '',
                            "test_label_name": configjson['test_label_name'] if configjson['test_label_name'] else '',
                            "val_feature_name": configjson['val_feature_name'] if configjson['val_feature_name'] else '',
                            "val_label_name": configjson['val_label_name'] if configjson['val_label_name'] else '',
                            "optimizer": optimizer['optimizer'],
                            "optimizer_conf": optimizer['conf'],
                            "loss_function": loss_function['loss_function'],
                            "loss_function_conf": loss_function['conf'],
                            "learning_rate": learning_rate,
                            "k-fold_validation": configjson['k-fold_validation'],
                            "k-fold_ids": k_fold_ids,
                            "metrics": configjson["extra-metrics"],
                            "label_column": configjson['label_column'] if configjson['label_column'] else ''
                        },
                        "model": modeljson
                    }
                    resp = requests.post(DEPLOYER_BASE_URL+"/simulations", json=postdata)
                    if not resp.ok:
                        allRespOk = False
                    firstPass = False
        if allRespOk:
            return sim
        for sim in simList:
            sim.delete()
        return HttpResponse("Failed to reach deployer", status=500)
    else:
        return HttpResponse("Bad request", status=400)


def simulations(request):
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", status=403)
    if request.method == 'POST':
        return post_sim(request)
    elif request.method == 'GET':
        return Simulation.objects.filter(owner=request.user)
    return HttpResponse("Bad request", status=400)


def get_simulation(request, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please Log In", status=403)

    sim = Simulation.objects.filter(pk=id)

    if not sim.exists():
        return HttpResponse("Not found", status=404)

    sim = sim.get()
    if sim.owner == request.user or request.user.is_staff:
        if request.method == "DELETE":
            sim.delete()
            return HttpResponse(sim, status=200)
        return sim
    else:
        return HttpResponse("Forbidden", status=403)


def command_start(request, id):  # return the objects you're acting on in these
    sim = Simulation.objects.filter(id=id)
    if not sim.exists():
        return HttpResponse('Not found', status=404)
    requests.post(DEPLOYER_BASE_URL+'/simulations/{id}/START')
    sim.isrunning = True
    sim.save()
    return HttpResponse(sim, status=200)


def command_stop(request, id):
    sim = Simulation.objects.filter(id=id)
    if not sim.exists():
        return HttpResponse('Not found', status=404)
    requests.delete(DEPLOYER_BASE_URL+'/simulations/{id}')
    sim.delete()
    return HttpResponse(sim, status=200)


def command_pause(request, id):
    sim = Simulation.objects.filter(id=id)
    if not sim.exists():
        return HttpResponse('Not found', status=404)
    requests.post(DEPLOYER_BASE_URL+'/simulations/{id}/PAUSE')
    sim.isrunning = False
    sim.save()
    return HttpResponse(sim, status=200)


def command_simulation(request, command, id):
    if not request.user.is_authenticated:
        return HttpResponse("Please log in", status=403)
    sim = Simulation.objects.filter(id__exact=id)
    if not sim.exists():
        return HttpResponse("Not found", status=404)
    if not sim.get().owner == request.user and not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)
    if command == "START":
        return command_start(request, id)
    elif command == "STOP":
        return command_stop(request, id)
    elif command == "PAUSE":
        return command_pause(request, id)
    else:
        return HttpResponse("Unknown command", status=400)
