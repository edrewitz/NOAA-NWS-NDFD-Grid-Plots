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
dirName = '/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus/VP.001-003/'

files = ftp.cwd(dirName)

# Opens file 
with open('ds.critfireo.bin', 'wb') as fp:
    ftp.retrbinary('RETR ds.critfireo.bin', fp.write)
ftp.close()

# Loads GRIB2 Data
ds = xr.load_dataset('ds.critfireo.bin', engine='cfgrib')

grbs = pygrib.open('ds.critfireo.bin')

grbs.seek(0)

# Gets current date and time
grb_12 = grbs[1]
if grb_12:
    grb_12_logic = True

grb_24 = grbs[2]
if grb_24:
    grb_24_logic = True

grb_48 = grbs[3]
if grb_48:
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

if grb_12_logic == True:
    prob_12 = grb_12.values
    grib1s_t = datetime(year, month, day, hr)
    grib1e_t = grib1s_t + timedelta(hours=24)

if grb_24_logic == True:
    prob_24 = grb_24.values
    grib2s_t = grb_24.validDate
    grib2e_t = grib2s_t + timedelta(hours=24)

if grb_48_logic == True:
    prob_48 = grb_48.values
    grib3s_t = grb_48.validDate
    grib3e_t = grib3s_t + timedelta(hours=24)

mapcrs = ccrs.LambertConformal(central_longitude=-100, central_latitude=38)

datacrs = ccrs.PlateCarree()

r'''

In this section we will create our different figures for each day fig...fig1...fig2...fig(n)

r'''
####################################
##### DAY 1 FIGURE #################
####################################
fig = plt.figure(figsize=(9,5))
fig.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')
fig.text(0.60, 0.82, 'Risk Index\n4-6 (Yellow) - Elevated\n6-8 (Orange) - Critical\n8-10 (Red) - Extreme', fontsize=8, fontweight='bold')

if grb_12_logic == True:

    ax = fig.add_subplot(1, 1, 1, projection=mapcrs)
    ax.set_extent([-123, -65, 25, 50], datacrs)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(USCOUNTIES, linewidth=0.75)
    ax.set_title('Critical Fire Wx Forecast (Day 1)\nStart: '+ grib1s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib1e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
    cs = ax.contourf(lons, lats, prob_12, levels=np.arange(4, 12, 2), cmap='YlOrRd', transform=datacrs)
    cbar = fig.colorbar(cs, shrink=0.80)
    cbar.set_label(label="Critical Fire Weather Risk", fontweight='bold')
    
    fig.savefig("NWS_Critical_Fire_Wx_Day_1_Forecast")
    fp.close()

if grb_12_logic == False:
    ax = fig.add_subplot(1, 1, 1, projection=mapcrs)
    ax.text(0.50, 0.50, 'NO DATA AVAILIABLE')
    fig.savefig("NWS_Critical_Fire_Wx_Day_1_Forecast")
    fp.close()

####################################
##### DAY 2 FIGURE #################
####################################    
    
fig1 = plt.figure(figsize=(9,5))
fig1.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')
fig1.text(0.60, 0.82, 'Risk Index\n4-6 (Yellow) - Elevated\n6-8 (Orange) - Critical\n8-10 (Red) - Extreme', fontsize=8, fontweight='bold')

if grb_24_logic == True:

    ax1 = fig1.add_subplot(1, 1, 1, projection=mapcrs)
    ax1.set_extent([-123, -65, 25, 50], datacrs)
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax1.add_feature(cfeature.STATES, linewidth=0.5)
    ax1.add_feature(USCOUNTIES, linewidth=0.75)
    ax1.set_title('Critical Fire Wx Forecast (Day 2)\nStart: '+ grib2s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib2e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
    cs1 = ax1.contourf(lons, lats, prob_24, levels=np.arange(4, 12, 2), cmap='YlOrRd', transform=datacrs)
    cbar1 = fig1.colorbar(cs1, shrink=0.80)
    cbar1.set_label(label="Critical Fire Weather Risk", fontweight='bold')
    
    fig1.savefig("NWS_Critical_Fire_Wx_Day_2_Forecast")
    fp.close()

if grb_24_logic == False:
    ax1 = fig1.add_subplot(1, 1, 1, projection=mapcrs)
    ax1.text(0.50, 0.50, 'NO DATA AVAILIABLE')
    fig1.savefig("NWS_Critical_Fire_Wx_Day_2_Forecast")
    fp.close()    
    
####################################
##### DAY 3 FIGURE #################
####################################     
fig2 = plt.figure(figsize=(9,5))
fig2.text(0.13, 0.06, 'Developed by: Eric Drewitz - Powered by MetPy | Data Source: NOAA/NWS/NDFD\nImage Created: ' + date1.strftime('%m/%d/%Y %H:%MZ'), fontweight='bold')
fig2.text(0.60, 0.82, 'Risk Index\n4-6 (Yellow) - Elevated\n6-8 (Orange) - Critical\n8-10 (Red) - Extreme', fontsize=8, fontweight='bold')

if grb_48_logic == True:

    ax2 = fig2.add_subplot(1, 1, 1, projection=mapcrs)
    ax2.set_extent([-123, -65, 25, 50], datacrs)
    ax2.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
    ax2.add_feature(cfeature.STATES, linewidth=0.5)
    ax2.add_feature(USCOUNTIES, linewidth=0.75)
    ax2.set_title('Critical Fire Wx Forecast (Day 3)\nStart: '+ grib3s_t.strftime('%m/%d/%Y %HZ') + '\nEnd:'+ grib3e_t.strftime('%m/%d/%Y %HZ'), fontsize=10, fontweight='bold', loc='center')
        
    cs2 = ax2.contourf(lons, lats, prob_48, levels=np.arange(4, 12, 2), cmap='YlOrRd', transform=datacrs)
    cbar2 = fig2.colorbar(cs2, shrink=0.80)
    cbar2.set_label(label="Critical Fire Weather Risk", fontweight='bold')
    
    fig2.savefig("NWS_Critical_Fire_Wx_Day_3_Forecast")
    fp.close()

if grb_48_logic == False:
    ax2 = fig2.subplot(1, 1, 1, projection=mapcrs)
    ax2.text(0.50, 0.50, 'NO DATA AVAILIABLE')
    fig2.savefig("NWS_Critical_Fire_Wx_Day_3_Forecast")
    fp.close()    
    
