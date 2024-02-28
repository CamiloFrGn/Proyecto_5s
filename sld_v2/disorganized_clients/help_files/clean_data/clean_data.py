import pandas as pd
import numpy as np
import sys


def clean_data(dataset,dataset_clients):
    try:
        print("Cleaning data")
        #group dataset by cliente and volpartida
        df = dataset.groupby(['Cliente'])['VolPartida'].sum().reset_index()
        df['VolPartida'] = df['VolPartida'].fillna(0)  

        #group by cancel
        df_cancel = dataset.groupby(['Cliente'])['VolCancelado'].sum().reset_index()
        df_cancel['VolCancelado'] = df_cancel['VolCancelado'].fillna(0)

        #merge cancel and dispatch
        df = pd.merge(df,df_cancel,on="Cliente",how="left")

        #create vol programmed column
        df['Volumen Total'] = df['VolPartida'] + df['VolCancelado']
        #create %cancel column
        df['%cancel'] = df['VolCancelado']/df['Volumen Total']

        #get same day category
        #filter orders programmed in the same day as dispatch
        df_same_day = dataset[dataset['diascreado'] == 0]
        df_same_day = df_same_day.groupby(['Cliente'])['VolPartida'].sum().reset_index()
        #rename volpartida to avoid duplicate on merge
        df_same_day.rename(columns = {'VolPartida':'VolPartida_0'}, inplace = True)
        #get day before category
        #filter orders programmed in the day before dispatch
        df_day_before = dataset[dataset['diascreado'] == 1]
        df_day_before = df_day_before.groupby(['Cliente'])['VolPartida'].sum().reset_index()
        #rename volpartida to avoid duplicate on merge
        df_day_before.rename(columns = {'VolPartida':'VolPartida_1'}, inplace = True)
        #get 2 days 
        #filter orders programmed 2 days before dispatch
        df_2_days = dataset[dataset['diascreado'] == 2]
        df_2_days = df_2_days.groupby(['Cliente'])['VolPartida'].sum().reset_index()
        #rename volpartida to avoid duplicate on merge
        df_2_days.rename(columns = {'VolPartida':'VolPartida_2'}, inplace = True)
        #get 3 days or more category
        #filter orders programmed 3 days or more before dispatch
        df_3_days_more = dataset[dataset['diascreado'] >= 3]
        df_3_days_more = df_3_days_more.groupby(['Cliente'])['VolPartida'].sum().reset_index()
        #rename volpartida to avoid duplicate on merge
        df_3_days_more.rename(columns = {'VolPartida':'VolPartida_3'}, inplace = True)
        
        #start mergeing dataframes by cliente number
        df = pd.merge(df,df_same_day,on="Cliente",how="left")
        df = pd.merge(df,df_day_before,on="Cliente",how="left")
        df = pd.merge(df,df_2_days,on="Cliente",how="left")
        df = pd.merge(df,df_3_days_more,on="Cliente",how="left")
        #replace nan values with 0
        df['VolPartida_0'] = df['VolPartida_0'].fillna(0)
        df['VolPartida_1'] = df['VolPartida_1'].fillna(0)
        df['VolPartida_2'] = df['VolPartida_2'].fillna(0)
        df['VolPartida_3'] = df['VolPartida_3'].fillna(0)
        #create % columns
        df['% Same day'] = df['VolPartida_0']/df['VolPartida']
        df['% Day before'] = df['VolPartida_1']/df['VolPartida']
        df['% 2 days before'] = df['VolPartida_2']/df['VolPartida']
        df['% 3 days or more'] = df['VolPartida_3']/df['VolPartida']

        df['% Same day'] = df['% Same day'].fillna(0)
        df['% Day before'] = df['% Day before'].fillna(0)
        df['% 2 days before'] = df['% 2 days before'].fillna(0)
        df['% 3 days or more'] = df['% 3 days or more'].fillna(0)
        df['%cancel'] = df['%cancel'].fillna(0)

        #drop unneccesary columns
        df = df[df.columns.drop(list(df.filter(regex='VolPartida_')))]
        #order by % 3 days or more
        df = df.sort_values(by=["% 3 days or more",'% 2 days before','% Day before','% Same day','%cancel',
                                'Volumen Total'],
                            ascending=[True,True,True,True,False,True])
        df.rename(columns = {'VolPartida':'Volumen Despachado'}, inplace = True)
        #merge with dataset_clients
        df = pd.merge(df,dataset_clients,on="Cliente",how="left")
        #reorganize columns
        df = df.reindex(columns=['Cliente','NombreCliente','Volumen Total','Volumen Despachado',
                                 'VolCancelado','% Same day','% Day before','% 2 days before',
                                 '% 3 days or more','%cancel'])
        #filter out clients that have 0 total vol
        df = df[df['Volumen Total'] > 0] 

        df = df[df['NombreCliente'] != ''] 
        
        return df
    except Exception as e:
        print(str(e))
        sys.exit()