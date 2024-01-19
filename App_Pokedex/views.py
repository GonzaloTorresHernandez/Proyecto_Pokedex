from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
import requests
import aiohttp

import time

#asincrona
import asyncio

#rutas
url_api = 'https://pokeapi.co/api/v2/'
#todos los pokemones
url_p_todos = f'{url_api}pokemon'
url_p_detalle = f'{url_api}pokemon-species/'

inicio = time.time()

async def lista_pokemones(nom_id_pokemon):
    # llamar del pokemon 0 al 151
    argumentos = {
            'offset': '0',
            'limit': '151'
        }
    respuesta_listaPoke = requests.get(url=url_p_todos, params=argumentos)

    if respuesta_listaPoke.status_code == 200:
        json_pokemones = respuesta_listaPoke.json()
        pokemones = json_pokemones.get('results', [])  
        lista_pokemones = []  

        tareas = []
        for pokemon in pokemones:
            #filtro
            if nom_id_pokemon in pokemon['name'] or nom_id_pokemon == pokemon['url'].split('/')[6]:
                tareas.append(buscar_datos_pokemon(pokemon))

        '''
        await -> se usa en funciones asincronas, significa que vamos a esperar que se resulva la operacion
                    antes de seguir ejecutando el codigo restante.
        asyncio.gather(*args) -> se utiliza para ejecutar múltiples coroutines(tareas) simultáneamente y esperar a que todas finalicen.
                             Toma como argumentos las coroutines que se ejecutarán en paralelo.

                             Puede resivir x tareas, como en este caso le pasamos *args -> con los elementos de una lista
        '''
        lista_pokemones = await asyncio.gather(*tareas)

        print((time.time())-inicio)

        return lista_pokemones

async def buscar_datos_pokemon(pokemon):  
    dic_pokemon = {}
    dic_pokemon['nombre'] = pokemon['name']
    numPoke = pokemon['url'].split('/')[6]
    dic_pokemon['numero'] = numPoke
    dic_pokemon['imagen'] = img_pokemon(numPoke)
    dic_pokemon['tipo'] = await tipo_pokemon(numPoke)
    return dic_pokemon
           
def img_pokemon(num_pokemon):
    #seleccionar la imagen
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{num_pokemon}.png"

async def tipo_pokemon(num_pokemon):
    #seleccionar tipos
    url_pokemon_unico = f'{url_p_todos}/{num_pokemon}/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url_pokemon_unico) as resp_datos_poke:
            json_datos_poke = await resp_datos_poke.json()

    lista_tipos_poke = []
    for datos in json_datos_poke['types']:
        lista_tipos_poke.append(datos['type']['name'])

    return lista_tipos_poke

def descripcion_pokemon(id_pokemon):
    url = f'{url_p_detalle}{id_pokemon}'
    response_pokemon = requests.get(url)

    if response_pokemon.status_code == 200:
        json_pokemon = response_pokemon.json()
        pokemon = json_pokemon.get('flavor_text_entries', [])  

        #descripcion del pokemon
        descrip = ''
        for texto in pokemon:
            if texto['language']['name'] == 'es' and texto['version']['name'] == 'omega-ruby':
                descrip = texto['flavor_text']
        return descrip

def info_pokemon(id_pokemon):
    url = f'{url_p_todos}/{id_pokemon}'
    resp_poke = requests.get(url)
    if resp_poke.status_code == 200:
        dict_pokemon = {}
        json_pokemon = resp_poke.json()
        #id
        dict_pokemon['numero'] = id_pokemon
        #nombre
        nombre = json_pokemon.get('forms', [])  
        dict_pokemon['nombre'] = nombre[0]['name']
        #imagen
        dict_pokemon['imagen'] = img_pokemon(id_pokemon)
        #altura
        altura = json_pokemon.get('height', []) 
        dict_pokemon['altura'] =altura/10 
        #peso
        peso = json_pokemon.get('weight', []) 
        dict_pokemon['peso'] =peso/10
        #tipos
        lista_tipos = []
        tipos = json_pokemon.get('types', [])
        for t in tipos:
            lista_tipos.append(t['type']['name'])
        dict_pokemon['tipo'] =lista_tipos
        #descripcion
        dict_pokemon['descripcion'] = descripcion_pokemon(id_pokemon)

        #stats
        #stats = json_pokemon.get('stats', [])
        #print(stats)

        return dict_pokemon


#HOME
class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buscar_pokemon = self.request.GET.get('buscar-pokemon') or ''
        context['pokemones'] = asyncio.run(lista_pokemones(buscar_pokemon))   
        return context
    
class Detalle_Pokemon(TemplateView):
    template_name = 'detalle_pokemon.html'

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       id_pokemon = self.kwargs.get('id')
       context['pokemon'] = info_pokemon(id_pokemon)
       return context



