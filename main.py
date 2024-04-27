# chat conversation
import json
import pymysql
import requests
import http.client
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from datetime import datetime, timedelta
import calendar

from itertools import cycle

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_DDBB = os.getenv("DB_DDBB")
#try:
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_DDBB)
cursor = connection.cursor()

@app.route("/", methods=["POST"])
@cross_origin()
def function(self):
    
    #try:
    
    fecha_inicio = str(request.json['fechaInicio'])
    fecha_fin = str(request.json['fechaFin'])
    
    frecuencia = str(request.json['frecuencia'])
    recurrencia = int(request.json['recurrencia'])
    dia = str(request.json['dia'])
    orden = str(request.json['orden'])

    # Generar las fechas de las citas
    repeticiones = calcular_fechas(fecha_inicio, fecha_fin, frecuencia, recurrencia, dia, orden)
    #print("Ejemplo 2:", repeticiones)

    # Insertar las fechas en la tabla MySQL
    insertar_fechas(repeticiones, frecuencia, orden)

    retorno = {
            "estado":True,
            "detalle":"success!!"
        }

    #except Exception as e:
    #    print('Error: '+ str(e))
    #    retorno = {
    #        "estado":False,
    #        "detalle":"fail!!"
    #    }
    return retorno

def calcular_fechas(fecha_inicio, fecha_fin, frecuencia, recurrencia, dia, orden):
    # Convertir las fechas de inicio y fin a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    # Crear una lista para almacenar las fechas de las repeticiones
    fechas_repeticiones = []

    # Definir el incremento según la frecuencia
    incremento = {'diaria': timedelta(days=recurrencia),
                  'semanal': timedelta(weeks=recurrencia),
                  'mensual': timedelta(days=30*recurrencia)}  # Aproximación mensual

    # Calcular las fechas de las repeticiones
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        if frecuencia == 'mensual':
            # Asegurarse de estar en el primer día del mes
            fecha_actual = fecha_actual.replace(day=1)
            # Encontrar el día de la semana correspondiente al dia
            dia_dia = dia_to_weekday(dia)
            # Mover al siguiente mes
            fecha_actual += timedelta(days=30*recurrencia)
            # Encontrar el día de la semana del primer día del siguiente mes
            while fecha_actual.weekday() != dia_dia:
                fecha_actual += timedelta(days=1)
            # Ajustar la fecha al orden especificado
            fecha_actual = ajustar_fecha_al_orden(fecha_actual, orden, dia_dia)
        fechas_repeticiones.append(fecha_actual.strftime('%Y-%m-%d'))
        fecha_actual += incremento[frecuencia]

    return fechas_repeticiones

def dia_to_weekday(dia):
    dias_semana = {'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5, 'domingo': 6}
    return dias_semana[dia]

def ajustar_fecha_al_orden(fecha, orden, dia_dia):
    # Encontrar el día de la semana del primer día del mes
    primer_dia_mes = fecha.replace(day=1)
    while primer_dia_mes.weekday() != dia_dia:
        primer_dia_mes += timedelta(days=1)
    # Encontrar el primer día de la semana correspondiente al día especificado
    primer_dia_semana = primer_dia_mes + timedelta(days=(dia_dia - primer_dia_mes.weekday()) % 7)
    # Ajustar la fecha al orden especificado
    if orden == 'primero':
        return primer_dia_semana
    elif orden == 'segundo':
        return primer_dia_semana + timedelta(weeks=1)
    elif orden == 'tercero':
        return primer_dia_semana + timedelta(weeks=2)
    elif orden == 'cuarto':
        return primer_dia_semana + timedelta(weeks=3)
    else:
        raise ValueError("El orden especificado no es válido.")

# Conexión a MySQL y función para insertar fechas en la tabla
def insertar_fechas(fechas, frecuencia, orden_dia_semana):
    horaIni = str(request.json['horaIni'])
    horaFin = str(request.json['horaFin'])
    modalidad = str(request.json['modalidad'])
    id_user = str(request.json['id_user'])
    tipo = 'profesional'
    id_bloque = 1
    repeticiones = 0

    #insertar_fechas(fechas_citas, frecuencia, recurrencia, orden_dia_semana, orden_numero)


    try:
        for fecha in fechas:
            sql_insertar = 'INSERT INTO '+DB_DDBB+'.disponibilidades'+'''
                (id_bloque, id_user, tipo, día, fechaInicio, fechaFin, repeticiones, horaIni, horaFin, modalidad, frecuencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                '''
            print('INSERT:'+sql_insertar)
            #print(str(id_bloque)+", "+str(id_user)+", "+str(tipo)+", "+str(dia)+", "+str(fechaInicio)+", "+str(fechaFin)+", "+str(repeticiones)+", "+str(horaIni)+", "+str(horaFin)+", "+str(modalidad)+", "+str(frecuencia))
            cursor.execute(sql_insertar,(id_bloque, id_user, tipo, orden_dia_semana, fecha, fecha, repeticiones, horaIni, horaFin, modalidad, frecuencia))

            #cursor.execute("INSERT INTO citas (fecha) VALUES (%s)", (fecha,))
        connection.commit()
        print(f"Se han insertado {len(fechas)} fechas.")
    except Error as e:
        print("Error al conectar con MySQL:", e)

if __name__ == "__main__":
    app.run(debug=True, port=8002, ssl_context='adhoc')