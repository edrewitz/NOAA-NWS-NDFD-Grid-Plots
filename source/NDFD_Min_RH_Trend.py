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
with open('ds.minrh.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.minrh.bin', fp.write)
ftp.close()

# Loads GRIB2 Data
ds = xr.load_dataset('ds.minrh.bin', engine='cfgrib')

grbs = pygrib.open('ds.minrh.bin')

grbs.seek(0)

# Checks to see how many times there are in the GRIB2 file 
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

# Gets current date and time
now = datetime.utcnow()
year = now.year
month = now.month
day = now.day
hour = now.hour
minute=now.minute

date = datetime(year, month, day, hour)
date1 = datetime(year, month, day, hour, minute)
hr = 18
hr1 = 6

if hour >= 18 or hour <=6:
    grib1s_t = datetime(year, month, day, hr)
    grib1e_t = grib1s_t + timedelta(hours=12)

else:
    grib1s_t = grb_12.validDate
    grib1e_t = grib1s_t + timedelta(hours=12)


if grb_24_logic == True:
    diff1 = grb_24.values - grb_12.values
    grib2s_t = grb_24.validDate
    grib2e_t = grib2s_t + timedelta(hours=12)
    
    if grb_48_logic == True:
        diff2 = grb_48.values - grb_24.values
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
    # Day 1 minRH plot
    #-------------------------------------------------------------------------------------------------------------------
    ax = plt.subplot(1, 2, 1, projection=mapcrs)
    ax.set_extent([-122, -114, 31, 39], datacrs)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(USCOUNTIES, linewidth=0.75)
    ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib1s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib1e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs = ax.contourf(lons, lats, grb.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs)
    cbar_RH = fig.colorbar(cs, shrink=0.80)
    cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
    #---------------------------------------------------------------------------------------------------------------------
    # Day 2 Trend
    #--------------------------------------------------------------------------------------------------------------------------------
    ax1 = plt.subplot(1, 2, 2, projection=mapcrs)
    ax1.set_extent([-122, -114, 31, 39], datacrs)
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax1.add_feature(cfeature.STATES, linewidth=0.5)
    ax1.add_feature(USCOUNTIES, linewidth=0.75)
    ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib2s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib2e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs1 = ax1.contourf(lons, lats, diff1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs)
    cbar_RH1 = fig.colorbar(cs1, shrink=0.80)
    cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')

if count == 3:
    #------------------------------------------------------------------------------------------------------------------
    # Day 1 maxRH plot
    #-------------------------------------------------------------------------------------------------------------------
    ax = plt.subplot(1, 3, 1, projection=mapcrs)
    ax.set_extent([-122, -114, 31, 39], datacrs)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(USCOUNTIES, linewidth=0.75)
    ax.set_title('Minimum RH Forecast (Day 1)\nStart: '+ grib1s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib1e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs = ax.contourf(lons, lats, grb_12.values, levels=np.arange(0, 100, 5), cmap='YlGnBu', transform=datacrs)
    
    cbar_RH = fig.colorbar(cs, shrink=0.80)
    cbar_RH.set_label(label="Min RH (%)", fontweight='bold')
    #---------------------------------------------------------------------------------------------------------------------
    # Day 2 Trend
    #--------------------------------------------------------------------------------------------------------------------------------
    ax1 = plt.subplot(1, 3, 2, projection=mapcrs)
    ax1.set_extent([-122, -114, 31, 39], datacrs)
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax1.add_feature(cfeature.STATES, linewidth=0.5)
    ax1.add_feature(USCOUNTIES, linewidth=0.75)
    ax1.set_title('Minimum RH Forecast Trend (Day 2)\nStart: '+ grib2s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib2e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs1 = ax1.contourf(lons, lats, diff1, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs)
    cbar_RH1 = fig.colorbar(cs1, shrink=0.80)
    cbar_RH1.set_label(label="Min RH Trend (%)", fontweight='bold')
    #---------------------------------------------------------------------------------------------------------------------
    # Day 3 Trend
    #--------------------------------------------------------------------------------------------------------------------------------
    ax2 = plt.subplot(1, 3, 3, projection=mapcrs)
    ax2.set_extent([-122, -114, 31, 39], datacrs)
    ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax2.add_feature(cfeature.STATES, linewidth=0.5)
    ax2.add_feature(USCOUNTIES, linewidth=0.75)
    ax2.set_title('Minimum RH Forecast Trend (Day 3)\nStart: '+ grib3s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib3e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
    
    cs2 = ax2.contourf(lons, lats, diff2, levels=np.arange(-50, 50, 5), cmap='BrBG', transform=datacrs)
    cbar_RH2 = fig.colorbar(cs2, shrink=0.80)
    cbar_RH2.set_label(label="Min RH Trend (%)", fontweight='bold')

plt.savefig("NWS_min_RH_Forecast")
fp.close()


















