
# coding: utf-8

# In[1]:


import csv
import random
import math
from copy import deepcopy
import gc


# In[2]:


import SimuLane
import SimuIntersection
from OptimFunBasic import CalcScore
from OptimFunBasic import is_InZone
from OptimFunBasic import AdjustLastStage
from OptimFunBasic import Update_Intersection_TimingPlan
from OptimFunBasic import Update_Variables_CycleLen
from OptimFunBasic import is_Tried


# In[3]:

'''
from input import dict_IntersectionFeature
from input import dict_SimuVariables
from input import dict_VelocityFeature
'''

# In[ ]:


def Search_WithDepth_FixedCycle(dict_Tried,dict_IntersectionFeature,dict_SimuVariables,dict_VelocityFeature):

    list_TimingPlan=deepcopy(dict_IntersectionFeature['list_TimingPlan'])
    list_TimingLimit=dict_IntersectionFeature['list_TimingLimit']
    SimuOut=SimuIntersection.CalcIntersection(dict_IntersectionFeature,dict_VelocityFeature,dict_SimuVariables)
    Score=CalcScore(SimuOut)
    Optimized={
        'TimingPlan':list_TimingPlan,
        'Score':Score    
    }
    CycleLen=dict_SimuVariables['CycleLen']
    CycleLenNew=CycleLen
    Depth=dict_SimuVariables['Depth']
    Demension=len(list_TimingPlan)-1

    for i in range(Demension):
        list_TimingPlan=Optimized['TimingPlan']
        Score=Optimized['Score']
        for j in range(Depth):
            Change=j+1
            list_TimingPlanNew=deepcopy(list_TimingPlan)
            list_TimingPlanNew[i]=list_TimingPlan[i]+Change
            list_TimingPlanNew=AdjustLastStage(list_TimingPlanNew,CycleLen)
            if is_InZone(list_TimingPlanNew,list_TimingLimit) == True:
                if is_Tried(list_TimingPlanNew,dict_Tried) == False:
                    dict_IntersectionFeatureNew=Update_Intersection_TimingPlan(list_TimingPlanNew,dict_IntersectionFeature)
                    dict_SimuVariablesNew=Update_Variables_CycleLen(CycleLenNew,dict_SimuVariables)
                    SimuOutNew=SimuIntersection.CalcIntersection(dict_IntersectionFeatureNew,dict_VelocityFeature,dict_SimuVariablesNew)
                    ScoreNew=CalcScore(SimuOutNew)
                    dict_Tried['list_Tried'].append(len(dict_Tried['list_Tried'])+1)
                    dict_Tried.update({dict_Tried['list_Tried'][-1]:list_TimingPlanNew})
                    
                    if ScoreNew > Score:
                        Optimized.update({
                            'TimingPlan':list_TimingPlanNew,
                            'Score':ScoreNew
                        })
                        print('Tried:',list_TimingPlanNew,'√')
                    else:
                        print('Tried:',list_TimingPlanNew,'×')

            list_TimingPlanNew=deepcopy(list_TimingPlan)
            list_TimingPlanNew[i]=list_TimingPlan[i]-Change
            list_TimingPlanNew=AdjustLastStage(list_TimingPlanNew,CycleLen)
            if is_InZone(list_TimingPlanNew,list_TimingLimit) == True:
                if is_Tried(list_TimingPlanNew,dict_Tried) == False:
                    dict_IntersectionFeatureNew=Update_Intersection_TimingPlan(list_TimingPlanNew,dict_IntersectionFeature)
                    dict_SimuVariablesNew=Update_Variables_CycleLen(CycleLenNew,dict_SimuVariables)
                    SimuOutNew=SimuIntersection.CalcIntersection(dict_IntersectionFeatureNew,dict_VelocityFeature,dict_SimuVariablesNew)
                    ScoreNew=CalcScore(SimuOutNew)
                    dict_Tried['list_Tried'].append(len(dict_Tried['list_Tried'])+1)
                    dict_Tried.update({dict_Tried['list_Tried'][-1]:list_TimingPlanNew})
                    if ScoreNew > Score:
                        Optimized.update({
                            'TimingPlan':list_TimingPlanNew,
                            'Score':ScoreNew
                        })
                        print('Tried:',list_TimingPlanNew,'√')
                    else:
                        print('Tried:',list_TimingPlanNew,'×')
    gc.collect()
    return Optimized


# In[ ]:


def Optimization_FixedCycle(dict_IntersectionFeature,dict_SimuVariables,dict_VelocityFeature):

    list_TimingPlan=deepcopy(dict_IntersectionFeature['list_TimingPlan'])
    dict_Tried={
        'list_Tried':[0],
        0:list_TimingPlan
    }
    Optimization=Search_WithDepth_FixedCycle(dict_Tried,dict_IntersectionFeature,dict_SimuVariables,dict_VelocityFeature)
    SearchTimes=1
    while(1):
        print('Search Steps:',SearchTimes)
        list_TimingPlanNew=Optimization['TimingPlan']
        dict_IntersectionFeatureNew=dict_IntersectionFeatureNew=Update_Intersection_TimingPlan(list_TimingPlanNew,dict_IntersectionFeature)
        OptimizationNew=Search_WithDepth_FixedCycle(dict_Tried,dict_IntersectionFeatureNew,dict_SimuVariables,dict_VelocityFeature)
        if OptimizationNew['TimingPlan']==Optimization['TimingPlan']:
            return OptimizationNew
        else:
            Optimization=OptimizationNew
            SearchTimes+=1
        


# In[ ]:

'''
Optimization_FixedCycle(dict_IntersectionFeature,dict_SimuVariables,dict_VelocityFeature)
'''
