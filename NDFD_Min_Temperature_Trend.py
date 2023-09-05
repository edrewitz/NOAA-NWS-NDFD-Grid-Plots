# Imports
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
import pygrib
import metpy.plots as mpplots
from metpy.units import units
import metpy.calc as mpcalc
import pandas as pd
from metpy.units import pandas_dataframe_to_unit_arrays
from metpy.plots import USCOUNTIES
from ftplib import FTP
import os

# Connects to NWS FTP Server
ftp = FTP('tgftp.nws.noaa.gov')
ftp.login()
dirName = '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.pacswest/VP.001-003/'

files = ftp.cwd(dirName)

# Opens file 
with open('ds.mint.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.mint.bin', fp.write)
ftp.close()

# Loads GRIB2 Data
ds = xr.load_dataset('ds.mint.bin', engine='cfgrib')

grbs = pygrib.open('ds.mint.bin')

grbs.seek(0)

# Gets current date and time
count = 0
for grb in grbs:
    count = count + 1
if count == 1:
    grb_12 = grbs[1]
    grb_12_logic = True
    grb_24_logic = False
    grb_48_logic = False

if count == 2:
    grb_12 = grbs[1]
    grb_24 = grbs[2]
    grb_12_logic = True
    grb_24_logic = True
    grb_48_logic = False
    
if count == 3: 
    grb_12 = grbs[1]
    grb_24 = grbs[2]
    grb_48 = grbs[3]
    grb_12_logic = True
    grb_24_logic = True
    grb_48_logic = True


lats, lons = grb_12.latlons()

now = datetime.utcnow()
year = now.year
month = now.month
day = now.day
hour = now.hour
minute=now.minute

date = datetime(year, month, day, hour)
date1 = datetime(year, month, day, hour, minute)
hr = 12
hr1 = 0
frac = 9/5

if hour >= 0 and hour <=12:
    grib1s_t = datetime(year, month, day, hr1)
    grib1e_t = grib1s_t + timedelta(hours=12)

else:
    grib1s_t = grb_12.validDate
    grib1e_t = grib1s_t + timedelta(hours=12)

if grb_12_logic == True:
    grb_12_C = (grb_12.values - 273.15)
    grb_12_F = (frac * grb_12_C) + 32
   
    if grb_24_logic == True:
        grb_24_C = (grb_24.values - 273.15)
        grb_24_F = (frac * grb_24_C) + 32
        diff1 = grb_24_F - grb_12_F
        grib2s_t = grb_24.validDate
        grib2e_t = grib2s_t + timedelta(hours=12)
        
        if grb_48_logic == True:
            grb_48_C = (grb_48.values - 273.15)
            grb_48_F = (frac * grb_48_C) + 32
            diff2 = grb_48_F - grb_24_F
            grib3s_t = grb_48.validDate
            grib3e_t = grib3s_t + timedelta(hours=12)

mapcrs = ccrs.LambertConformal(central_longitude=-115, central_latitude=35, standard_parallels=(30,60))

datacrs = ccrs.PlateCarree()

if count == 2:
    fig = plt.figure(figsize=(9,5))

if count == 3:
    fig = plt.figure(figsize=(15,5))
#plt.title('Overnight Recovery Maximum Relative Humidity Night 1 Forecast + Night 2 Trend\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')
fig.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')



if count == 2:

    #------------------------------------------------------------------------------------------------------------------
    # Day 1 maxT plot
    #-------------------------------------------------------------------------------------------------------------------
    ax = plt.subplot(1, 2, 1, projection=mapcrs)
    ax.set_extent([-122, -114, 31, 39], datacrs)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(USCOUNTIES, linewidth=0.75)
    ax.set_title('Min T Forecast (Day 1)\nStart: '+ grib1s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib1e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs = ax.contourf(lons, lats, grb_24_F, levels=np.arange(30, 100, 10), cmap='coolwarm', transform=datacrs)
    cbar_RH = fig.colorbar(cs, shrink=0.80)
    cbar_RH.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    #---------------------------------------------------------------------------------------------------------------------
    # Day 2 Trend
    #--------------------------------------------------------------------------------------------------------------------------------
    ax1 = plt.subplot(1, 2, 2, projection=mapcrs)
    ax1.set_extent([-122, -114, 31, 39], datacrs)
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax1.add_feature(cfeature.STATES, linewidth=0.5)
    ax1.add_feature(USCOUNTIES, linewidth=0.75)
    ax1.set_title('Min T Forecast Trend (Day 2)\nStart: '+ grib2s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib2e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs1 = ax1.contourf(lons, lats, diff1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs)
    cbar_RH1 = fig.colorbar(cs1, shrink=0.80)
    cbar_RH1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

if count == 3:
    #------------------------------------------------------------------------------------------------------------------
    # Day 1 maxRH plot
    #-------------------------------------------------------------------------------------------------------------------
    ax = plt.subplot(1, 3, 1, projection=mapcrs)
    ax.set_extent([-122, -114, 31, 39], datacrs)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(USCOUNTIES, linewidth=0.75)
    ax.set_title('Min T Forecast (Day 1)\nStart: '+ grib1s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib1e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs = ax.contourf(lons, lats, grb_24_F, levels=np.arange(50, 130, 10), cmap='coolwarm', transform=datacrs)
    
    cbar_RH = fig.colorbar(cs, shrink=0.80)
    cbar_RH.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    #---------------------------------------------------------------------------------------------------------------------
    # Day 2 Trend
    #--------------------------------------------------------------------------------------------------------------------------------
    ax1 = plt.subplot(1, 3, 2, projection=mapcrs)
    ax1.set_extent([-122, -114, 31, 39], datacrs)
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax1.add_feature(cfeature.STATES, linewidth=0.5)
    ax1.add_feature(USCOUNTIES, linewidth=0.75)
    ax1.set_title('Min T Forecast Trend (Day 2)\nStart: '+ grib2s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib2e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs1 = ax1.contourf(lons, lats, diff1, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs)
    cbar_RH1 = fig.colorbar(cs1, shrink=0.80)
    cbar_RH1.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')
    #---------------------------------------------------------------------------------------------------------------------
    # Day 3 Trend
    #--------------------------------------------------------------------------------------------------------------------------------
    ax2 = plt.subplot(1, 3, 3, projection=mapcrs)
    ax2.set_extent([-122, -114, 31, 39], datacrs)
    ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax2.add_feature(cfeature.STATES, linewidth=0.5)
    ax2.add_feature(USCOUNTIES, linewidth=0.75)
    ax2.set_title('Min T Forecast Trend (Day 3)\nStart: '+ grib3s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib3e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs2 = ax2.contourf(lons, lats, diff2, levels=np.arange(-30, 30, 1), cmap='coolwarm', transform=datacrs)
    cbar_RH2 = fig.colorbar(cs2, shrink=0.80)
    cbar_RH2.set_label(label="Min T \N{DEGREE SIGN}F", fontweight='bold')

plt.savefig("NWS_min_T_Forecast")
fp.close()
