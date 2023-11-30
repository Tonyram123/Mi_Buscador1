# buscador/views.py
# ya esta bien asi padrino no le muevas
from django.shortcuts import render
from .models import Palabra, URL
from django.http import HttpResponse
import json
import concurrent.futures
from threading import Thread
import urllib.request
from bs4 import BeautifulSoup
import time

# Leer el archivo JSON y cargar el diccionario
with open('mi_buscador/raiz_ind_inv.txt', 'r') as file:
    contenido = file.read()
    diccionario = json.loads(contenido)

def obtener_titulo(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        return title
    except Exception as e:
        print(f"No se pudo obtener el título de {url}")
        return ""

def buscar_palabra_clave(palabra_clave, diccionario):
    resultados = []


    if palabra_clave in diccionario:
        urls = diccionario[palabra_clave]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futuros = {executor.submit(obtener_titulo, url): (url, relevancia) for url, relevancia in urls}

            # Esperar a que todas las tareas se completen
            concurrent.futures.wait(futuros)

            # Obtener resultados ordenados por relevancia
            resultados_ordenados = sorted(futuros, key=lambda x: futuros[x][1], reverse=True)

            for resultado in resultados_ordenados:
                url, relevancia = futuros[resultado]
                try:
                    titulo = resultado.result()
                    resultados.append({
                        'url': url,
                        'titulo': titulo,
                        'relevancia': relevancia
                    })
                except Exception as e:
                    print(f"No se pudo obtener el título de {url}")

    return resultados

def buscar(request):
    resultados_totales = []

    start_time = time.time()
    
    if 'palabras_clave' in request.GET:
        palabras_clave = request.GET['palabras_clave'].split()

        for palabra_clave in palabras_clave:
            try:
                palabra = Palabra.objects.get(nombre=palabra_clave)
                urls = URL.objects.filter(palabra=palabra)
                resultados_palabra = buscar_palabra_clave(palabra_clave, diccionario)
                resultados_totales.append({'palabra_clave': palabra_clave, 'resultados': resultados_palabra})
            except Palabra.DoesNotExist:
                pass
        
        end_time = time.time()
        tiempo_total = end_time - start_time

        return render(request, 'buscador/resultados.html', {'resultados_totales': resultados_totales, 'tiempo_total': tiempo_total})
    
    return render(request, 'buscador/buscar.html')
