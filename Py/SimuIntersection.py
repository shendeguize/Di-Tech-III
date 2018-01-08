
# -*- coding: utf-8 -*-

import csv
import random
import math
import SimuLane
import SimuIntersection
from copy import deepcopy
import gc

def Gen_dict_DirectionFeature(Direction_id,dict_IntersectionFeature,dict_VelocityFeature,dict_SimuVariables):
    dict_DirectionFeature=deepcopy(dict_IntersectionFeature[Direction_id])

    
    list_TimingPlan=deepcopy(dict_IntersectionFeature['list_TimingPlan'])
    list_TimingLimit=deepcopy(dict_IntersectionFeature['list_TimingLimit'])
    CycleLen=dict_SimuVariables['CycleLen']

    list_StageidWithThis=dict_DirectionFeature.pop('list_StageidWithThis')
    StageStart=list_StageidWithThis[0]
    StageEnd=list_StageidWithThis[-1]
    TimeInCycle=0
    GreenEfStart=0
    GreenEfEnd=0
    for Stage_id in dict_IntersectionFeature['list_Stage']:
        if Stage_id == StageStart:
            GreenEfStart=TimeInCycle+3
        TimeInCycle+=list_TimingPlan[Stage_id-1]
        if Stage_id == StageEnd:
            GreenEfEnd=TimeInCycle-1
    item_Timing={
                 'GreenEfStart':GreenEfStart,
                 'GreenEfEnd':GreenEfEnd,
                 'CycleLen':CycleLen
                }
    
    VelocityFeature=deepcopy(dict_VelocityFeature)
    dict_DirectionFeature.update({
                                  'VelocityFeatures':VelocityFeature,
                                  'Timing':item_Timing
                                 })
    
    SimuVariables=deepcopy(dict_SimuVariables)
    TimeStep=SimuVariables.pop('TimeStep')
    SimuVariables.pop('Cycles')
    SimuVariables.pop('Depth')
    dict_DirectionFeature.update(SimuVariables)
    
    Volume=dict_DirectionFeature.pop('Volume')
    Volume=dict_IntersectionFeature['VolumeRatio']*Volume
    Headway=3600/Volume
    HeadwayMin=VelocityFeature['HeadwayMin']
    
    Times=Headway/TimeStep
    Sum_Times=0
    for i in range(int(Times)):
        Sum_Times+=i/Times
    SourceProp=1/Times
    
    
    item_Inflow={
                 'Source':{},
                 'Dilution':{}
                }
    for i in range(CycleLen):
        item_Inflow['Source'].update({i:SourceProp})
        item_Inflow['Dilution'].update({i:1.0})
    dict_DirectionFeature.update({'Inflow':item_Inflow})
    
    return dict_DirectionFeature

def CalcIntersection(dict_IntersectionFeature,dict_VelocityFeature,dict_SimuVariables):
    Stops=0
    Delay=0
    Count=0
    for Direction_id in dict_IntersectionFeature['list_Direction']:
        for i in range(dict_IntersectionFeature[Direction_id]['Lanes']):
            Cycles=dict_SimuVariables['Cycles']
            TimeStep=dict_SimuVariables['TimeStep']
            dict_DirectionFeature=Gen_dict_DirectionFeature(Direction_id,dict_IntersectionFeature,dict_VelocityFeature,dict_SimuVariables)
            SimuLaneOut=SimuLane.CalcSimuOut(dict_DirectionFeature,Cycles,TimeStep)
            Stops+=SimuLaneOut['Stops']*SimuLaneOut['Count']
            Delay+=SimuLaneOut['Delay']*SimuLaneOut['Count']
            Count+=SimuLaneOut['Count']
    return {
            'Stops':Stops/Count,
            'Delay':Delay/Count,
            'Count':Count
            }