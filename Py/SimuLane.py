
# coding: utf-8

# In[2]:


# -*- coding: utf-8 -*-


# In[4]:


import csv
import random
import math


# In[13]:


def Gen_NewVeh(dict_DirectionFeature,TimeNow,dict_Veh):
    CycleLen=dict_DirectionFeature['Timing']['CycleLen']
    TimeInCycle=TimeNow%CycleLen
    TimeGen=TimeNow
    
    SourceInflow=dict_DirectionFeature['Inflow']['Source'][math.floor(TimeInCycle)]
    DilutionInflow=dict_DirectionFeature['Inflow']['Dilution'][math.floor(TimeInCycle)]
    Lanes=dict_DirectionFeature['Lanes']
    InflowProp=SourceInflow*DilutionInflow/Lanes
    
    Random=random.random()
    VelocityFeatures=dict_DirectionFeature['VelocityFeatures']
    Velocity=VelocityFeatures['VelocityMean']

    item_VehState_Veh_id={
                          'Location':0,
                          'Velocity':Velocity,
                          'Acceleration':0,
                          'TimeGen':TimeGen,
                          'TimeDep':0,
                          'Stops':0,
                          'flag':0
    }
    if Random <= InflowProp:

        if len(dict_Veh['list_Veh']) == 0:
            item_VehState_Veh_id.update({'flag':1})
        else:
            Veh_idLast=dict_Veh['list_Veh'][-1]
            TimeGenLast=dict_Veh['dict_VehState'][Veh_idLast]['TimeGen']
            HeadwayMin=VelocityFeatures['HeadwayMin']
            
            if HeadwayMin <= (TimeGen-TimeGenLast):
                item_VehState_Veh_id.update({'flag':1})
    return item_VehState_Veh_id


# In[118]:


def Update_VehState(dict_Veh,TimeStep,TimeNow,dict_DirectionFeature):
    dict_VehStateNew=dict_Veh['dict_VehState']
    for Veh_id in dict_Veh['list_Veh']:
        LocationNew=Update_Location(dict_Veh,Veh_id,TimeStep)
        VelocityNew=Update_Velocity(dict_Veh,Veh_id,TimeStep,dict_DirectionFeature)
        AccelerationNew=Update_Acceleration(dict_Veh,Veh_id,TimeStep,TimeNow,dict_DirectionFeature)
                

        Velocity=dict_Veh['dict_VehState'][Veh_id]['Velocity']
        if VelocityNew == 0:
            if Velocity > 0:
                Stops=dict_Veh['dict_VehState'][Veh_id]['Stops']
                Stops=Stops+1
                
                dict_VehStateNew[Veh_id].update({'Stops':Stops})
        dict_VehStateNew[Veh_id].update({'Location':LocationNew})
        dict_VehStateNew[Veh_id].update({'Velocity':VelocityNew})
        dict_VehStateNew[Veh_id].update({'Acceleration':AccelerationNew})
    return dict_VehStateNew


# In[107]:


def Update_Location(dict_Veh,Veh_id,TimeStep):
    VehState=dict_Veh['dict_VehState'][Veh_id]
    Location=VehState['Location']
    Velocity=VehState['Velocity']
    LocationNew=Location+Velocity*TimeStep
    return LocationNew


# In[108]:


def Update_Velocity(dict_Veh,Veh_id,TimeStep,dict_DirectionFeature):
    VelocityFeatures=dict_DirectionFeature['VelocityFeatures']
    VelocityLimit=VelocityFeatures['VelocityLimit']
    VehState=dict_Veh['dict_VehState'][Veh_id]
    Velocity=VehState['Velocity']
    Acceleration=VehState['Acceleration']
    VelocityNew=Velocity+Acceleration*TimeStep
    if VelocityNew > VelocityLimit:
        VelocityNew = VelocityLimit
    if VelocityNew <= 0:
        VelocityNew = 0
    return VelocityNew


# In[164]:


def Update_Acceleration(dict_Veh,Veh_id,TimeStep,TimeNow,dict_DirectionFeature):
    VelocityFeatures=dict_DirectionFeature['VelocityFeatures']
    VelocityMean=VelocityFeatures['VelocityMean']
    Deceleration=VelocityFeatures['Deceleration']
    VelocityDeparture=VelocityFeatures['VelocityDeparture']
    Distance=dict_DirectionFeature['Distance']
    Lamda=dict_DirectionFeature['Lamda']
    VehLen=dict_DirectionFeature['VehLen']
    VehLenFactor=dict_DirectionFeature['VehLenFactor']
    AccelerationNew=0
    
    Location=dict_Veh['dict_VehState'][Veh_id]['Location']
    
    Velocity=dict_Veh['dict_VehState'][Veh_id]['Velocity']
    
    DistanceBraking=Velocity*Velocity/(2.0*Deceleration)
    if Veh_id-1 in dict_Veh['list_Veh']:
        LocationLast=dict_Veh['dict_VehState'][Veh_id-1]['Location']
        VelocityLast=dict_Veh['dict_VehState'][Veh_id-1]['Velocity']
        DistanceVeh=LocationLast-Location-VehLen*VehLenFactor
        if VehLen <= DistanceVeh <= DistanceBraking/Lamda:
            AccelerationNew=Lamda*(VelocityLast-Velocity)/(DistanceVeh*DistanceVeh)
        elif DistanceVeh < VehLen:
            AccelerationNew=-Deceleration
        else:
            AccelerationNew=Lamda*(VelocityMean-Velocity)
    else:
        Timing=dict_DirectionFeature['Timing']
        GreenEfStart=Timing['GreenEfStart']
        GreenEfEnd=Timing['GreenEfEnd']
        CycleLen=Timing['CycleLen']
        TimeInCycle=TimeNow%CycleLen
        
        DistanceIntersection=Distance-Location
        DistanceDepBraking=VelocityDeparture*VelocityDeparture/(2.0*Deceleration)
        
        if GreenEfStart <= TimeInCycle <= GreenEfEnd:
            if DistanceIntersection <= DistanceDepBraking:
                AccelerationNew=Lamda*(VelocityDeparture-Velocity)
            else:
                AccelerationNew=Lamda*(VelocityMean-Velocity)
        else:
            if DistanceIntersection > DistanceDepBraking+VehLen*Lamda/VehLenFactor:
                AccelerationNew=Lamda*(VelocityMean-Velocity)
            
            elif DistanceBraking-VehLen <= DistanceIntersection <= DistanceDepBraking+VehLen*Lamda/VehLenFactor:
                AccelerationNew=-Deceleration
    return AccelerationNew


# In[165]:


def SimuLane(dict_DirectionFeature,Cycles,TimeStep):
    dict_Veh={
              'list_Veh':[],
              'dict_VehState':{}
             }
    dict_Pass={
              'list_Veh':[],
              'dict_VehState':{}
              }
    CycleLen=dict_DirectionFeature['Timing']['CycleLen']
    for i in range(int(Cycles*CycleLen/TimeStep)):
        TimeNow=TimeStep*i
        item_Veh=Gen_NewVeh(dict_DirectionFeature,TimeNow,dict_Veh)
        flag=item_Veh.pop('flag')
        if flag==1:
            if len(dict_Veh['list_Veh'])==0:
                dict_Veh['list_Veh'].append(1)
            else:
                dict_Veh['list_Veh'].append(dict_Veh['list_Veh'][-1]+1)
            item_VehState={dict_Veh['list_Veh'][-1]:item_Veh}
            dict_Veh['dict_VehState'].update(item_VehState)
        dict_VehStateNew=Update_VehState(dict_Veh,TimeStep,TimeNow,dict_DirectionFeature)
        dict_Veh.update({'dict_VehState':dict_VehStateNew})

        Distance=dict_DirectionFeature['Distance']
        if len(dict_Veh['list_Veh'])!=0:
            Veh_id_First=dict_Veh['list_Veh'][0]
            if dict_Veh['dict_VehState'][Veh_id_First]['Location'] >= Distance:
                item_Pass=dict_Veh['dict_VehState'].pop(Veh_id_First)
                dict_Pass['list_Veh'].append(Veh_id_First)
                item_Pass.update({'TimeDep':TimeNow})
                dict_Pass['dict_VehState'].update({Veh_id_First:item_Pass})
                dict_Veh['list_Veh'].remove(Veh_id_First)
    return {'dict_Veh':dict_Veh,
            'dict_Pass':dict_Pass
           }


# In[172]:


def CalcSimuOut(dict_DirectionFeature,Cycles,TimeStep):
    dict_SimuOut=SimuLane(dict_DirectionFeature,Cycles+1,TimeStep)
    dict_Pass=dict_SimuOut['dict_Pass']
    TimeGenFirst=dict_Pass['dict_VehState'][1]['TimeGen']
    TimeDepFirst=dict_Pass['dict_VehState'][1]['TimeDep']
    TimeFree=dict_DirectionFeature['Distance']/dict_DirectionFeature['VelocityFeatures']['VelocityMean']
    TimeStart=TimeDepFirst
    CycleLen=dict_DirectionFeature['Timing']['CycleLen']
    TimeEnd=TimeStart+Cycles*CycleLen
    Stops=0
    Delay=0
    Count=0
    for Veh_id in dict_Pass['list_Veh']:
        if TimeStart <= dict_Pass['dict_VehState'][Veh_id]['TimeDep'] <= TimeEnd:
            Stops=Stops+dict_Pass['dict_VehState'][Veh_id]['Stops']
            Delay=dict_Pass['dict_VehState'][Veh_id]['TimeDep']-dict_Pass['dict_VehState'][Veh_id]['TimeGen']-TimeFree+Delay
            Count=Count+1
    return {
            'Stops':Stops/Count,
            'Delay':Delay/Count,
            'Count':Count,
            'dict_SimuOut':dict_SimuOut
           }


# In[169]:
'''

dict_DirectionFeature={
                       'Inflow':{
                                 'Source':{
                                          },
                                 'Dilution':{
                                            }
                                },
                      'Timing':{
                                'GreenEfStart':0,
                                'GreenEfEnd':100,
                                'CycleLen':200,
                                'GreenMin':10
                               },
                      'VelocityFeatures':{
                                          'VelocityMean':6,
                                          'VelocityDeparture':8,
                                          'VelocityVariance':0,
                                          'VelocityLimit':10,
                                          'HeadwayMin':3,
                                          'Deceleration':10
                                         },
                      'Lanes':2,
                      'Distance':200,
                      'Lamda':0.6667,
                      'VehLen':2.5,
                      'VehLenFactor':1.5
                    }


for i in range(200):
    item_InflowSource={i:1.2}
    dict_DirectionFeature['Inflow']['Source'].update(item_InflowSource)
    item_InflowDilution={i:1}
    dict_DirectionFeature['Inflow']['Dilution'].update(item_InflowDilution)

Cycles=2
TimeStep=0.1


# In[174]:


SimuOut=CalcSimuOut(dict_DirectionFeature,Cycles,TimeStep)
print(SimuOut['Stops'],SimuOut['Delay'])

'''