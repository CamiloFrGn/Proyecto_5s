import sys
#sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\sld\ranking')
sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\Proyectos-Cemex\otros\proyectos_cemex\sld_v2\ranking')

def main_app_plant(cluster,plant,paramrandom):
    if cluster == "CLUSTER SANTANDER":
        if plant == "F015":
            from santander.cucuta.app_san_cuc.app import main_cucuta
            x = main_cucuta(plant)
        if plant == "F066":
            from santander.florida.app_san_flor.app import main_florida
            x = main_florida(plant)
    if cluster == "CLUSTER SURORIENTE":
        if plant == "F055":
            from suroriente.sumapaz.app_suro_sumapaz.app import main_sumapaz
            x = main_sumapaz(plant)
        if plant == "F061":
            from suroriente.neiva.app_suro_neiva.app import main_neiva
            x = main_neiva(plant)
        if plant == "FA04":
            from suroriente.ibague.app_suro_ibague.app import main_ibague
            x = main_ibague(plant)
        if plant == "FB63":
            from suroriente.fusa.app_suro_fusa.app import main_fusa
            x = main_fusa(plant)
    if cluster == "CLUSTER OCCIDENTE":
        if plant == "FB91" or plant == "F009":
            from occidente.cali.app_occi_cali.app import main_cali
            x = main_cali(plant)
        if plant == "F012":
            from occidente.pereira.app_occi_pereira.app import main_pereira
            x = main_pereira(plant)
        if plant == "F075":
            from occidente.tulua.app_occi_tulua.app import main_tulua
            x = main_tulua(plant)
    if cluster == "CLUSTER PANAMA":
        if plant == "G413" or plant == "G406":
            plant = "G413"
            from panama.juandiaz.app_juandiaz.app import main_juandiaz
            x = main_juandiaz(plant)
    if cluster == "Panama Oeste":
        if plant == "G407":
            from panama.vacamonte.app_vacamonte.app import main_vacamonte
            x = main_vacamonte(plant)
    return x
