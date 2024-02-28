import sys
sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\Proyectos-Cemex\otros\proyectos_cemex\sld_v2\ranking')

def main_app(cluster,paramrandom):
 
    if cluster == "CLUSTER CENTRO":
        from centro.app.app import main_centro
        x = main_centro(cluster,paramrandom)
    if cluster == "CLUSTER ANTIOQUIA":
        from antioquia.app_an.app import main_antioquia
        x = main_antioquia(cluster,paramrandom)
    if cluster == "SANTO DOMINGO":
        from santo_domingo.app_santodom.app import main_santodom
        x = main_santodom(cluster,paramrandom)
    if cluster == "Panama":
        from panama.app_pan.app import main_pan
        x = main_pan(cluster,paramrandom)
    if cluster == "ZONA SUR":
       from zona_sur.app_zsur.app import main_zona_sur
       x = main_zona_sur(cluster,paramrandom)
    if cluster == 'CLUSTER METROPOLITANA':
        from metropolitana.app_metropo.app import main_metropo
        x = main_metropo(cluster,paramrandom)
    
    return x