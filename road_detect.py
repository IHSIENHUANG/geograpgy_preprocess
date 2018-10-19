
# coding: utf-8

# In[145]:

import pandas as pd
import numpy as np


# In[146]:

data = pd.read_excel('./Network_LA/uc6_locals_junc_pair_v1.xlsx')
print (data.head(10))


# In[138]:

testing_data = []
multiple_road = {} # store which junction coneected to more than two roads
dic = {} # store junction A connected to junction B
street_id = {} # store pair of junction with the edge
for LinkID,JID1,JID2,StName in zip(data['LinkID'],data['JID1'],data['JID2'],data['StName']):
    if "Pioneer Blvd" in StName:
        testing_data.append([LinkID,JID1,JID2,StName])

testing_data = sorted(testing_data,key=lambda x:x[1])
for row in testing_data:
    if row[1] not in dic:
        dic[row[1]] = [row[2]]
    elif row[2] not in dic[row[1]]:
        dic[row[1]].append(row[2])
    
    if row[2] not in dic:
        dic[row[2]] = [row[1]]
    elif row[1] not in dic[row[2]]:
        dic[row[2]].append(row[1])
        
    smaller = row[1]
    bigger = row[2]
    if smaller > bigger:
        smaller,bigger = bigger,smaller
    street_id[(smaller,bigger)] = row[0]
    
    #print (row)

for num in dic:
    if len(set(dic[num])) >=3:
        multiple_road[num] = dic[num]
#print (multiple_road)
print ("end reading data")


# In[139]:

#Utilize the DFS to find all the circle with the main street name
#it might contains a lot of circles
#However, we can know that # unique group of circle is not as many as original one 
def DFS(path,pre_element,next_element,seen,seen_pt,seen_edge):#seen saved the seen path
    if next_element in path:# it means head to head
        path = path+[next_element]   
        path = path[path.index(next_element):]
        cur_street = []
        for index in range(len(path)-1):
            smaller = path[index]
            bigger = path[index+1]
            if smaller > bigger:
                smaller,bigger = bigger,smaller
            cur_street.append(street_id[(smaller,bigger)])
        if sorted(cur_street) in seen: # make sure there is no redundant loop
            return None
        seen_edge.append(cur_street)
        seen.append(sorted(cur_street))
        seen_pt.append(path)
        return path 
    flag = None
    for new in dic[next_element]:
        if new != pre_element and new not in path[1:]:# make sure the circle should be from head to head
            flag = DFS(path+[next_element],next_element,new,seen,seen_pt,seen_edge)
            if flag != None:
                flag = True
                break
    if flag == None:
        return None
    return path


# In[140]:

#seen recorded sorted edge
#seen_pt record path of pt
#seen_edge record edges of path
seen = [] # record the route edge
seen_edge = []
seen_pt = [] # record the  route point
for start_pos in multiple_road:
    for i in multiple_road[start_pos]:
        if DFS([start_pos],start_pos,i,seen,seen_pt,seen_edge) != None:
            break
print (len(seen))
seen = sorted(seen,key = lambda x:len(x))
seen_pt = sorted(seen_pt,key = lambda x:len(x))
seen_edge = sorted(seen_edge,key = lambda x:len(x))


# In[141]:

# Because some circle should be sub-circle of the larger one
# We need to Union all of them and find out how many group of large circle
# And we only need to handle those Large Circles
def find_group_circle(seen_pt,seen_edge): # union all the circle and find out unique group of circle
    dif_group = 0
    dif_group_pt = []
    dif_group_edge = []
    for i,val in enumerate(seen_pt):
        flag = False
        for j in range(i+1,len(seen_pt)): # if any circle is concluded in the larger cricle, remove this circle
            if all(n in seen_pt[j] for n in val):
                flag = True
                break
        if flag == False:
            print ((val))
            dif_group_pt.append(val)
            dif_group_edge.append(seen_edge[i])
            '''
            for pt_id in val:
                print ("or \"id\" = ",pt_id)
            '''
            dif_group+=1
    print ("Ending Find Group Circle")
    print ("total %d different group" %(dif_group))
    return dif_group_pt,dif_group_edge


# In[142]:


# read_pos:
# read the position of all the pts in this circle
# And utilize the X or Y pos to determine the circle is North-South or East-West Dir and 
# read_critical_pt:
# Based on the direction to determine which pts are boundary pt, starting pt and ending pt
# get_the_route_by_critical_pt:
# The function is to find the path from the starting pt to ending pt which contains more junction
# besides Route_pt is not sorted, it means it keep the situation how the pts coneected
def read_pos(file_name,route_pt,route_edge): # read the position for the circle and find out the direction of the circle
    print ("-----------start_read_pos_of_all_pt-----------------")
    #print (route_pt)
    data_pos = pd.read_excel(file_name)
    X_pos = []
    Y_pos = []
    for pt in route_pt:
        X_pos.append(data_pos.ix[pt-1,1]) # id 1 is first row
        Y_pos.append(data_pos.ix[pt-1,2])
    #print ("std of x",np.std(X_pos))
    #print ("std of y",np.std(Y_pos))
    N_S_Flag = False
    if np.std(Y_pos) > np.std(X_pos):
        N_S_Flag = True
    return read_critical_pt(N_S_Flag,X_pos,Y_pos,route_pt,route_edge)
def read_critical_pt(N_S_Flag,X_pos,Y_pos,route_pt,route_edge): #Use the direction to get the critical pt pair <northest,southest> or <eastest,westesst>
    print ("------------start_get_the_critical_pt---------------")
    #print (route_pt)
    critical_pt1= critical_pt2 = -1 # store the boundary pt
    if N_S_Flag == True:
        print ("north_south_dir")
        critical_pt1 = Y_pos.index(max(Y_pos)) # find the northest pt index
        critical_pt1 = route_pt[critical_pt1] # get the id of the point
        critical_pt2 = Y_pos.index(min(Y_pos)) # find the southest pt index
        critical_pt2 = route_pt[critical_pt2] # get the id of the point
    else: # east west dir , haven't test it 
        critical_pt1 = X_pos.index(max(X_pos)) # find the eastest pt index
        critical_pt1 = route_pt[critical_pt1] # get the id of the point
        critical_pt2 = X_pos.index(min(X_pos)) # find the westest pt index
        critical_pt2 = route_pt[critical_pt2] # get the id of the point
        print ("east_west_dir")
    print ("critical pt=",critical_pt1,critical_pt2)
    return get_the_route_by_critical_pt(critical_pt1,critical_pt2,route_pt,route_edge)
def get_the_route_by_critical_pt(critical_pt1,critical_pt2,route_pt,route_edge):
    print ("------------start_get_the_critical_pt---------------")
    #print (route_pt)
    start_index = route_pt.index(critical_pt1)
    end_index = route_pt.index(critical_pt2)
    #print ("path index = ",start_index,end_index)
    start_index,end_index = min(start_index,end_index),max(start_index,end_index)
    if end_index - start_index+1 > int(len(route_pt)/2):
        print ("From start to end")
        route_pt =route_pt[start_index:end_index+1]
        route_edge= route_edge[start_index:end_index]
    else:
        route_pt =route_pt[end_index:] + route_pt[:start_index+1]
        route_edge= route_edge[end_index:] + route_edge[:start_index]
    for pt_id in route_pt:
        print ("or \"id\" = ",pt_id)
    for edge in route_edge:
        print ("or \"LinkID\" = ",edge)
    return route_edge,route_pt


# In[143]:

filename = "./Network_LA/uc6_02_05_UTM_locals_ND_Junctions.xlsx"
dif_group_pt,dif_group_edge = find_group_circle(seen_pt,seen_edge)
for route_pt,route_edge in zip(dif_group_pt,dif_group_edge):
    print ("\n\nnew round",route_pt)
    print ("path =",read_pos(filename,route_pt,route_edge))


# In[161]:

data = pd.read_excel('./Network_LA/uc6_locals_junc_pair_v1.xlsx')
Street_Name = {} # record which index is store in the name of streer
Direction = ['E','N','S','W']
for index,(LinkID,JID1,JID2,StName) in enumerate(zip(data['LinkID'],data['JID1'],data['JID2'],data['StName'])):
    Main_StName = StName.split(" ")
    if Main_StName[0] in Direction:
        Main_StName = Main_StName[1:]
    if Main_StName[-1] in Direction:
        Main_StName = Main_StName[:-1]
    Main_StName= ''.join(Main_StName)
    Street_Name[Main_StName]= Street_Name.get(Main_StName,[])
    Street_Name[Main_StName].append(LinkID)
for name in Street_Name:
    if len(Street_Name[name])>2:
        df = data.loc[data['LinkID'].isin(Street_Name[name])] # find the all rows with same street name
        print (df)


# In[157]:



df = data.loc[data['LinkID'].isin(Street_Name["HenryMayoDr"])]
print (df)
for index,name in enumerate(Street_Name):
    test_data = []
    if index > 10:
        break
    if len(Street_Name[name])>2:
        
        print (name,Street_Name[name])
        df = data.loc[data['LinkID'].isin(Street_Name[name])]
        print (df)
        '''
        for val in Street_Name[name]:
            print (val,data['LinkID'][val-1],data['JID1'][val-1],data['JID2'][val-1],data['StName'][val-1])
            test_data.append([data['LinkID'][val-1],data['JID1'][val-1],data['JID2'][val-1],data['StName'][val-1]])
        #print (test_data)
        '''


# In[154]:

data.head(1500)


# In[ ]:

'''
union_edge = {}
merge_index = []
#print("multiple road dictionary",multiple_road)
print ("-------------")

for index,row in enumerate(seen):
    print (row)
    print (seen_pt[index])
    total = 0 
    for element in row:
        #print ("or \"LinkID\" = ",element)
        union_edge[element] = union_edge.get(element,0)+1
    for pt in seen_pt[index]:
        if pt in multiple_road:
            total+=1
    print ("TOTAL 3-WAY:",total-1)# -1 for it go back to original pt and we calculate start pos twice
    #if total -1 >=3:
    merge_index.append(index)
seen = sorted([v for i,v in enumerate(seen) if i in merge_index],key = lambda x : len(x))
seen_pt = sorted([v for i,v in enumerate(seen_pt) if i in merge_index],key = lambda x : len(x))
seen_edge = sorted([v for i,v in enumerate(seen_edge) if i in merge_index],key = lambda x : len(x))
'''

