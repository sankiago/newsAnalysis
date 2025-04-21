import pandas as pd

row1 = {'keyword':1, 'content':'hola', 'xd': 'ajá'}
row2 = {'keyword':2, 'content':'amiguitos', 'xd': 'y'}
row3 = {'keyword':1, 'content':'de', 'xd': 'tu'}
row4 = {'keyword':2, 'content':'youtube', 'xd': 'q'}
row5 = {'keyword':1, 'content':'aquí', 'xd': 'enton'}
row6 = {'keyword':2, 'content':'un', 'xd': 'si'}
row7= {'keyword':1, 'content':'nuevo', 'xd': 'nop'}


df = pd.DataFrame([row1, row2, row3, row4, row5, row5, row6, row7])
df_mod = df.groupby('keyword').agg(r'\n---\n'.join).reset_index()
print(df_mod)