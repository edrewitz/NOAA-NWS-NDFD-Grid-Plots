#====================================================================================================
# THIS IS THE MASTER FILE FOR THE NWS NDFD GRAPHICS
#
# THESE GRAPHICS INCLUDE:
#
# 1) NWS NDFD MAXIMUM TEMPERATURE FORECAST AND TRENDS
# 2) NWS NDFD EXTREME HEAT (NWS MAX T FORECAST >= 120F DURING THE WARM SEASON OR >= 100F DURING COOL SEASON)
# 3) NWS NDFD MINIMUM TEMPERATURE FORECAST AND TRENDS
# 4) NWS NDFD ABNORMALLY COOL TEMPERATURES (WARM SEASON) OR FROST/FREEZE (COOL SEASON)
#
#
#
#                            |----------------------------------------|
#                            |             DEVELOPED BY               | 
#                            |        (C) ERIC J. DREWITZ             |
#                            |             METEOROLOGIST              |
#                            |               USDA/USFS                |
#                            |----------------------------------------|
#
#=====================================================================================================

###################################################
# IMPORTS
###################################################

from datetime import datetime, timedelta
from siphon.catalog import TDSCatalog
from metpy.plots import colortables
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import pygrib
import xarray as xr
import math
import metpy.plots as mpplots
from metpy.units import units
import metpy.calc as mpcalc
import pandas as pd
from metpy.units import pandas_dataframe_to_unit_arrays
from metpy.plots import USCOUNTIES
from ftplib import FTP
import os

#######################################################
# NDFD GRIDS DATA ACCESS FROM NOAA/NWS FTP SERVER
#######################################################

ftp = FTP('tgftp.nws.noaa.gov')
ftp.login()
dirName = '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/VP.001-003/'
files = ftp.cwd(dirName)

####################################################
# DOWNLOADS THE NWS NDFD GRIDS FOR PACIFIC SOUTHWEST
####################################################


# MAX TEMPERATURE
with open('ds.maxt.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.maxt.bin', fp.write)


# MIN TEMPERATURE
with open('ds.mint.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.mint.bin', fp.write)

ftp.close()
###########################################################
# DATA ARRAYS FOR DIFFERENT PARAMETERS
###########################################################

# MAX TEMPERATURE
ds_max_T = xr.load_dataset('ds.maxt.bin', engine='cfgrib')
grbs_max_T = pygrib.open('ds.maxt.bin')
grbs_max_T.seek(0)

# MIN TEMPERATURE
ds_min_T = xr.load_dataset('ds.mint.bin', engine='cfgrib')
grbs_min_T = pygrib.open('ds.mint.bin')
grbs_min_T.seek(0)

####################################################################
# CHECKS FOR THE NUMBER OF GRIB FILES FOR EACH PARAMETER
####################################################################

# MAX TEMPERATURE
count_max_T = 0
for grb in grbs_max_T:
    count_max_T = count_max_T + 1
if count_max_T == 1:
    grb_max_T_12 = grbs_max_T[1]
    grb_max_T_12_logic = True
    grb_max_T_24_logic = False
    grb_max_T_48_logic = False
    grb_max_T_72_logic = False

if count_max_T == 2:
    grb_max_T_12 = grbs_max_T[1]
    grb_max_T_24 = grbs_max_T[2]
    grb_max_T_12_logic = True
    grb_max_T_24_logic = True
    grb_max_T_48_logic = False
    grb_max_T_72_logic = False
    
if count_max_T == 3: 
    grb_max_T_12 = grbs_max_T[1]
    grb_max_T_24 = grbs_max_T[2]
    grb_max_T_48 = grbs_max_T[3]
    grb_max_T_12_logic = True
    grb_max_T_24_logic = True
    grb_max_T_48_logic = True
    grb_max_T_72_logic = False

if count_max_T >= 4: 
    grb_max_T_12 = grbs_max_T[1]
    grb_max_T_24 = grbs_max_T[2]
    grb_max_T_48 = grbs_max_T[3]
    grb_max_T_72 = grbs_max_T[4]
    grb_max_T_12_logic = True
    grb_max_T_24_logic = True
    grb_max_T_48_logic = True
    grb_max_T_72_logic = True

# MIN TEMPERATURE
count_min_T = 0
for grb in grbs_min_T:
    count_min_T = count_min_T + 1
if count_min_T == 1:
    grb_min_T_12 = grbs_min_T[1]
    grb_min_T_12_logic = True
    grb_min_T_24_logic = False
    grb_min_T_48_logic = False
    grb_min_T_72_logic = False

if count_min_T == 2:
    grb_min_T_12 = grbs_min_T[1]
    grb_min_T_24 = grbs_min_T[2]
    grb_min_T_12_logic = True
    grb_min_T_24_logic = True
    grb_min_T_48_logic = False
    grb_min_T_72_logic = False
    
if count_min_T == 3: 
    grb_min_T_12 = grbs_min_T[1]
    grb_min_T_24 = grbs_min_T[2]
    grb_min_T_48 = grbs_min_T[3]
    grb_min_T_12_logic = True
    grb_min_T_24_logic = True
    grb_min_T_48_logic = True
    grb_min_T_72_logic = False

if count_min_T >= 4: 
    grb_min_T_12 = grbs_min_T[1]
    grb_min_T_24 = grbs_min_T[2]
    grb_min_T_48 = grbs_min_T[3]
    grb_min_T_72 = grbs_min_T[4]
    grb_min_T_12_logic = True
    grb_min_T_24_logic = True
    grb_min_T_48_logic = True
    grb_min_T_72_logic = True

# LAT/LON COORDINATES FOR DIFFERENT PARAMETERS
lats_max_T, lons_max_T = grb_max_T_12.latlons()
lats_min_T, lons_min_T = grb_min_T_12.latlons()

####################################################
# DATE AND TIME SECTION
####################################################

# CURRENT DATE/TIME
now = datetime.utcnow()
year = now.year
month = now.month
day = now.day
hour = now.hour
minute=now.minute

night_2 = now + timedelta(days=1)
night_3 = now + timedelta(days=2)

date = datetime(year, month, day, hour)
date1 = datetime(year, month, day, hour, minute)

# Start and end times for the different grids
# Temperature grids are from 00z to 12z and 12z to 00z
hr_T_12z = 12
hr_T_00z = 0
        
####################
# MAX TEMPERATURE
####################
frac = 9/5

if hour >= 12 and hour <=24:
    grib_file_1_max_T_start = datetime(year, month, day, hr_T_12z)
    grib_file_1_max_T_end = grib_file_1_max_T_start + timedelta(hours=12)

else:
    grib_file_1_max_T_start = grb_max_T_12.validDate
    grib_file_1_max_T_end = grib_file_1_max_T_start + timedelta(hours=12)

if grb_max_T_12_logic == True:
    grb_max_T_12_C = (grb_max_T_12.values - 273.15)
    grb_max_T_12_F = (frac * grb_max_T_12_C) + 32
   
    if grb_max_T_24_logic == True:
        grb_max_T_24_C = (grb_max_T_24.values - 273.15)
        grb_max_T_24_F = (frac * grb_max_T_24_C) + 32
        diff_max_T_1 = grb_max_T_24_F - grb_max_T_12_F
        grib_file_2_max_T_start = grb_max_T_24.validDate
        grib_file_2_max_T_end = grib_file_2_max_T_start + timedelta(hours=12)
        
        if grb_max_T_48_logic == True:
            grb_max_T_48_C = (grb_max_T_48.values - 273.15)
            grb_max_T_48_F = (frac * grb_max_T_48_C) + 32
            diff_max_T_2 = grb_max_T_48_F - grb_max_T_24_F
            grib_file_3_max_T_start = grb_max_T_48.validDate
            grib_file_3_max_T_end = grib_file_3_max_T_start + timedelta(hours=12)

            if grb_max_T_72_logic == True:
                grb_max_T_72_C = (grb_max_T_72.values - 273.15)
                grb_max_T_72_F = (frac * grb_max_T_72_C) + 32
                diff_max_T_3 = grb_max_T_72_F - grb_max_T_48_F
                grib_file_4_max_T_start = grb_max_T_72.validDate
                grib_file_4_max_T_end = grib_file_4_max_T_start + timedelta(hours=12)


##################################
# MIN TEMPERATURE
##################################

if hour >= 0 and hour <=12:
    grib_file_1_min_T_start = datetime(year, month, day, hr_T_00z)
    grib_file_1_min_T_end = grib_file_1_min_T_start + timedelta(hours=12)

else:
    grib_file_1_min_T_start = grb_min_T_12.validDate
    grib_file_1_min_T_end = grib_file_1_min_T_start + timedelta(hours=12)

if grb_min_T_12_logic == True:
    grb_min_T_12_C = (grb_min_T_12.values - 273.15)
    grb_min_T_12_F = (frac * grb_min_T_12_C) + 32
   
    if grb_min_T_24_logic == True:
        grb_min_T_24_C = (grb_min_T_24.values - 273.15)
        grb_min_T_24_F = (frac * grb_min_T_24_C) + 32
        diff_min_T_1 = grb_min_T_24_F - grb_min_T_12_F
        grib_file_2_min_T_start = grb_min_T_24.validDate
        grib_file_2_min_T_end = grib_file_2_min_T_start + timedelta(hours=12)
        
        if grb_min_T_48_logic == True:
            grb_min_T_48_C = (grb_min_T_48.values - 273.15)
            grb_min_T_48_F = (frac * grb_min_T_48_C) + 32
            diff_min_T_2 = grb_min_T_48_F - grb_min_T_24_F
            grib_file_3_min_T_start = grb_min_T_48.validDate
            grib_file_3_min_T_end = grib_file_3_min_T_start + timedelta(hours=12)

            if grb_min_T_72_logic == True:
                grb_min_T_72_C = (grb_min_T_72.values - 273.15)
                grb_min_T_72_F = (frac * grb_min_T_72_C) + 32
                diff_min_T_3 = grb_min_T_72_F - grb_min_T_72_F
                grib_file_4_min_T_start = grb_min_T_72.validDate
                grib_file_4_min_T_end = grib_file_4_min_T_start + timedelta(hours=12)


################################################
# ***GRAPHICS SECTION***
################################################

#*****************************************************************************************************
#*****************************************************************************************************

############################################################################################
#     
#
#
#    THIS SECTION HAS ALL THE MAXIMUM TEMPERATURE GRAPHICS
#     1) MAXIMUM TEMPERATURE FORECAST AND TREND
#     2) FILTERED EXTREME HEAT
#                                 
#
#
#############################################################################################

mapcrs_max_T = ccrs.LambertConformal(central_longitude=-115, central_latitude=35, standard_parallels=(30,60))
datacrs_max_T = ccrs.PlateCarree()

if hour >= 0 and hour < 19:
    if count_max_T == 2:
        fig_max_T = plt.figure(figsize=(9,5))
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        fig_max_T = plt.figure(figsize=(15,5))
    if count_max_T >= 3 and grb_max_T_72_logic == True:
        fig_max_T = plt.figure(figsize=(12,12)) 

if hour >= 19 and hour < 24:
    if count_max_T == 2:
        fig_max_T = plt.figure(figsize=(7,5))
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        fig_max_T = plt.figure(figsize=(9,5))
    if count_max_T >= 3 and grb_max_T_72_logic == True:
        fig_max_T = plt.figure(figsize=(15,5)) 

fig_max_T.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 00z AND 12z
if hour >= 0 and hour < 19:
    if count_max_T == 1:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 1, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')    


    if count_max_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_T, lats_max_T, diff_max_T_1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar1 = fig_max_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_T, lats_max_T, diff_max_T_1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar1 = fig_max_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Max T Forecast Trend (Day 3)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_T, lats_max_T, diff_max_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar2 = fig_max_T.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

    if count_max_T >= 3 and grb_max_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_T, lats_max_T, diff_max_T_1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar1 = fig.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_max_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Max T Forecast Trend (Day 3)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_T, lats_max_T, diff_max_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar2 = fig_max_T.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Day 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_max_T)
        ax3.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Max T Forecast Trend (Day 4)\nStart: '+ grib_file_4_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs3 = ax3.contourf(lons_max_T, lats_max_T, diff_max_T_3, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar3 = fig_max_T.colorbar(cs3, shrink=0.80)
        cbar3.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 12z AND 00z
if hour >= 19 and hour < 24:

    if count_max_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_T, lats_max_T, diff_max_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar1 = fig_max_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_T, lats_max_T, diff_max_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar1 = fig_max_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

    if count_max_T >= 3 and grb_max_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Max T Forecast (Day 1)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_max_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_max_T)
        
        cbar = fig_max_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_T, lats_max_T, diff_max_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar1 = fig_max_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Max T Forecast Trend (Day 3)\nStart: '+ grib_file_4_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_T, lats_max_T, diff_max_T_3, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_max_T)
        cbar2 = fig_max_T.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

#################################################################
#
#
# EXTREME HEAT
#
#
#################################################################


if hour >= 0 and hour < 19:
    if count_max_T == 2:
        fig_extreme_heat = plt.figure(figsize=(9,5))
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        fig_extreme_heat = plt.figure(figsize=(15,5))
    if count_max_T >= 3 and grb_max_T_72_logic == True:
        fig_extreme_heat = plt.figure(figsize=(12,12)) 

if hour >= 19 and hour < 24:
    if count_max_T == 2:
        fig_extreme_heat = plt.figure(figsize=(7,5))
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        fig_extreme_heat = plt.figure(figsize=(9,5))
    if count_max_T >= 3 and grb_max_T_72_logic == True:
        fig_extreme_heat = plt.figure(figsize=(15,5)) 

fig_extreme_heat.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 00z AND 12z
if hour >= 0 and hour < 19:
    if count_max_T == 1:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 1, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')    


    if count_max_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax1.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)
        cbar1 = fig_extreme_heat.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_12_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax1.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)
        cbar1 = fig_extreme_heat.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax2.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax2.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)
        cbar2 = fig_extreme_heat.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

    if count_max_T >= 3 and grb_max_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax1.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)      
        cbar1 = fig_extreme_heat.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_max_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax2.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax2.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar2 = fig_extreme_heat.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Day 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_max_T)
        ax3.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax3.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs3 = ax3.contourf(lons_max_T, lats_max_T, grb_max_T_72_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax3.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs3 = ax3.contourf(lons_max_T, lats_max_T, grb_max_T_72_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar3 = fig_extreme_heat.colorbar(cs3, shrink=0.80)
        cbar3.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 12z AND 00z
if hour >= 19 and hour < 24:

    if count_max_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Max T Forecast Trend (Day 2)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            ax1.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax1.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)                
        cbar1 = fig_extreme_heat.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_max_T >= 3 and grb_max_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax1.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)                
        cbar1 = fig_extreme_heat.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

    if count_max_T >= 3 and grb_max_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 maxT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_max_T, lats_max_T, grb_max_T_24_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)        
        cbar = fig_extreme_heat.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax1.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_max_T, lats_max_T, grb_max_T_48_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)                
        cbar1 = fig_extreme_heat.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax2.set_title('Extreme Heat (Max T >= 120\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_max_T, lats_max_T, grb_max_T_72_F, levels=np.arange(120, 140, 5), cmap='hot', transform=datacrs_max_T)
        if month > 10 or month < 4:
            ax2.set_title('Extreme Heat (Max T >= 100\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_max_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_max_T, lats_max_T, grb_max_T_72_F, levels=np.arange(100, 130, 5), cmap='hot', transform=datacrs_max_T)                        
        cbar2 = fig_extreme_heat.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Max T \N{DEGREE SIGN}F", fontweight='bold')

############################################################################################
#     
#
#
#    THIS SECTION HAS ALL THE MINIMUM TEMPERATURE GRAPHICS
#     1) MINIMUM TEMPERATURE FORECAST AND TREND
#     2) FILTERED EXTREME COLD/FROST/FREEZE
#                                 
#
#
#############################################################################################

################################################################################
# MINIMUM TEMPERATURE FORECAST AND TREND
################################################################################

mapcrs_min_T = ccrs.LambertConformal(central_longitude=-115, central_latitude=35, standard_parallels=(30,60))
datacrs_min_T = ccrs.PlateCarree()

if hour >= 14 or hour < 11:
    if count_min_T == 2:
        fig_min_T = plt.figure(figsize=(9,5))
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        fig_min_T = plt.figure(figsize=(15,5))
    if count_min_T >= 3 and grb_min_T_72_logic == True:
        fig_min_T = plt.figure(figsize=(12,12)) 

if hour >= 11 and hour < 14:
    if count_min_T == 2:
        fig_min_T = plt.figure(figsize=(7,5))
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        fig_min_T = plt.figure(figsize=(9,5))
    if count_min_T >= 3 and grb_min_T_72_logic == True:
        fig_min_T = plt.figure(figsize=(15,5)) 

fig_min_T.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 00z AND 12z
if hour >= 14 or hour < 11:
    if count_min_T == 1:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 1, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')    


    if count_min_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Night 2)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_T, lats_min_T, diff_min_T_1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar1 = fig_min_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Night 2)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_T, lats_min_T, diff_min_T_1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar1 = fig_min_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Min T Forecast Trend (Night 3)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_T, lats_min_T, diff_min_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar2 = fig_min_T.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

    if count_min_T >= 3 and grb_min_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Night 2)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_T, lats_min_T, diff_min_T_1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar1 = fig.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_min_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Min T Forecast Trend (Night 3)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_T, lats_min_T, diff_min_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar2 = fig_min_T.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Night 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_min_T)
        ax3.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Min T Forecast Trend (Night 4)\nStart: '+ grib_file_4_Min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_Min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs3 = ax3.contourf(lons_min_T, lats_min_T, diff_min_T_3, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar3 = fig_min_T.colorbar(cs3, shrink=0.80)
        cbar3.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 12z AND 00z
if hour >= 11 and hour < 14:

    if count_min_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Night 2)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_T, lats_min_T, diff_min_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar1 = fig_min_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Night 2)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_T, lats_min_T, diff_min_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar1 = fig_min_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

    if count_min_T >= 3 and grb_min_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Min T Forecast (Night 1)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        if month >= 4 and month <= 10:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(50, 140, 10), cmap='coolwarm', transform=datacrs_min_T)
        if month > 10 or month < 4:
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 110, 10), cmap='coolwarm', transform=datacrs_min_T)
        
        cbar = fig_min_T.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Night 2)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_T, lats_min_T, diff_min_T_2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar1 = fig_min_T.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Min T Forecast Trend (Night 3)\nStart: '+ grib_file_4_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_T, lats_min_T, diff_min_T_3, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs_min_T)
        cbar2 = fig_min_T.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')


################################################
#
#
# EXTREME COLD/FROST/FREEZE
#
#
################################################

mapcrs_min_T = ccrs.LambertConformal(central_longitude=-115, central_latitude=35, standard_parallels=(30,60))
datacrs_min_T = ccrs.PlateCarree()

if hour >= 14 or hour < 11:
    if count_min_T == 2:
        fig_freeze = plt.figure(figsize=(9,5))
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        fig_freeze = plt.figure(figsize=(15,5))
    if count_min_T >= 3 and grb_min_T_72_logic == True:
        fig_freeze = plt.figure(figsize=(12,12)) 

if hour >= 11 and hour < 14:
    if count_min_T == 2:
        fig_freeze = plt.figure(figsize=(7,5))
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        fig_freeze = plt.figure(figsize=(9,5))
    if count_min_T >= 3 and grb_min_T_72_logic == True:
        fig_freeze = plt.figure(figsize=(15,5)) 

fig_freeze.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS AFTER 14z OR BEFORE 11z
if hour >= 14 or hour < 11:
    if count_min_T == 1:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 1, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')    


    if count_min_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax1.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)
        cbar1 = fig_freeze.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_12_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax1.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)
        cbar1 = fig_freeze.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax2.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax2.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)
        cbar2 = fig_freeze.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

    if count_min_T >= 3 and grb_min_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT Plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_1_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax1.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)      
        cbar1 = fig_freeze.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_min_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax2.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax2.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar2 = fig_freeze.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Night 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_min_T)
        ax3.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax3.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs3 = ax3.contourf(lons_min_T, lats_min_T, grb_min_T_72_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax3.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs3 = ax3.contourf(lons_min_T, lats_min_T, grb_min_T_72_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar3 = fig_freeze.colorbar(cs3, shrink=0.80)
        cbar3.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 11z AND 14z
if hour >= 11 and hour < 14:

    if count_min_T == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Min T Forecast Trend (Day 2)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        if month >= 4 and month <= 10:
            ax1.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax1.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)                
        cbar1 = fig_freeze.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    
    if count_min_T >= 3 and grb_min_T_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax1.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)                
        cbar1 = fig_freeze.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

    if count_min_T >= 3 and grb_min_T_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 MinT plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_T)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_2_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs = ax.contourf(lons_min_T, lats_min_T, grb_min_T_24_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)        
        cbar = fig_freeze.colorbar(cs, shrink=0.80)
        cbar.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_T)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax1.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax1.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_3_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs1 = ax1.contourf(lons_min_T, lats_min_T, grb_min_T_48_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)                
        cbar1 = fig_freeze.colorbar(cs1, shrink=0.80)
        cbar1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_T)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_T)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        if month >= 4 and month <= 10:
            ax2.set_title('Abnormally Cool Areas (Min T <= 40\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_min_T, lats_min_T, grb_min_T_72_F, levels=np.arange(20, 42, 2), cmap='cool_r', transform=datacrs_min_T)
        if month > 10 or month < 4:
            ax2.set_title('Frost & Freeze (Min T <= 32\N{DEGREE SIGN}F)\nStart: '+ grib_file_4_min_T_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_T_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            cs2 = ax2.contourf(lons_min_T, lats_min_T, grb_min_T_72_F, levels=np.arange(0, 36, 4), cmap='cool_r', transform=datacrs_min_T)                        
        cbar2 = fig_freeze.colorbar(cs2, shrink=0.80)
        cbar2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
fp.close()

#############################################################
#
#
# SAVING FIGURES TO FOLDER
#
#
#############################################################

fig_max_T.savefig(f"Weather Data/NWS NDFD Max Temperature")
fig_min_T.savefig(f"Weather Data/NWS NDFD Min Temperature")
fig_extreme_heat.savefig(f"Weather Data/NWS NDFD Extreme Heat")
fig_freeze.savefig(f"Weather Data/NWS NDFD Frost And Freeze")
