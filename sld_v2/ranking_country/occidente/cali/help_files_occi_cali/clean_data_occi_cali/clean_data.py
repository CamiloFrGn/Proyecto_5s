import pandas as pd
import numpy as np
import sys


def clean_data(get_clients_df,volumen_attribute_df,
                       time_in_site_attribute_df,profits_attribute_df,
                       payment_discipline_attribute_df,tools_adoption_attribute_df,brandvis_growthpot_attribute_df,cluster,plant):
    try:
      

        #start merging
        #merge volume
        df = pd.merge(get_clients_df,volumen_attribute_df,on="Cliente",how="left")
        
        #merge time in site
        df = pd.merge(df,time_in_site_attribute_df,on="Cliente",how="left")
        #merge profits
        df = pd.merge(df,profits_attribute_df,on="Cliente",how="left")
        #merge payment discipline
        df = pd.merge(df,payment_discipline_attribute_df,on="Cliente",how="left")
        #merge tools adoption
        df = pd.merge(df,tools_adoption_attribute_df,on="Cliente",how="left")
        #merge brand visibility
        df = pd.merge(df,brandvis_growthpot_attribute_df,on="Cliente",how="left")
        
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

        df['avg_time'] = df['avg_time'].fillna(0)
        df['time_in_site_final'] = df['time_in_site_final'].fillna(0)
        
        df['mc'] = df['mc'].fillna(0)
        df['profits_final'] = df['profits_final'].fillna(0)
        df['profits_final'] = round(df['profits_final'],2)
        df['update_date'] = df['update_date'].fillna(df['update_date'][0])

        df['value_discipline'] = df['value_discipline'].fillna(5)
        df['value_discipline'] = round(df['value_discipline'],2)
        df['payment_discipline_final'] = df['payment_discipline_final'].fillna(15)
        df['payment_discipline_final'] = round(df['payment_discipline_final'],2)

        df['%tools_adoption'] = df['%tools_adoption'].fillna(0)
        df['tools_adoption_final'] = df['tools_adoption_final'].fillna(0)

        df['brand_vis'] = df['brand_vis'].fillna("NO")
        df['brand_visibility_final'] = df['brand_visibility_final'].fillna(0)
        
        #create total points column
        df['total_points'] = round(df['volume_final']+
                              df['time_in_site_final']+
                              df['profits_final']+
                              df['payment_discipline_final']+
                              df['tools_adoption_final']+
                              df['brand_visibility_final'],2)

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
            if (df['% cumulative vol'] < 0.35):
                x = "PLATINUM"
            if (df['% cumulative vol'] >= 0.35) and (df['% cumulative vol'] < 0.60):
                x = "GOLD"
            if (df['% cumulative vol'] >=0.60):
                x = "SILVER"
            if (df['total_points'] == max_value):
                x = "PLATINUM"
                        
            return x
        
        df['sld'] = df.apply(conditions, axis=1)
        df['ranking'] = np.arange(1, len(df) + 1)
        
        df['cluster'] = cluster
        df['planta'] = plant
        df = df.rename(columns={'NombreCliente':'nombre_cliente'})
        df = df.rename(columns={'Cliente':'cliente'})
        df = df[['cluster','planta','cliente','sld','nombre_cliente','ranking']]

        return df

        
    except Exception as e:
        print(str(e))
        sys.exit()