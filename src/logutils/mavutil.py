#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Fake version of mavutil to help eliminate the pymavlink prerequisite.

This ***should*** cover all the required parts of mavutil that are imported
by DFReader.py.
"""

mode_mapping_apm = {
    0 : 'MANUAL',
    1 : 'CIRCLE',
    2 : 'STABILIZE',
    3 : 'TRAINING',
    4 : 'ACRO',
    5 : 'FBWA',
    6 : 'FBWB',
    7 : 'CRUISE',
    8 : 'AUTOTUNE',
    10 : 'AUTO',
    11 : 'RTL',
    12 : 'LOITER',
    13 : 'TAKEOFF',
    14 : 'AVOID_ADSB',
    15 : 'GUIDED',
    16 : 'INITIALISING',
    17 : 'QSTABILIZE',
    18 : 'QHOVER',
    19 : 'QLOITER',
    20 : 'QLAND',
    21 : 'QRTL',
    22 : 'QAUTOTUNE',
    23 : 'QACRO',
    24 : 'THERMAL',
}
mode_mapping_acm = {
    0 : 'STABILIZE',
    1 : 'ACRO',
    2 : 'ALT_HOLD',
    3 : 'AUTO',
    4 : 'GUIDED',
    5 : 'LOITER',
    6 : 'RTL',
    7 : 'CIRCLE',
    8 : 'POSITION',
    9 : 'LAND',
    10 : 'OF_LOITER',
    11 : 'DRIFT',
    13 : 'SPORT',
    14 : 'FLIP',
    15 : 'AUTOTUNE',
    16 : 'POSHOLD',
    17 : 'BRAKE',
    18 : 'THROW',
    19 : 'AVOID_ADSB',
    20 : 'GUIDED_NOGPS',
    21 : 'SMART_RTL',
    22 : 'FLOWHOLD',
    23 : 'FOLLOW',
    24 : 'ZIGZAG',
}
mode_mapping_rover = {
    0 : 'MANUAL',
    1 : 'ACRO',
    2 : 'LEARNING',
    3 : 'STEERING',
    4 : 'HOLD',
    5 : 'LOITER',
    6 : 'FOLLOW',
    7 : 'SIMPLE',
    10 : 'AUTO',
    11 : 'RTL',
    12 : 'SMART_RTL',
    15 : 'GUIDED',
    16 : 'INITIALISING'
}
mode_mapping_tracker = {
    0 : 'MANUAL',
    1 : 'STOP',
    2 : 'SCAN',
    4 : 'GUIDED',
    10 : 'AUTO',
    16 : 'INITIALISING'
}
mode_mapping_sub = {
    0: 'STABILIZE',
    1: 'ACRO',
    2: 'ALT_HOLD',
    3: 'AUTO',
    4: 'GUIDED',
    7: 'CIRCLE',
    9: 'SURFACE',
    16: 'POSHOLD',
    19: 'MANUAL',
}

class mavlink(object):
    MAV_TYPE_GENERIC = 0
    MAV_TYPE_FIXED_WING = 1                                                     
    MAV_TYPE_QUADROTOR = 2                                                      
    MAV_TYPE_COAXIAL = 3                                                        
    MAV_TYPE_HELICOPTER = 4                                                     
    MAV_TYPE_ANTENNA_TRACKER = 5                                                
    MAV_TYPE_GCS = 6                                                            
    MAV_TYPE_AIRSHIP = 7                                                        
    MAV_TYPE_FREE_BALLOON = 8                                                   
    MAV_TYPE_ROCKET = 9                                                         
    MAV_TYPE_GROUND_ROVER = 10                                                  
    MAV_TYPE_SURFACE_BOAT = 11                                                  
    MAV_TYPE_SUBMARINE = 12                                                     
    MAV_TYPE_HEXAROTOR = 13                                                     
    MAV_TYPE_OCTOROTOR = 14                                                     
    MAV_TYPE_TRICOPTER = 15                                                     
    MAV_TYPE_FLAPPING_WING = 16                                                 
    MAV_TYPE_KITE = 17                                                          
    MAV_TYPE_ONBOARD_CONTROLLER = 18                                            
    MAV_TYPE_VTOL_DUOROTOR = 19                                                 
    MAV_TYPE_VTOL_QUADROTOR = 20                                                
    MAV_TYPE_VTOL_TILTROTOR = 21                                                
    MAV_TYPE_VTOL_RESERVED2 = 22                                                
    MAV_TYPE_VTOL_RESERVED3 = 23                                                
    MAV_TYPE_VTOL_RESERVED4 = 24                                                
    MAV_TYPE_VTOL_RESERVED5 = 25                                                
    MAV_TYPE_GIMBAL = 26                                                        
    MAV_TYPE_ADSB = 27                                                          
    MAV_TYPE_PARAFOIL = 28                                                      
    MAV_TYPE_DODECAROTOR = 29                                                   
    MAV_TYPE_CAMERA = 30                                                        
    MAV_TYPE_CHARGING_STATION = 31                                              
    MAV_TYPE_FLARM = 32                                                         
    MAV_TYPE_SERVO = 33                                                         
    MAV_TYPE_ODID = 34                                                          
    MAV_TYPE_DECAROTOR = 35    


def mode_mapping_bynumber(mav_type):
    '''return dictionary mapping mode numbers to name, or None if unknown'''
    map = None
    if mav_type in [mavlink.MAV_TYPE_QUADROTOR,
                    mavlink.MAV_TYPE_HELICOPTER,
                    mavlink.MAV_TYPE_HEXAROTOR,
                    mavlink.MAV_TYPE_DECAROTOR,
                    mavlink.MAV_TYPE_OCTOROTOR,
                    mavlink.MAV_TYPE_DODECAROTOR,
                    mavlink.MAV_TYPE_COAXIAL,
                    mavlink.MAV_TYPE_TRICOPTER]:
        map = mode_mapping_acm
    if mav_type == mavlink.MAV_TYPE_FIXED_WING:
        map = mode_mapping_apm
    if mav_type == mavlink.MAV_TYPE_GROUND_ROVER:
        map = mode_mapping_rover
    if mav_type == mavlink.MAV_TYPE_SURFACE_BOAT:
        map = mode_mapping_rover # for the time being
    if mav_type == mavlink.MAV_TYPE_ANTENNA_TRACKER:
        map = mode_mapping_tracker
    if mav_type == mavlink.MAV_TYPE_SUBMARINE:
        map = mode_mapping_sub
    if map is None:
        return None
    return map

def mode_string_acm(mode_number):
    '''return mode string for APM::Copter'''
    if mode_number in mode_mapping_acm:
        return mode_mapping_acm[mode_number]
    return "Mode(%u)" % mode_number

def evaluate_condition(condition, vars):
    if condition is None:
        return True
    v = evaluate_expression(condition, vars)
    if v is None:
        return False
    return v

def evaluate_expression(expression, vars, nocondition=False):
    # first check for conditions which take the form EXPRESSION{CONDITION}
    if expression[-1] == '}':
        startidx = expression.rfind('{')
        if startidx == -1:
            return None
        condition=expression[startidx+1:-1]
        expression=expression[:startidx]
        try:
            v = eval(condition, globals(), vars)
        except Exception:
            return None
        if not nocondition and not v:
            return None
    try:
        v = eval(expression, globals(), vars)
    except NameError:
        return None
    except ZeroDivisionError:
        return None
    except IndexError:
        return None
    return v

