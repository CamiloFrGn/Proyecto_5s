import sys
import pandas as pd


def get_clients(cluster,today_date_dt,relativedelta,query_sql_df):
    try:

        sql_call_client_list = "{CALL sld_v2_client_list (?,?,?)}"
        startdate = today_date_dt - relativedelta(months=+3)
        startdate = startdate.replace(day=1)
        startdate = startdate.strftime("%Y-%m-%d")
        today_date_string = today_date_dt.strftime("%Y-%m-%d")
        client_list = query_sql_df(sql_call_client_list,(cluster,startdate,today_date_string))
        return client_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def volumen_attribute(cluster,today_date_dt,relativedelta,query_sql_df):
    try:

        weight = 0.3
  
        sql_call_client_list = "{CALL sld_v2_volume_attribute (?,?,?)}"
        startdate = today_date_dt - relativedelta(months=+6)
        startdate = startdate.replace(day=1)
        startdate = startdate.strftime("%Y-%m-%d")
        today_date_string = today_date_dt.strftime("%Y-%m-%d")
        df_volumen_attribute = query_sql_df(sql_call_client_list,(cluster,startdate,today_date_string))
        df_volumen_attribute['volume'] = df_volumen_attribute['volume'].astype(float)
        df_volumen_attribute['volume'] = df_volumen_attribute['volume'].fillna(0)

        def conditions(df_volumen_attribute):
            if (df_volumen_attribute['volume'] <= 2000 ):
                x = (0.15*weight)*100
            if (df_volumen_attribute['volume'] > 2000 ) and (df_volumen_attribute['volume'] <= 6000 ):
                x = (0.3*weight)*100
            if (df_volumen_attribute['volume'] > 6000 ) and (df_volumen_attribute['volume'] <= 10000 ):
                x = (0.5*weight)*100
            if (df_volumen_attribute['volume'] > 10000 ) and (df_volumen_attribute['volume'] <= 20000 ):
                x = (0.75*weight)*100
            if (df_volumen_attribute['volume'] > 20000 ):
                x = (1*weight)*100
       

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

def brandvis_growthpot_attribute(query_sql_df):
    try:

        weight_bv = 0.01
        weight_growth = 0.15
        sql_call_client_list = "select * from sld_brandvis_growth"
        brand_growth_list = query_sql_df(sql_call_client_list,())
        def conditions_brand(brand_growth_list):
            if (brand_growth_list['brand_vis'] == "SI" ):
                x = weight_bv
            else:
                x = 0
            return x
        brand_growth_list['brand_visibility_final'] = brand_growth_list.apply(conditions_brand, axis=1)
        
        def conditions_growth(brand_growth_list):
            if (brand_growth_list['growth_pot'] == "SI" ):
                x = weight_growth
            else:
                x = 0
            return x
        
        brand_growth_list['growth_potential_final'] = brand_growth_list.apply(conditions_growth, axis=1)


        return brand_growth_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def sales_recurrence_attribute(cluster,today_date_dt,relativedelta,query_sql_df):
    try:

        weight = 0.15
        sql_call_client_list = "{CALL sld_v2_recurrence_attribute (?,?,?)}"
        startdate = today_date_dt - relativedelta(months=+12)
        startdate = startdate.replace(day=1)
        startdate = startdate.strftime("%Y-%m-%d")
        today_date_string = today_date_dt.strftime("%Y-%m-%d")
        df_time_in_site_attribute = query_sql_df(sql_call_client_list,(cluster,startdate,today_date_string))
        df_time_in_site_attribute['count'] = 1
        df_time_in_site_attribute_pv = pd.pivot_table(df_time_in_site_attribute, values='count'
                                                   , index=['Cliente'], columns=['month_present']
                                                   , fill_value=0)
        column_order = df_time_in_site_attribute['month_present'].unique()
        df_time_in_site_attribute = df_time_in_site_attribute_pv.reindex(column_order, axis=1)
        df_time_in_site_attribute = df_time_in_site_attribute.reset_index()
        #df_time_in_site_attribute = df_time_in_site_attribute.drop(['month_present'], axis=1)   

        df_time_in_site_attribute['total_recurrence'] = 0
        for x in range(1,14):
            if x >= 1 and x <=3:
                multiplicador = round(0.5 - 0.125,1)
            if x >= 4 and x <=6:
                multiplicador = round(0.75 - 0.125,2)
            if x >= 7 and x <=9:
                multiplicador = round(1.25 - 0.125,2)
            if x >= 10:
                multiplicador = round(1.5 - 0.125,1)

            col_name = df_time_in_site_attribute.columns[x]
            df_time_in_site_attribute[col_name] = df_time_in_site_attribute[col_name] * multiplicador
            df_time_in_site_attribute['total_recurrence'] = round(df_time_in_site_attribute['total_recurrence'] + df_time_in_site_attribute[col_name],1)

        df_time_in_site_attribute = df_time_in_site_attribute[['Cliente', 'total_recurrence']]
        df_time_in_site_attribute = df_time_in_site_attribute.sort_values(by="total_recurrence", ascending=[False])
        df_time_in_site_attribute['recurrence_final'] = round(df_time_in_site_attribute['total_recurrence']*weight*(100/12),2)

        return df_time_in_site_attribute
    except Exception as e:
        print(str(e))
        sys.exit() 

def payment_discipline_attribute(query_sql_df):
    try:
   
        weight = 0.04
        sql_call_client_list = "select * from sld_payment_discipline"
        payment_discipline_list = query_sql_df(sql_call_client_list,())
        payment_discipline_list['value_discipline'] = payment_discipline_list['value_discipline'].fillna(5)
        payment_discipline_list['value_discipline'] = payment_discipline_list['value_discipline'].astype(float)
        payment_discipline_list['payment_discipline_final'] = payment_discipline_list['value_discipline']*weight*(100/5)
        return payment_discipline_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def unload_zone_safety_attribute(query_sql_df):
    try:

        weight = 0.15
        sql_call_client_list = "select * from sld_hs_safety_measures"
        safety_measures_list = query_sql_df(sql_call_client_list,())
        safety_measures_list['value_safety'] = safety_measures_list['value_safety'].astype(int)
        safety_measures_list['value_safety_final'] = safety_measures_list['value_safety']*weight*(100)
        return safety_measures_list
    except Exception as e:
        print(str(e))
        sys.exit() 

def time_in_site_attribute(cluster,today_date_dt,relativedelta,query_sql_df):
    try:
 
        weight = 0.05
        sql_call_client_list = "{CALL sld_v2_time_in_site_attribute (?,?,?)}"
        startdate = today_date_dt - relativedelta(months=+2)
        startdate = startdate.replace(day=1)
        startdate = startdate.strftime("%Y-%m-%d")
        today_date_string = today_date_dt.strftime("%Y-%m-%d")
        df_time_in_site_attribute = query_sql_df(sql_call_client_list,(cluster,startdate,today_date_string))
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
            if (df_time_in_site_attribute['avg_time'] >= 90):
                x = (0.2*weight)*100

            return x
        
        df_time_in_site_attribute['time_in_site_final'] = df_time_in_site_attribute.apply(conditions, axis=1)

        return df_time_in_site_attribute
    except Exception as e:
        print(str(e))
        sys.exit() 

