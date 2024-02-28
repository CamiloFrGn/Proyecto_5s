import pandas as pd
import re

#create DataFrame
df = pd.DataFrame({'team' : ['Mavs?', 'Nets -', 'Kings!!', 'Spurs%', '&Heat&'],
                   'points' : [12, 15, 22, 29, 24]})

df['team'] = df['team'].str.replace('\W', '', regex=True)
df['team']=re.sub("[$@&]","",s)
#view DataFrame
print(df)