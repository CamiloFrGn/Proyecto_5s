import sys
import os


current_dir = os.getcwd()
path_file = r"Documents\Proyectos-Cemex\sld_v2\ranking_country"
wrk_direc = os.path.join(current_dir,path_file)
sys.path.insert(0, wrk_direc)


def main_app():
    try:
        plant = "G421"
        from panama.lineatres.app_lineatres.app import main_lineatres
        main_lineatres(plant)
        plant = "G407"
        from panama.planta_vacamonte.app_vacamonte.app import main_vacamonte
        main_vacamonte(plant)
        plant = "G413"
        from panama.juan_diaz.app_juandiaz.app import main_juandiaz
        main_juandiaz(plant)
        cluster = "CLUSTER CENTRO"
        from centro.app.app import main_centro
        main_centro(cluster)
        print("cluster centro")
        cluster = "CLUSTER ANTIOQUIA"
        from antioquia.app_an.app import main_antioquia
        main_antioquia(cluster)
        plant = "F015"
        from santander.cucuta.app_san_cuc.app import main_cucuta
        main_cucuta(plant)
        plant = "F066"
        from santander.florida.app_san_flor.app import main_florida
        main_florida(plant)
        plant = "F055"
        from suroriente.sumapaz.app_suro_sumapaz.app import main_sumapaz
        main_sumapaz(plant)
        plant = "F061"
        from suroriente.neiva.app_suro_neiva.app import main_neiva
        main_neiva(plant)
        plant = "FA04"
        from suroriente.ibague.app_suro_ibague.app import main_ibague
        main_ibague(plant)
        plant = "FB63"
        from suroriente.fusa.app_suro_fusa.app import main_fusa
        main_fusa(plant)
        plant = "FB91"
        from occidente.cali.app_occi_cali.app import main_cali
        main_cali(plant)
        plant = "F012"
        from occidente.pereira.app_occi_pereira.app import main_pereira
        main_pereira(plant)
        plant = "F075"
        from occidente.tulua.app_occi_tulua.app import main_tulua
        main_tulua(plant)    
        cluster = "SANTO DOMINGO"
        from santo_domingo.app_santodom.app import main_santodom
        main_santodom(cluster)
        cluster = "ZONA SUR"
        from zona_sur.app_zsur.app import main_zona_sur
        main_zona_sur(cluster)
        cluster = 'CLUSTER METROPOLITANA'
        from metropolitana.app_metropo.app import main_metropo
        main_metropo(cluster)

        print("finished")
    except Exception as e:
        print(str(e))

main_app()
    
