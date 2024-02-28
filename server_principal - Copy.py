# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 15:06:28 2020

@author: jsdelgadoc
"""

from flask import Flask
from flask import send_file

from SegmentacionClientes import SegmentacionClientes
from MallaTurnos import MallaTurnosWebapp
from MateriasPrimas import DesagregacionMateriasPrimas

app = Flask(__name__)


@app.route("/", methods=['GET'])
def welcome():
    return "al servidor principal de aplicacion inhouse de Asignaciones Cemex"

@app.route("/segmentacion/<pais>/<dias>/<paramrandom>", methods=['GET'])
def generar_segmentacion(pais, dias, paramrandom):
    
    return SegmentacionClientes.segmentar_clientes( pais, int(dias), paramrandom)

@app.route("/malla/<planta>/<fecha>/<precargadores>/<jornada>/<anticipacion>/<paramrandom>", methods=['GET'])
def generarmallaturnos( planta, fecha, precargadores, jornada, anticipacion, paramrandom):
   
    return MallaTurnosWebapp.generarm( planta,fecha, precargadores, jornada, anticipacion, paramrandom )

@app.route("/malla2/<planta>/<fecha>/<precargadores>/<jornada>/<anticipacion>/<paramrandom>/<tipopedido>", methods=['GET'])
def generarmallaturnos2( planta, fecha, precargadores, jornada, anticipacion, paramrandom, tipopedido):
   
    return MallaTurnosWebapp.generarm2( planta,fecha, precargadores, jornada, anticipacion, paramrandom, tipopedido )

@app.route("/mmpp/<fecha>/<pais>/<paramrandom>", methods=['GET'])
def generar_desagregacion_mmpp(fecha, pais, paramrandom):
   
    return DesagregacionMateriasPrimas.exportar_materias_primas_programacion(fecha, pais)

if(__name__=="__main__"):
    app.run()