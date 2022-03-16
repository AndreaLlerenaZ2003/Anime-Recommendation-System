# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 12:49:42 2022

@author: aplle
"""

from tkinter import*
import tkinter as tk
import numpy as np 
import pandas as pd 
import warnings
import scipy as sp 
from sklearn.metrics.pairwise import cosine_similarity

pd.options.display.max_columns
warnings.filterwarnings("always")
warnings.filterwarnings("ignore")

def alinear_esquina_superior_izquierda(r):
    r.geometry("+0+0")


def alinear_esquina_inferior_derecha(r):
    r.geometry("-0-0")


def alinear_esquina_inferior_izquierda(r):
    r.geometry("+0-0")


def alinear_esquina_superior_derecha(r):
    r.geometry("-0+0")

def centrar(r):
    altura = r.winfo_reqheight()
    anchura = r.winfo_reqwidth()
    altura_pantalla = r.winfo_screenheight()
    anchura_pantalla = r.winfo_screenwidth()
    x = (anchura_pantalla // 2) - (anchura//2)
    y = (altura_pantalla//2) - (altura//2)
    r.geometry(f"+{x}+{y}")



raiz = tk.Tk()
raiz.geometry("500x380")
raiz.title("RecomendaciónAnimes")

raiz.etiqueta = tk.Label(raiz, text="Sistema de recomendacion de anime",font="Helvetica 10 bold")

raiz.etiqueta.pack(side="top")

raiz.update()

centrar(raiz)
raiz.etiqueta.place(x=124,y=3,height=50)
raiz.update()                        
app = tk.Frame()
app.pack()

lbl1 = Label(raiz,text = "Buscar anime similiar a: ",bg="yellow")
lbl1.place(x=10,y=55,width=140,height=30)

#txt1 = tk.Entry(raiz,bg="pink")
#txt1.place(x=170,y=55,width=200,height=30)

entrada = tk.StringVar()
tk.Entry(raiz,bg="pink", textvariable=entrada, width=30).place(x=170, y=55,width=200,height=30)

lbl2 = Label(raiz,text = "Animes similares: ",bg="yellow")
lbl2.place(x=10,y=150,width=100,height=30)




resultados =  tk.Label(raiz,bg="pink")
resultados.place(x=130,y=150,width=350,height=180)




def SistemadeRecomendaciondeAnime():
    result=entrada.get()
    anime_data = pd.read_csv('./anime.csv')
    #print(anime_data.head(5))
    rating_data = pd.read_csv('./rating.csv')
    #print(rating_data.head(5))
    
    # borrar datos con 0 rating
    anime_data=anime_data[~np.isnan(anime_data["rating"])]
    anime_data['genre'] = anime_data['genre'].fillna(anime_data['genre'].dropna().mode().values[0])

    anime_data['type'] = anime_data['type'].fillna(anime_data['type'].dropna().mode().values[0])
    #vemos si hay nulos
    #print(anime_data.isnull().sum())
    rating_data['rating'] = rating_data['rating'].apply(lambda x: np.nan if x==-1 else x)
    #print(rating_data.head(20))
    
    #buscmaos que solo se recomiende series de anime
    anime_data = anime_data[anime_data['type']=='TV']
    #buscamos crear un dataFrame que junte los anteriores por ID
    DataJunta = rating_data.merge(anime_data, left_on = 'anime_id', right_on = 'anime_id', suffixes= ['_user', ''])
    DataJunta = DataJunta[['user_id', 'name', 'rating']]
    #Utilizamos nuestra data de los primeros 8000 usuarios
    DataJunta_8000 =  DataJunta[DataJunta.user_id <= 8000]
    #print(DataJunta_8000.head(5))
    
    #USUARIOS FILAS --- ANIMES COLUMNAS
    aux = DataJunta_8000.pivot_table(index=['user_id'], columns=['name'], values='rating')
    #print("aqui vemos el aux")
    #print(aux.head(5))
    
    
    #normalizamos lo valores para poder hacer comparaciones respecto a conjuntos de elementos y a la media.
    aux2 = aux.apply(lambda x: (x-np.mean(x))/(np.max(x)-np.min(x)), axis=1)
    
   
    
    #Rellenamos los espacios vacios con 0
    aux2.fillna(0, inplace=True)

    #ponemos todos los elemtentos de la fila a la columna y los de la columna a la fila
    aux2 = aux2.T
   
    #solo nos quedamos con las columnas que no tengan  0
    aux2 = aux2.loc[:, (aux2 != 0).any(axis=0)]
    #Convetimos el dataframe a una matriz dispersa pues los usuarios no califican los ítems que van visitando
    aux3 = sp.sparse.csr_matrix(aux2.values)
    
    # Aplicamos el modelo basado en la similaridad // similitud de coseno
    animeSimilaridad = cosine_similarity(aux3)
    
    DataSimilaridadAnime = pd.DataFrame(animeSimilaridad, index = aux2.index, columns = aux2.index)
    
    def RecomendaciondeAnime(ANIME):
        cad = ""
        number = 1
        cad = cad+ 'Recomendados por que viste {}:\n'.format(ANIME)
        #cad = cad + "\n"
    
        for anime in  DataSimilaridadAnime.sort_values(by = ANIME, ascending = False).index[1:6]:
          cad = cad + "\n" + f'#{number}: {anime}, {round( DataSimilaridadAnime[anime][ANIME]*100,2)}% similaridad'
          number +=1
        
        
        #print(cad)
        resultados =  tk.Label(raiz,bg="pink",text=cad)
        resultados.place(x=130,y=150,width=350,height=180)
        
        
    try:
      RecomendaciondeAnime(result)
    except:
        cad = "No se encuentro el anime buscado para recomendar"
        #print(cad)
        resultados =  tk.Label(raiz,bg="pink",text=cad)
        resultados.place(x=130,y=150,width=350,height=180)
        
    


   
    


    
boton = tk.Button(text="BUSCAR",font="Helvetica 8 bold",command=SistemadeRecomendaciondeAnime)
boton.place(x=230, y=110)


    
    





app.mainloop()


