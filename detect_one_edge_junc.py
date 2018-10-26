
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
from datetime import datetime
import math


# In[2]:

#detect one-edge-connected-junction
#data = pd.read_excel('./Network_LA/uc6_locals_junc_pair_v1.xlsx')
#data_pos = pd.read_excel("./Network_LA/uc6_02_05_UTM_locals_ND_Junctions.xlsx")
#data = pd.read_excel('./Network_LA_uc1/join_junc_to_links_uc1_locals.xlsx')
#data_pos = pd.read_excel("./Network_LA_uc1/uc1_02_05_locals_ND_Junctions_UTM.xlsx")
#--- uc2
#data = pd.read_excel('./uc2_freeway/join_junc_to_links_uc2_freeways_v1.xlsx')
#data_pos = pd.read_excel("./uc2_freeway/uc2_00_01_freeways_W_N_ND2_Junctions_UTM.xlsx")
#--- uc3
data = pd.read_excel('./uc3_freeway/join_junc_to_links_uc3_freeways.xlsx')
data_pos = pd.read_excel("./uc3_freeway/uc3_00_01_N_E_ND_Junctions_UTM.xlsx")


# In[5]:

def Build_dict(dic,df):
    #print (df)
    #df = sorted(df,key=lambda x:x[1])
    #print ("ending building dictionary with one street name data")
    #testing_data = sorted(testing_data,key=lambda x:x[1])
    #print (testing_data)
    multiple_road = {} # store which junction coneected to more than two roads
    #dic = {} # store junction A connected to junction B
    street_id = {} # store pair of junction with the edge
    for i in range(len(df)):
        row = df.iloc[i,:]
        if row[1] not in dic:
            dic[row[1]] = [row[2]]
        elif row[2] not in dic[row[1]]:
            dic[row[1]].append(row[2])
        if row[2] not in dic:
            dic[row[2]] = [row[1]]
        elif row[1] not in dic[row[2]]:
            dic[row[2]].append(row[1])
        smaller,bigger = min(row[1],row[2]),max(row[1],row[2])
        if (smaller,bigger) in street_id:
            All_Deleted_Edge.append([row[0]])
            #street_id[(smaller,bigger)].append(row[0])
        else:
            street_id[(smaller,bigger)] = row[0]
    for num in dic:
        if len(set(dic[num])) >=2:
            multiple_road[num] = dic[num]
    #print ("end reading data")
    return multiple_road,street_id
def build_main_street_dic():
    for index,(LinkID,JID1,JID2,StName) in enumerate(zip(data['LinkID'],data['JID1'],data['JID2'],data['NAME'])):
        Main_StName = str(StName).split(" ")
        if Main_StName[0] in Direction:
            Main_StName = Main_StName[1:]
        if Main_StName[-1] in Direction:
            Main_StName = Main_StName[:-1]
        Main_StName= ''.join(Main_StName)
        Street_Name[Main_StName]= Street_Name.get(Main_StName,[])
        Street_Name[Main_StName].append(LinkID)


# In[6]:

def BFS(start,end):#seen saved the seen path
    queue = []
    queue.append([start])
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node in path[:-1]:#no circle is allowed
            return False
        if node == end:
            return path
        for adj in dic[node]:
            new_path = list(path)
            new_path.append(adj)
            queue.append(new_path)
    return False
        


# In[7]:

All_Deleted_Edge = []
#data = pd.read_excel('./Network_LA/uc6_locals_junc_pair_v1.xlsx')
Street_Name = {} # record which index is store in the name of streer
Direction = ['E','N','S','W']
build_main_street_dic() # call func
now = datetime.now()

Deleted_edge = []
for index,name in  enumerate(Street_Name):
    #print (name)
    #"PioneerBlvd" "HayvenhurstAve"
    df = data.loc[data['LinkID'].isin(Street_Name[name])] # find the all rows with same street name
    multiple_road = {} # store which junction coneected to more than two roads
    dic = {}
    multiple_road,street_id = Build_dict(dic,df)
    one_edge_junc = []
    parallel_pts = []
    for element in dic:
        if len(set(dic[element]))==1:
            one_edge_junc.append(element)
    one_edge_junc = sorted(one_edge_junc)
    view_pair = set()
    for val in (one_edge_junc): # get the parallele pt 
        data_x,data_y = data_pos.ix[val-1,1],data_pos.ix[val-1,2]
        for val2 in one_edge_junc:
            if val == val2 or (min(val,val2),max(val,val2)) in view_pair:
                break
            x2,data_y2 = data_pos.ix[val2-1,1],data_pos.ix[val2-1,2]
            if math.sqrt((data_x-x2)**2 +(data_y-data_y2)**2) < 25:
                path = BFS(val,val2)
                if path != False:
                    parallel_pts.append(path)
                    view_pair.add((min(val,val2),max(val,val2)))
                    #print (val,val2,path)
                    break       
    for path in parallel_pts: # get the path from one pt to another pt
        print (path)
        if len(path) ==2:
            Deleted_edge.append(street_id[(min(path[0],path[1]),max(path[0],path[1]))])
        else:
            if len(path) %2 ==0:
                mid = int(len(path)/2)
            else:
                mid = int(len(path)/2)+1
            for i in range(1,len(path[:mid])):
                Deleted_edge.append(street_id[(min(path[i],path[i-1]),max(path[i],path[i-1]))])
'''
for element in Deleted_edge:
    print ("or \"LinkID\" = ",element)
print (len(Deleted_edge))
'''


# In[8]:

df2 = pd.DataFrame(Deleted_edge, columns=["LinkID"])
#df2.to_csv('uc6_delete_v2.csv', index=False)
#df1 = pd.read_excel("delete_v1.csv")
#df1.to_csv('uc6_delete_v3.csv', index=False)
df2.to_csv('delete_uc3.csv', index=False,header=False, mode='a+')


# In[ ]:




# In[ ]:



