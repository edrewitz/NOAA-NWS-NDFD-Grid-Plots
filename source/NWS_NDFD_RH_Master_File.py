#====================================================================================================
# THIS IS THE MASTER FILE FOR THE NWS NDFD GRAPHICS
#
# THESE GRAPHICS INCLUDE:
# 1) NWS Forecast and forecast trends for Max RH
# 2) NWS Forecast and forecast trends for Min RH
# 3) NWS Max RH Forecast filtering areas with poor overnight RH recovery (RH <= 30%)
# 4) NWS Min RH Forecast filtering areas with RFW RH criteria (RH <= 15%)
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
# DOWNLOADS THE NWS MAX AND MIN RH NDFD GRIDS FOR PACIFIC SOUTHWEST
####################################################

# MAX RH
with open('ds.maxrh.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.maxrh.bin', fp.write)


# MIN RH
with open('ds.minrh.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.minrh.bin', fp.write)


ftp.close()
###########################################################
# DATA ARRAYS FOR DIFFERENT PARAMETERS
###########################################################

# MAX RH
ds_max_rh = xr.load_dataset('ds.maxrh.bin', engine='cfgrib')
grbs_max_rh = pygrib.open('ds.maxrh.bin')
grbs_max_rh.seek(0)

# MIN RH
ds_min_rh = xr.load_dataset('ds.minrh.bin', engine='cfgrib')
grbs_min_rh = pygrib.open('ds.minrh.bin')
grbs_min_rh.seek(0)

####################################################################
# CHECKS FOR THE NUMBER OF GRIB FILES FOR EACH PARAMETER
####################################################################

# MAX RH
count_max_rh = 0
for grb in grbs_max_rh:
    count_max_rh = count_max_rh + 1
if count_max_rh == 1:
    grb_max_rh_12 = grbs_max_rh[1]
    grb_max_rh_12_logic = True
    grb_max_rh_24_logic = False
    grb_max_rh_48_logic = False
    grb_max_rh_72_logic = False

if count_max_rh == 2:
    grb_max_rh_12 = grbs_max_rh[1]
    grb_max_rh_24 = grbs_max_rh[2]
    grb_max_rh_12_logic = True
    grb_max_rh_24_logic = True
    grb_max_rh_48_logic = False
    grb_max_rh_72_logic = False
    
if count_max_rh == 3: 
    grb_max_rh_12 = grbs_max_rh[1]
    grb_max_rh_24 = grbs_max_rh[2]
    grb_max_rh_48 = grbs_max_rh[3]
    grb_max_rh_12_logic = True
    grb_max_rh_24_logic = True
    grb_max_rh_48_logic = True
    grb_max_rh_72_logic = False

if count_max_rh >= 4: 
    grb_max_rh_12 = grbs_max_rh[1]
    grb_max_rh_24 = grbs_max_rh[2]
    grb_max_rh_48 = grbs_max_rh[3]
    grb_max_rh_72 = grbs_max_rh[4]
    grb_max_rh_12_logic = True
    grb_max_rh_24_logic = True
    grb_max_rh_48_logic = True
    grb_max_rh_72_logic = True


# MIN RH
count_min_rh = 0
for grb in grbs_min_rh:
    count_min_rh = count_min_rh + 1
if count_min_rh == 1:
    grb_min_rh_12 = grbs_min_rh[1]
    grb_min_rh_12_logic = True
    grb_min_rh_24_logic = False
    grb_min_rh_48_logic = False
    grb_min_rh_72_logic = False

if count_min_rh == 2:
    grb_min_rh_12 = grbs_min_rh[1]
    grb_min_rh_24 = grbs_min_rh[2]
    grb_min_rh_12_logic = True
    grb_min_rh_24_logic = True
    grb_min_rh_48_logic = False
    grb_min_rh_72_logic = False
    
if count_min_rh == 3: 
    grb_min_rh_12 = grbs_min_rh[1]
    grb_min_rh_24 = grbs_min_rh[2]
    grb_min_rh_48 = grbs_min_rh[3]
    grb_min_rh_12_logic = True
    grb_min_rh_24_logic = True
    grb_min_rh_48_logic = True
    grb_min_rh_72_logic = False

if count_min_rh >= 4: 
    grb_min_rh_12 = grbs_min_rh[1]
    grb_min_rh_24 = grbs_min_rh[2]
    grb_min_rh_48 = grbs_min_rh[3]
    grb_min_rh_72 = grbs_min_rh[4]
    grb_min_rh_12_logic = True
    grb_min_rh_24_logic = True
    grb_min_rh_48_logic = True
    grb_min_rh_72_logic = True


# LAT/LON COORDINATES FOR DIFFERENT PARAMETERS
lats_max_rh, lons_max_rh = grb_max_rh_12.latlons()
lats_min_rh, lons_min_rh = grb_min_rh_12.latlons()

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
# RH grids are from 18z to 06z and 06z to 18z 
hr_RH_06z = 6
hr_RH_18z = 18
    
###############
# MAX RH 
###############

if hour >= 6 and hour <=18:
    grib_file_1_max_rh_start = datetime(year, month, day, hr_RH_06z)
    grib_file_1_max_rh_end = grib_file_1_max_rh_start + timedelta(hours=12)

else:
    grib_file_1_max_rh_start = grb_max_rh_12.validDate
    grib_file_1_max_rh_end = grib_file_1_max_rh_start + timedelta(hours=12)


if grb_max_rh_24_logic == True:
    diff_max_rh_1 = grb_max_rh_24.values - grb_max_rh_12.values
    grib_file_2_max_rh_start = grb_max_rh_24.validDate
    grib_file_2_max_rh_end = grib_file_2_max_rh_start + timedelta(hours=12)
    
    if grb_max_rh_48_logic == True:
        diff_max_rh_2 = grb_max_rh_48.values - grb_max_rh_24.values
        grib_file_3_max_rh_start = grb_max_rh_48.validDate
        grib_file_3_max_rh_end = grib_file_3_max_rh_start + timedelta(hours=12)

        if grb_max_rh_72_logic == True:
            diff_max_rh_3 = grb_max_rh_72.values - grb_max_rh_48.values
            grib_file_4_max_rh_start = grb_max_rh_72.validDate
            grib_file_4_max_rh_end = grib_file_4_max_rh_start + timedelta(hours=12)
        

#################################
# MIN RH
#################################

if hour >= 18 and hour < 24:
    grib_file_1_min_rh_start = datetime(year, month, day, hr_RH_18z)
    grib_file_1_min_rh_end = grib_file_1_min_rh_start + timedelta(hours=12)

elif hour >= 0 and hour <= 6:
    grib_file_1_min_rh_start = datetime(year, month, day, hr_RH_18z) - timedelta(days=1)
    grib_file_1_min_rh_end = grib_file_1_min_rh_start + timedelta(hours=12)


else:
    grib_file_1_min_rh_start = grb_min_rh_12.validDate
    grib_file_1_min_rh_end = grib_file_1_min_rh_start + timedelta(hours=12)


if grb_min_rh_24_logic == True:
    grib_file_2_min_rh_start = grb_min_rh_24.validDate
    diff_min_rh_1 = grb_min_rh_24.values - grb_min_rh_12.values
    grib_file_2_min_rh_end = grib_file_2_min_rh_start + timedelta(hours=12)
    
    if grb_min_rh_48_logic == True:
        grib_file_3_min_rh_start = grb_min_rh_48.validDate
        diff_min_rh_2 = grb_min_rh_48.values - grb_min_rh_24.values
        grib_file_3_min_rh_end = grib_file_3_min_rh_start + timedelta(hours=12)

        if grb_min_rh_72_logic == True:
            diff_min_rh_3 = grb_min_rh_72.values - grb_min_rh_48.values
            grib_file_4_min_rh_start = grb_min_rh_72.validDate
            grib_file_4_min_rh_end = grib_file_4_min_rh_start + timedelta(hours=12)

################################################
# ***GRAPHICS SECTION***
################################################

#*****************************************************************************************************
#*****************************************************************************************************
############################################################################################
#     
#
#
#    THIS SECTION HAS ALL THE MAXIMUM RH GRAPHICS
#     1) MAXIMUM RH FORECAST AND TREND
#     2) MAXIMUM RH TRENDS ONLY
#     3) FILTERED MAXIMUM RH FORECAST VALUES FOR POOR RECOVERY RH (MAX RH <= 30%)                             
#
#
#############################################################################################

################################################
#
#
#
# MAX RH FORECAST AND TRENDS
#
#
#
################################################

mapcrs_max_RH = ccrs.LambertConformal(central_longitude=-115, central_latitude=35, standard_parallels=(30,60))
datacrs_max_RH = ccrs.PlateCarree()

if hour > 18 or hour <= 6:
    if count_max_rh == 2:
        fig_max_RH = plt.figure(figsize=(9,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        fig_max_RH = plt.figure(figsize=(15,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        fig_max_RH = plt.figure(figsize=(12,12)) 

if hour > 6 and hour <= 18:
    if count_max_rh == 2:
        fig_max_RH = plt.figure(figsize=(7,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        fig_max_RH = plt.figure(figsize=(9,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        fig_max_RH = plt.figure(figsize=(15,5)) 

           
fig_max_RH.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 18z AND 06z
if hour > 18 or hour <= 6:
    if count_max_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast (Night 1)\nStart: '+ grib_file_1_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_max_RH)
        cbar_RH = fig_max_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast Trend (Night 2)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, diff_max_rh_1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH Trend (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast (Night 1)\nStart: '+ grib_file_1_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast Trend (Night 2)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, diff_max_rh_1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Maximum RH Forecast Trend (Night 3)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_rh, lats_max_rh, diff_max_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH2 = fig_max_RH.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Max RH Trend (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast (Night 1)\nStart: '+ grib_file_1_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast Trend (Night 2)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, diff_max_rh_1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_max_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Maximum RH Forecast Trend (Night 3)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_rh, lats_max_rh, diff_max_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH2 = fig_max_RH.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Max RH Trend (%)", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Night 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_max_RH)
        ax3.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Maximum RH Forecast Trend (Night 4)\nStart: '+ grib_file_4_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs3 = ax3.contourf(lons_max_rh, lats_max_rh, diff_max_rh_3, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH3 = fig_max_RH_TREND_ONLY.colorbar(cs3, shrink=0.80)
        cbar_RH3.set_label(label="Max RH Trend (%)", fontweight='bold')
        
# PLOT FOR WHEN PROGRAM RUNS BETWEEN 06z AND 18z
if hour > 6 and hour <= 18:
    if count_max_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 1, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast (Night 1)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_max_RH)
        cbar_RH = fig_max_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast (Night 1)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast Trend (Night 2)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, diff_max_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH Trend (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast (Night 1)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast Trend (Night 2)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, diff_max_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Maximum RH Forecast Trend (Night 3)\nStart: '+ grib_file_4_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_rh, lats_max_rh, diff_max_rh_3, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_max_RH)
        cbar_RH2 = fig_max_RH.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Max RH Trend (%)", fontweight='bold')


#######################################################
#
#
#
# MAXIMUM RH FILTERED <= 30% (POOR RH RECOVERY ONLY)
#
#
#       
#######################################################

if hour > 18 or hour <= 6:
    if count_max_rh == 2:
        fig_max_RH_filtered = plt.figure(figsize=(9,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        fig_max_RH_filtered = plt.figure(figsize=(15,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        fig_max_RH_filtered = plt.figure(figsize=(12,12)) 

if hour > 6 and hour <= 18:
    if count_max_rh == 2:
        fig_max_RH_filtered = plt.figure(figsize=(7,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        fig_max_RH_filtered = plt.figure(figsize=(9,5))
    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        fig_max_RH_filtered = plt.figure(figsize=(15,5)) 
    
fig_max_RH_filtered.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 18z AND 06z
if hour > 18 or hour <= 6:
    if count_max_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_1_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_12.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH = fig_max_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_1_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_12.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_max_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_rh, lats_max_rh, grb_max_rh_48.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH2 = fig_max_RH_filtered.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Max RH (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_1_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_12.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_max_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_max_rh, lats_max_rh, grb_max_rh_48.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH2 = fig_max_RH_filtered.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Max RH (%)", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Night 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_max_RH)
        ax3.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_4_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs3 = ax3.contourf(lons_max_rh, lats_max_rh, grb_max_rh_72.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH3 = fig_max_RH_TREND_ONLY.colorbar(cs3, shrink=0.80)
        cbar_RH3.set_label(label="Max RH (%)", fontweight='bold')


# PLOT FOR WHEN PROGRAM RUNS BETWEEN 01z AND 13z
if hour > 6 and hour <= 18:
    if count_max_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Night 1 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 1, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH = fig_max_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Night 2 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, grb_max_rh_48.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH (%)", fontweight='bold')

    if count_max_rh >= 3 and grb_max_rh_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Night 2 maxRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_max_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_2_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_max_rh, lats_max_rh, grb_max_rh_24.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        
        cbar_RH = fig_max_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Max RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Night 3
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_max_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_3_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_max_rh, lats_max_rh, grb_max_rh_48.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH1 = fig_max_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Max RH (%)", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Night 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(1, 3, 3, projection=mapcrs_max_RH)
        ax3.set_extent([-122, -114, 31, 39], datacrs_max_RH)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('Maximum RH Forecast\n(Filtered Maximum RH <= 30%)\nStart: '+ grib_file_4_max_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_max_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs3 = ax3.contourf(lons_max_rh, lats_max_rh, grb_max_rh_72.values, levels=np.arange(0, 31, 1), cmap='YlOrBr_r', transform=datacrs_max_RH)
        cbar_RH3 = fig_max_RH_filtered.colorbar(cs3, shrink=0.80)
        cbar_RH3.set_label(label="Max RH (%)", fontweight='bold')       

#*****************************************************************************************************
#*****************************************************************************************************
############################################################################################
#     
#
#
#    THIS SECTION HAS ALL THE MINIMUM RH GRAPHICS
#     1) MINIMUM RH FORECAST AND TREND
#     2) MINIMUM RH TRENDS ONLY
#     3) FILTERED MINIMUM RH FORECAST VALUES EXCEPTIONALLY LOW RH (MIN RH <= 15%)                             
#
#
#############################################################################################


##############################################
#
#
#        
# MINIMUM RH FORECAST AND TRENDS
#
#
#        
##############################################

mapcrs_min_RH = ccrs.LambertConformal(central_longitude=-115, central_latitude=35, standard_parallels=(30,60))
datacrs_min_RH = ccrs.PlateCarree()


if hour > 6 and hour <= 18:
    if count_min_rh == 2:
        fig_min_RH = plt.figure(figsize=(9,5))
    if count_min_rh >= 3 and grb_min_rh_72_logic == False:
        fig_min_RH = plt.figure(figsize=(15,5))
    if count_min_rh >= 3 and grb_min_rh_72_logic == True:
        fig_min_RH = plt.figure(figsize=(12,12)) 

if hour > 18 or hour <= 6:
    if count_min_rh == 2:
        fig_min_RH = plt.figure(figsize=(7,5))
    if count_min_rh >= 3 and grb_min_rh_72_logic == False:
        fig_min_RH = plt.figure(figsize=(9,5))
    if count_min_rh >= 3 and grb_min_rh_72_logic == True:
        fig_min_RH = plt.figure(figsize=(15,5)) 
            
fig_min_RH.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 18z AND 06z
if hour > 18 or hour <= 6:
    if count_min_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_min_RH)
        cbar_RH = fig_min_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')

    if count_min_rh >= 3 and grb_min_rh_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_min_RH)
        
        cbar_RH = fig_min_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, diff_min_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')

    if count_min_rh >= 3 and grb_min_rh_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_min_RH)
        
        cbar_RH = fig_min_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, diff_min_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')        
        #---------------------------------------------------------------------------------------------------------------------
        # Day 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Minimum RH Forecast Trend (Day 3)\nStart: '+ grib_file_4_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_rh, lats_min_rh, diff_min_rh_3, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH2 = fig_min_RH.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 01z AND 13z
if hour > 6 and hour <= 18:
    if count_min_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_min_RH)
        cbar_RH = fig_min_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, diff_min_rh_1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')

    if count_min_rh >= 3 and grb_min_rh_72_logic == False:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_min_RH)
        
        cbar_RH = fig_min_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, diff_min_rh_1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Minimum RH Forecast Trend (Day 3)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_rh, lats_min_rh, diff_min_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH2 = fig_min_RH.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

    if count_min_rh >= 3 and grb_min_rh_72_logic == True:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(2, 2, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs_min_RH)
        
        cbar_RH = fig_min_RH.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(2, 2, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, diff_min_rh_1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(2, 2, 3, projection=mapcrs_min_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Minimum RH Forecast Trend (Day 3)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_rh, lats_min_rh, diff_min_rh_2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH2 = fig_min_RH.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

        #---------------------------------------------------------------------------------------------------------------------
        # Day 4 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax3 = plt.subplot(2, 2, 4, projection=mapcrs_min_RH)
        ax3.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax3.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax3.add_feature(cfeature.STATES, linewidth=0.5)
        ax3.add_feature(USCOUNTIES, linewidth=0.75)
        ax3.set_title('minimum RH Forecast Trend (Night 4)\nStart: '+ grib_file_4_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_4_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs3 = ax3.contourf(lons_min_rh, lats_min_rh, diff_min_rh_3, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs_min_RH)
        cbar_RH3 = fig_min_RH.colorbar(cs3, shrink=0.80)
        cbar_RH3.set_label(label="min RH Trend (%)", fontweight='bold')

#################################################
#
#
#        
# MINIMUM RH FILTERED <=15%
#
#
#        
#################################################

if count_min_rh == 2:
    fig_min_RH_filtered = plt.figure(figsize=(9,5))
if count_min_rh == 3 and hour < 6:
    fig_min_RH_filtered = plt.figure(figsize=(9,5))
if count_min_rh == 3 and hour >= 6:
    fig_min_RH_filtered = plt.figure(figsize=(15,5))
    
fig_min_RH_filtered.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')

# PLOT FOR WHEN PROGRAM RUNS BETWEEN 13z AND 01z
if hour > 18 or hour <= 6:
    if count_min_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH = fig_min_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')

    if count_min_rh == 3 and hour >= 6:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        
        cbar_RH = fig_min_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_rh, lats_min_rh, grb_min_rh_48.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH2 = fig_min_RH_filtered.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

    if count_min_rh == 3 and hour < 6:
       #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 1, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 2, 2, projection=mapcrs_min_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_rh, lats_min_rh, grb_min_rh_48.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH2 = fig_min_RH_filtered.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

        
# PLOT FOR WHEN PROGRAM RUNS BETWEEN 01z AND 13z
if hour > 6 and hour <= 18:
    if count_min_rh == 2:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 2, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH = fig_min_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 2, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
            
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')

    if count_min_rh == 3:
        #------------------------------------------------------------------------------------------------------------------
        # Day 1 minRH plot
        #-------------------------------------------------------------------------------------------------------------------
        ax = plt.subplot(1, 3, 1, projection=mapcrs_min_RH)
        ax.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        ax.add_feature(USCOUNTIES, linewidth=0.75)
        ax.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_1_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_1_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs = ax.contourf(lons_min_rh, lats_min_rh, grb_min_rh_12.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        
        cbar_RH = fig_min_RH_filtered.colorbar(cs, shrink=0.80)
        cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 2 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax1 = plt.subplot(1, 3, 2, projection=mapcrs_min_RH)
        ax1.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax1.add_feature(cfeature.STATES, linewidth=0.5)
        ax1.add_feature(USCOUNTIES, linewidth=0.75)
        ax1.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_2_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_2_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs1 = ax1.contourf(lons_min_rh, lats_min_rh, grb_min_rh_24.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH1 = fig_min_RH_filtered.colorbar(cs1, shrink=0.80)
        cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')
        #---------------------------------------------------------------------------------------------------------------------
        # Day 3 Trend
        #--------------------------------------------------------------------------------------------------------------------------------
        ax2 = plt.subplot(1, 3, 3, projection=mapcrs_min_RH)
        ax2.set_extent([-122, -114, 31, 39], datacrs_min_RH)
        ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
        ax2.add_feature(cfeature.STATES, linewidth=0.5)
        ax2.add_feature(USCOUNTIES, linewidth=0.75)
        ax2.set_title('Minimum RH Forecast\n(Filtered Minimum RH <= 15%)\nStart: '+ grib_file_3_min_rh_start.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib_file_3_min_rh_end.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
        cs2 = ax2.contourf(lons_min_rh, lats_min_rh, grb_min_rh_48.values, levels=np.arange(0, 16, 1), cmap='YlOrBr_r', transform=datacrs_min_RH)
        cbar_RH2 = fig_min_RH_filtered.colorbar(cs2, shrink=0.80)
        cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

#######################################
# SAVING FIGURES
#######################################
fig_max_RH.savefig(f"Weather Data/NWS NDFD Max RH")
fig_max_RH_filtered.savefig(f"Weather Data/NWS Filtered Poor Recovery Max RH")
fig_min_RH.savefig(f"Weather Data/NWS NDFD Min RH")
fig_min_RH_filtered.savefig(f"Weather Data/NWS Filtered Min RH")
