import sys
import pandas as pd


def get_clients(plant,today_date_dt,relativedelta,query_sql_df):
    try:
    
        sql_call_client_list = "{CALL sld_v2_client_list_plant (?,?,?)}"
        startdate = today_date_dt - relativedelta(months=+3)
        startdate = startdate.replace(day=1)
        startdate = startdate.strftime("%Y-%m-%d")
        today_date_string = today_date_dt.strftime("%Y-%m-%d")
        client_list = query_sql_df(sql_call_client_list,(plant,startdate,today_date_string))
        return client_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def volumen_attribute(plant,query_sql_df):
    try:
       
        weight = 0.35
        sql_call_client_list = "{CALL sld_v2_volume_attribute_plant (?)}"
        df_volumen_attribute = query_sql_df(sql_call_client_list,(plant))
        df_volumen_attribute['volume'] = df_volumen_attribute['volume'].astype(float)
        df_volumen_attribute['volume'] = df_volumen_attribute['volume'].fillna(0)
        df_volumen_attribute = df_volumen_attribute.sort_values(by=["volume"], ascending=[False])
        max_value = pd.DataFrame()
        max_value['volume'] = df_volumen_attribute['volume']
        max_value = max_value.loc[max_value['volume'].idxmax()]
        max_value = max_value/5
     
        range1 = max_value[0]
        range2 = max_value[0]*2
        range3 = max_value[0]*3
        range4 = max_value[0]*4


        def conditions(df_volumen_attribute):
            if (df_volumen_attribute['volume'] <= range1 ):
                x = (0.2*weight)*100
            if (df_volumen_attribute['volume'] > range1 ) and (df_volumen_attribute['volume'] <= range2 ):
                x = (0.4*weight)*100
            if (df_volumen_attribute['volume'] > range2 ) and (df_volumen_attribute['volume'] <= range3 ):
                x = (0.6*weight)*100
            if (df_volumen_attribute['volume'] > range3 ) and (df_volumen_attribute['volume'] <= range4 ):
                x = (0.8*weight)*100
            if (df_volumen_attribute['volume'] > range4 ):
                x = (weight)*100
            return x
        
        df_volumen_attribute['volume_final'] = df_volumen_attribute.apply(conditions, axis=1)
        
        return df_volumen_attribute
    except Exception as e:
        print(str(e))
        sys.exit() 

def profits_attribute(query_sql_df,get_clients_df):
    try:
       
        weight = 0.15
        sql_call_client_list = "select * from sld_profits"
        profits_list = query_sql_df(sql_call_client_list,())
        profits_list = pd.merge(get_clients_df['Cliente'],profits_list,on="Cliente",how="left")
        profits_list['mc'] = profits_list['mc'].fillna(0)
        profits_list['update_date'] = profits_list['update_date'].fillna(profits_list['update_date'][0])
        profits_list['mc'] = profits_list['mc'].astype(float)
        profits_list = profits_list.sort_values(by=["mc"], ascending=[False])
        max_value = pd.DataFrame()
        max_value['mc'] = profits_list['mc']
        max_value = max_value.loc[max_value['mc'].idxmax()]
        def conditions(profits_list):
            if (profits_list['mc'] <= 0):
                x = (0*weight)*100
            if (profits_list['mc'] > 0):
                x = (profits_list['mc']/max_value)*weight*100
            return x
        
        profits_list['profits_final'] = profits_list.apply(conditions, axis=1)


        return profits_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def payment_discipline_attribute(query_sql_df):
    try:
        weight = 0.15
        sql_call_client_list = "select * from sld_payment_discipline"
        payment_discipline_list = query_sql_df(sql_call_client_list,())
        payment_discipline_list['value_discipline'] = payment_discipline_list['value_discipline'].astype(float)
        payment_discipline_list['value_discipline'] = payment_discipline_list['value_discipline'].fillna(5)
        payment_discipline_list['payment_discipline_final'] = payment_discipline_list['value_discipline']*weight*(100/5)
        return payment_discipline_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def time_in_site_attribute(plant,today_date_dt,relativedelta,query_sql_df):
    try:
      
        weight = 0.05
        sql_call_client_list = "{CALL sld_v2_time_in_site_attribute_plant (?,?,?)}"
        startdate = today_date_dt - relativedelta(months=+2)
        startdate = startdate.replace(day=1)
        startdate = startdate.strftime("%Y-%m-%d")
        today_date_string = today_date_dt.strftime("%Y-%m-%d")
        df_time_in_site_attribute = query_sql_df(sql_call_client_list,(plant,startdate,today_date_string))
        df_time_in_site_attribute['avg_time'] = df_time_in_site_attribute['avg_time'].astype(float)
        df_time_in_site_attribute['avg_time'] = df_time_in_site_attribute['avg_time'].fillna(0)

        def conditions(df_time_in_site_attribute):
            if (df_time_in_site_attribute['avg_time'] < 30):
                x = (1*weight)*100
            if (df_time_in_site_attribute['avg_time'] >= 30) and (df_time_in_site_attribute['avg_time'] < 45):
                x = (0.8*weight)*100
            if (df_time_in_site_attribute['avg_time'] >= 45) and (df_time_in_site_attribute['avg_time'] < 60):
                x = (0.6*weight)*100
            if (df_time_in_site_attribute['avg_time'] >= 60) and (df_time_in_site_attribute['avg_time'] < 90):
                x = (0.4*weight)*100
            if (df_time_in_site_attribute['avg_time'] >= 90) and (df_time_in_site_attribute['avg_time'] < 120):
                x = (0.2*weight)*100
            if (df_time_in_site_attribute['avg_time'] >= 120):
                x = 0

            return x
        
        df_time_in_site_attribute['time_in_site_final'] = df_time_in_site_attribute.apply(conditions, axis=1)

        return df_time_in_site_attribute
    except Exception as e:
        print(str(e))
        sys.exit() 

def tools_adoption_attribute(query_sql_df,get_clients_df):
    try:
        
        weight = 0.1
        sql_call_client_list = "select Cliente, sum(total) as total, sum(cxgo) as cxgo from sld_use_tools where delivery_date >= DATEADD(month,-2,getdate()) group by Cliente"
        tools_adoption_list = query_sql_df(sql_call_client_list,())
        tools_adoption_list = pd.merge(get_clients_df['Cliente'],tools_adoption_list,on="Cliente",how="left")
        tools_adoption_list['total'] = tools_adoption_list['total'].fillna(1)
        tools_adoption_list['cxgo'] = tools_adoption_list['cxgo'].fillna(0)
        tools_adoption_list['cxgo'] = tools_adoption_list['cxgo'].astype(int)
        tools_adoption_list['total'] = tools_adoption_list['total'].astype(int)
        tools_adoption_list['%tools_adoption'] = tools_adoption_list['cxgo']/tools_adoption_list['total']
        tools_adoption_list = tools_adoption_list.drop(['total','cxgo'], axis=1)
        tools_adoption_list['%tools_adoption'] = tools_adoption_list['%tools_adoption'].astype(float)
        tools_adoption_list = tools_adoption_list.sort_values(by=["%tools_adoption"], ascending=[False])
        
        tools_adoption_list['tools_adoption_final'] = tools_adoption_list['%tools_adoption']*weight*(100)


        return tools_adoption_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def brandvis_growthpot_attribute(query_sql_df):
    try:
        weight_bv = 0.2
        
        sql_call_client_list = "select * from sld_brandvis_growth"
        brand_growth_list = query_sql_df(sql_call_client_list,())
        brand_growth_list = brand_growth_list.drop(['growth_pot'],axis=1)

        def conditions_brand(brand_growth_list):
            if (brand_growth_list['brand_vis'] == "SI" ):
                x = weight_bv
            else:
                x = 0
            return x
        brand_growth_list['brand_visibility_final'] = brand_growth_list.apply(conditions_brand, axis=1)


        return brand_growth_list
    except Exception as e:
        print(str(e))
        sys.exit() 