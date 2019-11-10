%matplotlib inline

# Dependencies and Setup
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import datetime
import gzip
from pandas.io.json import json_normalize
import pprint as pp

import os
import json
import gmaps
import ipywidgets as widgets



filepath='current.city.json' #from bulk/openweathermap gz file that I uncompressed with a secondary tool
#note that the encoding is 'latin-1', this is because of non UTF-8 characters in some of the names  
with open(filepath,'r',encoding='latin-1') as data_file:
    weathercities=json.load(data_file)
    
 
    df = pd.DataFrame.from_dict(weathercities)#, orient='columns')
    df.dropna()
    
 
def getsample(df,number):
    '''
    *df - DataFrame
    *number of random samples to generate
    '''
    dfcount =len(df.index)
    print(dfcount)
    if dfcount <number:
        msgbox(f"Sample request is greater than {dfcount} of current dataset")
    else:   
        df = df.sample(number)
        return df

    
def getnext(mylist,pntr,numtoget):
    maxnum=len(mylist)
    counter = 0
    retstr=""
    while counter<numtoget:
        if counter == numtoget-1:
            cmend=' '
        else:
            cmend=','
            
    retstr+=mylist[counter+pntr]+cmend
    counter +=1
    return retstr
	
	
	
dfs2=getsample(df,1020)
Citylist=dfs2['name']
#dfs2.head()	

# # Import API key
from api_keys import api_key
 
    # Configure gmaps
gmaps.configure(api_key="AIzaSyAXYb2Hj_DAfwLMr_zzUmC6i3sdj-y9RgY")


url = "http://api.openweathermap.org/data/2.5/weather?"
units = "imperial"
# Build partial query URL 
query_url = f"{url}appid={api_key}&units={units}&q="
#for name in dfs1:
problems =[]

counter = 0
indxcnt = 0
#Create a set of lists for 
#Each item

ids=[]    #city id needed to merge with city.current list 
maxts=[]  #max temp for city from JSON response
mints=[]  #min temp for city from JSON response
cloudy=[] #percent cloudiness for city from JSON response
humids=[] #average humidity city from JSON response
speeds=[] #average wind speed city from JSON response
lats=[]   #lat stored in JSON from JSON response
longs=[]  #long stored in JSON for city from JSON response
sunrises=[] #unix timestamp for sunrise
sunsets=[] #unix timestamp for sunrize

#now, iterate through the panda list of cities
#and construct lists from the JSON responses
#of the items we want to track

for index,row in dfs2.T.iteritems():
    try:
        print('-------------'+ row['name'] +'---'+ str(indxcnt) +'-----------')
        response = requests.get(query_url + row['name']).json()
        ids.append(response['id'])
        lats.append(response['coord']['lat'])
        longs.append(response['coord']['lon'])
        maxts.append(response['main']["temp_max"])
        mints.append(response['main']["temp_min"])
        humids.append(response["main"]["humidity"])
        speeds.append(response["wind"]["speed"])         
        cloudy.append(response["clouds"]["all"] )
        sunrises.append(response["sys"]["sunrise"])
        sunsets.append(response["sys"]["sunset"])
        indxcnt+=1 # count how many successful passes we have 
        if indxcnt==1000:
             break
    except:
        problems.append(row['name'])
        counter+=1 # count failures
        print('PROBLEM------------'+ row['name'] +'--->'+ str(counter) +'-----------')
        continue #loop
	
import datetime
now = datetime.datetime.now() 
DayofAnalysis= (now.strftime("%Y-%m-%d"))
TimeofAnalysis =(now.strftime("%Y-%m-%d-%H:%M"))
print(TimeofAnalysis)	
		
 
# Convert Lists to a Dataframe
# Convert lists to dataframe from dictionary
# Merge JSON sourced Dataframe with Sample Dataframe
# Write CSV File of Dataframe


# build a dictionary of the lists, with name and data for each column
dict={'id':ids,
      'latf':lats,'lngf':longs,
      'maxtf':maxts,'mints':mints,
      'humidf':humids,'speedf':speeds,
      'cloudf':cloudy,
      'sunrise':sunrises,'sunset':sunsets} # a dictionary of lists

#use panda to create a DATAFRAME from the dictionary
dfilt = pd.DataFrame(dict) #, columns = ['Indexf', 'latf','lngf','maxtf','humidf','speedf','cloudf']) 
weather_data = pd.merge(dfs2,dfilt, on=['id']) #default inner join will give us only the ids common to both, which is what we want
weather_data['Daylight']=(weather_data['sunset']-weather_data['sunrise'])/3600 #hours of daylight
# Output File (CSV)

output_data_file = "output_data/cities.csv"
export_csv = df.to_csv (r'weatherdata'+TimeofAnalysis+'.csv', index = None, header=True)
#export_csv = weather_data.to_csv (r'weatherdatarandomlyselected.csv', index = None, header=True) 
# 
print("Problems encountered "+ str(counter)+ ' of ' + str(indxcnt+counter))
#weather_data.head()
## Show on Gmaps
%matplotlib inline
locations=weather_data[['latf','lngf']]
temps=weather_data['maxtf'].astype(float)

# Plot Heatmap
fig = gmaps.figure(map_type="HYBRID")

# Create heat layer
heat_layer = gmaps.heatmap_layer(locations, weights=temps, 
                                 dissipating=False, max_intensity=30,
                                 point_radius=1)


# Add layer
fig.add_layer(heat_layer)




fig




### Plotting the Data
# * Use proper labeling of the plots using plot titles (including date of analysis) and axes labels.
# * Save the plotted figures as .pngs.

def drawlatvslong(ax):
    # Build a scatter plot for each data type
    ax.scatter(weather_data["lngf"], weather_data["latf"], marker="o")

    # Incorporate the other graph properties
    plt.title("City Latitude vs. Longitude - Station Map" ,fontsize=15)
    plt.xlabel("Longitude °")
    plt.ylabel("Latitude °")
    plt.ylim(-60,80) # plt.ylim(-60,80)
    plt.xlim(-180,180)
    plt.grid(True)
    #plt.tight_layout()
    # Save the figure
    plt.savefig("CityLatvsLong.png")
    # Show plot
    # plt.show()
    
	
	 Build a scatter plot for each data type
def latvstemp(ax):
    ax.scatter(weather_data["maxtf"], weather_data["latf"], marker="o",color='r')

    # Incorporate the other graph properties
    plt.title("City Latitude vs. Max Temperature "+ DayofAnalysis,fontsize=15,color='b')
    plt.xlabel("Max Temperature (F°)")
    plt.ylabel("Latitude °")
    plt.ylim(-60,80) # plt.ylim(-60,80)
    plt.xlim(-40,130)
    plt.grid(True)
    #plt.tight_layout()

    # Save the figure
    plt.savefig("CityLatvsMaxTemp.png")

    # Show plot
    #plt.show()
	
	# Build a scatter plot for each data type
def latvshumidity(ax):
    ax.scatter(weather_data["humidf"], weather_data["latf"], marker="o",color='b')

    # Incorporate the other graph properties
    plt.title("City Latitude vs. Humidity "+ DayofAnalysis,fontsize=15)
    plt.xlabel("Humidity %")
    plt.ylabel("Latitude °")
    plt.xlim(0,100)
    plt.ylim(-50,80)
    plt.grid(True)
    #plt.tight_layout()

    # Save the figure
    plt.savefig("CityLatvsHumidity.png")

    # Show plot
    #plt.show()
	
	
	# Build a scatter plot for each data type
def latvsclouds(ax):
    ax.scatter(weather_data["cloudf"], weather_data["latf"], marker="o",color='g')
    # Incorporate the other graph properties
    plt.title("City Latitude vs. Cloudiness "+ DayofAnalysis,fontsize=15)
    plt.xlabel("Cloudiness")
    plt.ylabel("Latitude")
    plt.xlim(0,100)
    plt.ylim(-50,80)
    plt.grid(True)
    #plt.tight_layout()
    # Save the figure
    plt.savefig("CityLatvsCloudiness.png")

    # Show plot
    #plt.show()
	
	# Build a scatter plot for each data type
def latvswind(ax):
    ax.scatter(weather_data["speedf"], weather_data["latf"], marker="o",color='y')
    # Incorporate the other graph properties
    plt.title("City Latitude vs. Windspeed "+ DayofAnalysis,fontsize=15)
    plt.xlabel("Windspeed")
    plt.ylabel("Latitude")
    plt.xlim(0,50)
    plt.ylim(-50,80)
    plt.grid(True)
    #plt.tight_layout()
    # Save the figure
    plt.savefig("CityLatvsCloudiness.png")
    plt.show()
    plt.draw()
    # Show plot
    #plt.show()
	
	def scatterthis(ax,df,Xseries,Yseries,Plottitle,
                Xlabel,Ylabel,xlimlo,xlimhi,ylimlo,
                ylimhi,colorcode,gridon,filename):
    '''
    Purpose: Make a scatter plot
    *ax - Predefined graph object, should be subplotted ideally
    *df - Dataframe object containing the data to be used
    *Xserie -name of X-axis data column in df,
    *Yserie -name of Y-axis data column in df
    *Plottitle -Title to put on graph 
    *Xlabel -X axis label
    *Ylabel -Y axis label
    *Xlimlo,hi - lower and upper bounds of x axis (tuple)
    *ylimlo,hi - lower and upper bounds of y axis (tuple)
    *colorcode - a legal definition of color 
    *gridon - turn on grid True or False
    *filename - name to call plot
    
    Note that a figure should always have been
    created for using this, and that the calls to this
    will only set up the plot, but not display it.  A
    file will be saved.
    '''
    
    ax.scatter(df[Xseries], df[Yseries], marker="o",color=colorcode)
    # Incorporate the other graph properties
    plt.title(Plottitle,fontsize=15)
    plt.xlabel(Xlabel)
    plt.ylabel(Ylabel)
    ax.set_xlim(xlimlo,xlimhi)
    ax.set_ylim(ylimlo,ylimhi)
    plt.grid(True)
    #plt.tight_layout()
    # Save the figure
    plt.savefig(filename)


def drawfigure():
    fig= plt.figure(figsize=(21,14))
    from matplotlib import style
 

    #style.use('fivethirtyeight')
    #print(plt.style.available)
    frows=2
    fcols=3
    # Divide the figure into a 2x1 grid, and give me the first section
    ax1 = plt.subplot2grid((frows,fcols),(0,0),rowspan=1,colspan=2) 
    drawlatvslong(ax1)
    ax2 = plt.subplot2grid((frows,fcols),(1,2),rowspan=1,colspan=1) 
    latvstemp(ax2)
    ax3 = plt.subplot2grid((frows,fcols),(0,2),rowspan=1,colspan=1)
    latvshumidity(ax3)
    ax4 = plt.subplot2grid((frows,fcols),(1,0),rowspan=1,colspan=1) 
    latvsclouds(ax4)
    ax5 = plt.subplot2grid((frows,fcols),(1,1),rowspan=1,colspan=1) 
    latvswind(ax5)
    #ax6 = plt.subplot2grid((frows,fcols),(1,2),rowspan=1,colspan=1) 
    fig.suptitle("Graphic Data Analyis of Weather for "+TimeofAnalysis,fontsize=20)
    fig = plt.gcf()
    plt.show()
    plt.draw()
    fig.savefig('Latgraphs_'+TimeofAnalysis+'.png',dpi=100)
	
	# Build a scatter plot for each data type
def latvstemp2(ax):
    ax.scatter(weather_data["maxtf"], weather_data["latf"], marker="o",color='g')

    # Incorporate the other graph properties
    # plt.title("City Latitude vs. Max Temperature "+ DayofAnalysis,fontsize=15,color='b')
    plt.xlabel("Max Temperature (F°)")
    plt.ylabel("Latitude °")
    plt.ylim(-90,90) # plt.ylim(-60,80)
    plt.xlim(-40,130)
    plt.grid(False)
    #plt.tight_layout()

    # Save the figure
    plt.savefig("CityLatvsMaxTemp2.png")

    # Show plot
    #plt.show()
	
	def drawfigure2(Title):
    fig= plt.figure(figsize=(10,10))
    from matplotlib import style
 

    #style.use('fivethirtyeight')
    #print(plt.style.available)
    frows=5
    fcols=5
    # Divide the figure into a 2x1 grid, and give me the first section
    ax1 = plt.subplot2grid((frows,fcols),(0,0),rowspan=2,colspan=2) 
    scatterthis(ax=ax1,
                df=weather_data,
                Yseries='Daylight',
                Xseries= 'maxtf',
                Xlabel='Maximum Temperature',
                Ylabel="Daylight Hours", 
                xlimlo=-40,
                xlimhi=120,
                ylimlo =0,
                ylimhi=24,
                gridon=False,
                colorcode='r',
                Plottitle='Daylight vs Temperature'+DayofAnalysis, 
                filename ='Daylightplot'+TimeofAnalysis +'.png'            
       )
    ax2 = ax1.twinx()#Dual Axis Plot
    latvstemp2(ax2)
    #this will show the direct correlation between length of day and Latitude, not news.
    ax3 = plt.subplot2grid((frows,fcols),(0,3),rowspan=2,colspan=2) 
                 
    scatterthis(ax=ax3,
                df=weather_data,
                Yseries='latf',
                Xseries='Daylight',
                Xlabel='Daylight Hours',
                Ylabel="Latitude °", 
                xlimlo=0,
                xlimhi=24,
                ylimlo =-80,
                ylimhi=80,
                gridon=False,
                colorcode='b',
                Plottitle='Daylight vs Latitude'+DayofAnalysis, 
                filename ='DaylightLatitudeplot'+TimeofAnalysis +'.png'          
       )
#     ax3 = plt.subplot2grid((frows,fcols),(0,2),rowspan=1,colspan=1)
#     latvshumidity(ax3)
#     ax4 = plt.subplot2grid((frows,fcols),(1,0),rowspan=1,colspan=1) 
#     latvsclouds(ax4)
#     ax5 = plt.subplot2grid((frows,fcols),(1,1),rowspan=1,colspan=1) 
#     latvswind(ax5)
#     #ax6 = plt.subplot2grid((frows,fcols),(1,2),rowspan=1,colspan=1) 
    fig.suptitle(Title+DayofAnalysis,fontsize=20)
    fig = plt.gcf()
    plt.show()
    plt.draw()
    fig.savefig('DaylightGraphs_'+TimeofAnalysis+'.png')
	
	
	%matplotlib inline
drawfigure()
#drawfigure2('Analysis of Daylight vs Temperature Correlation')