from copy import deepcopy
def CalcScore(SimuOut):
    PI=SimuOut['Delay']+10*SimuOut['Stops']
    Score=1/PI*1000
    return Score
def is_InZone(list_TimingPlanNew,list_TimingLimit):
    flag = True
    for i in range(len(list_TimingPlanNew)):
        if list_TimingPlanNew[i] < list_TimingLimit[i]:
            flag = False
            return flag
    return flag
def AdjustLastStage(list_TimingPlanNew,CycleLen):
    LastStage=CycleLen
    for i in range(len(list_TimingPlanNew)-1):
        LastStage-=list_TimingPlanNew[i]
    list_TimingPlanNew[-1]=LastStage
    return list_TimingPlanNew
def Update_Intersection_TimingPlan(list_TimingPlanNew,dict_IntersectionFeature):
    dict_IntersectionFeatureNew=deepcopy(dict_IntersectionFeature)
    dict_IntersectionFeatureNew.update({'list_TimingPlan':list_TimingPlanNew})
    return dict_IntersectionFeatureNew
def Update_Variables_CycleLen(CycleLenNew,dict_SimuVariables):
    dict_SimuVariablesNew=deepcopy(dict_SimuVariables)
    dict_SimuVariablesNew.update({'CycleLen':CycleLenNew})
    return dict_SimuVariablesNew
def is_Tried(list_TimingPlanNew,dict_Tried):
    flag=False
    for key in dict_Tried['list_Tried']:
        if list_TimingPlanNew == dict_Tried[key]:
            flag=True
            return flag
    return flag