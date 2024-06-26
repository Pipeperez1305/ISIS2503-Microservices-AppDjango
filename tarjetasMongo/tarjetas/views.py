from django.conf import settings
from tarjetas.forms import  TarjetaForm
from .models import Tarjeta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

def TarjetaList(request):
    client = MongoClient(settings.MONGO_CLI)
    db = client.tarjetas_db
    tarjetas_collection = db['tarjetas']
    tarjetas_data = tarjetas_collection.find({})
    tarjetas = [{
            'id': str(tarjeta['_id']),  
            'tipo': tarjeta.get('tipo', ''),
            'puntaje': tarjeta.get('puntaje', 0)
        } for tarjeta in tarjetas_data]
    client.close()
    return render(request, 'Tarjeta/tarjetas.html', {'tarjeta_list': tarjetas})

def TarjetaCreate(request):
    client = MongoClient(settings.MONGO_CLI)
    db = client.tarjetas_db
    tarjetas_collection = db['tarjetas']
    
    if request.method == 'POST':
        tarjeta_data = {
            'tipo': request.POST.get('tipo'),
            'puntaje': request.POST.get('puntaje')
        }
        result = tarjetas_collection.insert_one(tarjeta_data)
        if result.acknowledged:
            messages.add_message(request, messages.SUCCESS, 'Tarjeta creada exitosamente')
            return HttpResponseRedirect(reverse('tarjetaCreate'))
        else:
            messages.add_message(request, messages.ERROR, 'Error al crear la tarjeta')
    client.close()
    return render(request, 'Tarjeta/tarjetaCreate.html')


def TarjetaUpdate(request, id):
    client = MongoClient(settings.MONGO_CLI)
    db = client.tarjetas_db
    tarjetas_collection = db['tarjetas']
    tarjeta = tarjetas_collection.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        update_data = {
            'tipo': request.POST.get('tipo'),
            'puntaje': request.POST.get('puntaje')
        }
        result = tarjetas_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        if result.modified_count > 0:
            messages.add_message(request, messages.SUCCESS, 'Tarjeta actualizada exitosamente')
            return HttpResponseRedirect(reverse('tarjetaList'))
        else:
            messages.add_message(request, messages.ERROR, 'Error al actualizar la tarjeta')
    client.close()
    return render(request, 'Tarjeta/tarjetaUpdate.html', {'form': tarjeta})


def getTarjetaList(request):
    if request.method == 'GET':
        client = MongoClient(settings.MONGO_CLI)
        db = client.tarjetas_db
        tarjetas_collection = db['tarjetas']
        tarjetas_data = tarjetas_collection.find({})
        # Convertir los documentos MongoDB a formato adecuado para JSON
        tarjetas = [{
            'id': str(tarjeta['_id']), 
            'tipo': tarjeta.get('tipo', ''),
            'puntaje': tarjeta.get('puntaje', 0)
        } for tarjeta in tarjetas_data]

        client.close()
        return JsonResponse(tarjetas, safe=False)
    

 
def deleteTarjeta(request, id):
    client = MongoClient(settings.MONGO_CLI)
    db = client.tarjetas_db
    tarjetas_collection = db['tarjetas']

    if request.method == 'POST':
        result = tarjetas_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count > 0:
            return HttpResponseRedirect(reverse('tarjetaList'))
        else:
            return HttpResponse('No se pudo eliminar la tarjeta')
    client.close()