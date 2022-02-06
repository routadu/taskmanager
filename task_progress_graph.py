import matplotlib.pyplot as plt
import sqlite3 as sql
import numpy as np 
from datetime import datetime as dt

a = sql.connect('./AppData/local_data')
c = a.cursor()

c.execute('select * from task_progress_list')

bfr = c.fetchall()

progress = []
recommended = []
for i in bfr:
    if not dt.strptime(i[0],"%d-%m-%Y") > dt.now():
        progress.append(i[1]*100/i[2])
        recommended.append(70)
    
x = np.arange(len(progress))

plt.plot(x,progress,'b')
plt.plot(x,recommended,'r')
plt.show()
