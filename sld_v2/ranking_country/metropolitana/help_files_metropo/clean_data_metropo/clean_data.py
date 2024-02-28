import pandas as pd
import sys
import numpy as np

def clean_data(get_clients_df,volumen_attribute_df,cancelations_attribute_df,profits_attribute_df,
time_in_site_attribute_df,cluster):
    try:

        #start merging
        #merge volume
        df = pd.merge(get_clients_df,volumen_attribute_df,on="Cliente",how="left")
        #merge cancelations
        df = pd.merge(df,cancelations_attribute_df,on="Cliente",how="left")
        #merge profits
        df = pd.merge(df,profits_attribute_df,on="Cliente",how="left")
        #merge time in site
        df = pd.merge(df,time_in_site_attribute_df,on="Cliente",how="left")
        
        
        #CREATE participation column for volumen and then change to position 4
        vol_total = df['volume'].sum()
        df['% participation'] = df['volume'] / vol_total
        # Pop the column 'E' from its current position
        participation = df.pop('% participation')
        # Insert the popped column 'E' at position 1
        df.insert(4, '% participation', participation)
        
        #clean nan values
        df['volume'] = df['volume'].fillna(0)
        df['% participation'] = df['% participation'].fillna(0)
        df['volume_final'] = df['volume_final'].fillna(0)
        
        df['mc'] = df['mc'].fillna(0)
        df['profits_final'] = df['profits_final'].fillna(0)
        df['profits_final'] = round(df['profits_final'],2)
        df['update_date'] = df['update_date'].fillna(df['update_date'][0])
        
        
        df['vol_cancelado'] = df['vol_cancelado'].fillna(0)
        df['cancelations_final'] = df['cancelations_final'].fillna(0)
        df['cancelations_final'] = round(df['cancelations_final'],2)

        df['avg_time'] = df['avg_time'].fillna(0)
        df['time_in_site_final'] = df['time_in_site_final'].fillna(0)
        df['time_in_site_final'] = round(df['time_in_site_final'],2)

        

        


        #create total points column
        df['total_points'] = round(df['volume_final']+
                              df['cancelations_final']+
                              df['profits_final']+
                              df['time_in_site_final']
                             ,2)

        #sort values by total points and volume
        df = df.sort_values(by=["total_points","volume"], ascending=[False,False])

        #create cumulative vol
        df['% cumulative vol'] = df['% participation'].cumsum(axis=0)
        
        
        max_value = pd.DataFrame()
        max_value['total_points'] = df['total_points']
        max_value = max_value.loc[max_value['total_points'].idxmax()]
        max_value = max_value[0]
        #create sld column
        def conditions(df):
            if (df['% cumulative vol'] < 0.25):
                x = "PLATINUM"
            if (df['% cumulative vol'] >= 0.25) and (df['% cumulative vol'] < 0.50):
                x = "GOLD"
            if (df['% cumulative vol'] >=0.50):
                x = "SILVER"
            if (df['total_points'] == max_value):
                x = "PLATINUM"
            
                      
            return x
        
        df['sld'] = df.apply(conditions, axis=1)
        df['ranking'] = np.arange(1, len(df) + 1)
        
        df['cluster'] = cluster
        df['planta'] = cluster
        df = df.rename(columns={'NombreCliente':'nombre_cliente'})
        df = df.rename(columns={'Cliente':'cliente'})
        df = df[['cluster','planta','cliente','sld','nombre_cliente','ranking']]
        

        return df

        
    except Exception as e:
        print(str(e))
        sys.exit()