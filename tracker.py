import cartopy
import cartopy.crs as ccrs
import numpy as np
#import pylab as plt
import ephem
import datetime
import requests
import matplotlib.pyplot as plt
import tkinter

from ephem import degree
from datetime import datetime as date_t

def loadTLE(filename):
    """ Loads a TLE file and creates a list of satellites."""
    f = open(filename)
    satlist = []
    l1 = f.readline()
    while l1:
        l2 = f.readline()
        l3 = f.readline()
        sat = ephem.readtle(l1,l2,l3)
        satlist.append(sat)
        #print (sat.name)
        l1 = f.readline()

    f.close()
    print (len(satlist), "satellites loaded into list")
    return satlist


def main():
	print("start")
	window = tkinter.Tk()
	window.title("GUI")
	Titulo = tkinter.Label(window, text = "TSM Patagonia: Posicionado de constelacion satelital").pack()
	tkinter.Label(window, text="Latitud").pack()
	

	var_1 = tkinter.Entry(window)
	var_1.pack()
	tkinter.Label(window, text="Longitud").pack()
	var_2 = tkinter.Entry(window)
	var_2.pack()
	tkinter.Label(window, text="Fecha y hora [dd-mm-yyyy hh:mm] [0 para ahora]").pack()
	var_3 = tkinter.Entry(window)
	var_3.pack()


	def welcomeMessage():
		global var1, var2, var3
		var1 = var_1.get()
		var2 = var_2.get()
		var3 = var_3.get()
		print(var1)
		print(var2)
		print(var3)
		if (var3 == "0"):
			var3 = date_t.now()
		else:
			var3 = date_t.strptime(var3, "%d-%m-%Y %H:%M")

		return var1, var2, var3


	tkinter.Button(window, text="Click Here", command=welcomeMessage).pack()	

	window.mainloop()

	print("Sector mapa")
	# Define observer coordinates (Wachusett Mtn.)
	#loc_lat = -42.503
	#loc_long = -71.886
	#print "Latitud"

	loc_lat = float(var1)
	#print "Longitud"
	loc_long = float(var2)
	#fecha_str = input("Fecha y hora [dd-mm-yyyy hh:mm]: ")
	fecha = var3




	observer = ephem.Observer()
	observer.lat = np.deg2rad(loc_lat)
	observer.long = np.deg2rad(loc_long)
	observer.elevation = 611 # in meters
	#observer.date = date_t.now()
	observer.date = fecha

	url = 'http://celestrak.com/NORAD/elements/globalstar.txt'
	r = requests.get(url, allow_redirects=True)
	open('globalstar.txt', 'wb').write(r.content)

	''' TODO: Check HTTP headers to pull a more up updated version 
	file = urlopen('http://celestrak.com/NORAD/elements/globalstar.txt', timeout = 30)
	print("Online file last modified:", file.headers['last-modified'])

	localfile = 'globalstar.txt'
	statbuf = os.stat(localfile)
	print("Local file last modified: {}".format(statbuf.st_mtime))
	'''

	# Load TLE data
	globalstar = loadTLE("globalstar.txt")

	# Define time interval (now until next 10 minutes)
	#dt = [date_t.now() + datetime.timedelta(minutes = x) for x in range(0, 20)]
	dt = [fecha + datetime.timedelta(minutes = x) for x in range(0, 20)]
	sat_alt, sat_az = [], []
	sat_lat, sat_long = [], []

	for i in range(len(globalstar)):
		sat_alt.append([])
		sat_az.append([])
		sat_lat.append([])
		sat_long.append([])

		for date in dt:
			satellite = globalstar[i]
			satellite.compute(date)
			sat_lat[i].append(satellite.sublat / degree)
			sat_long[i].append(satellite.sublong / degree)

			observer.date = date
			satellite.compute(observer)
			sat_alt[i].append(np.rad2deg(satellite.alt))
			sat_az[i].append(np.rad2deg(satellite.az))

	
	#ax = plt.subplot(121, projection = ccrs.PlateCarree())
	fig = plt.figure(figsize=(20,5))
	fig.suptitle("TSMP - Globalstar SAT position : {}".format(fecha), size=10)
	ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
	#ax = plt.axes(projection=ccrs.PlateCarree())
	
	ax.add_feature(cartopy.feature.OCEAN)
	ax.add_feature(cartopy.feature.LAND)
	ax.add_feature(cartopy.feature.COASTLINE)
	ax.add_feature(cartopy.feature.LAKES)
	ax.add_feature(cartopy.feature.RIVERS)
	ax.add_feature(cartopy.feature.BORDERS, linestyle = '-')
	ax.gridlines()

	mlats = loc_lat + 5
	mlati = loc_lat - 5
	mlongs = loc_long + 10
	mlongi = loc_long - 10

	#AMERICA ax.set_extent([  -169.99, -26.26,-53.06, 66.53 ], crs = ccrs.PlateCarree())
	ax.set_extent([mlongi, mlongs, mlati, mlats], crs = ccrs.PlateCarree())

	# Plot our reference location
	plt.plot(loc_long, loc_lat,
		color = 'red',
		marker = '*',
		transform = ccrs.Geodetic()
	)

	# Plot satellites on map
	for i in range(len(globalstar)):
		plt.scatter(sat_long[i][0],	sat_lat[i][0],
			linewidth = 4,
			transform = ccrs.Geodetic()
		)
		plt.scatter(sat_long[i][0],	sat_lat[i][0],
			linewidth = 60,
			transform = ccrs.Geodetic(),
			alpha = .5
		)

		ax.annotate(globalstar[i].name[11:15], (sat_long[i][0] -3 ,sat_lat[i][0] - 3))

		plt.plot(sat_long[i], sat_lat[i],
			linewidth = 2,
			transform = ccrs.Geodetic()
		)
		plt.plot(sat_long[i], sat_lat[i],
			linewidth = 60,
			transform = ccrs.Geodetic(),
			alpha = .5
		)
		plt.plot(sat_long[i][-1], sat_lat[i][-1],
			linewidth = 2,
			color = 'black',
			marker = 'x',
			transform = ccrs.Geodetic()
		)

	# Plot satellites on polar az/el graph
#	ax = plt.subplot(122, polar=True)
#	for i in range(len(globalstar)):
#		ax.scatter(np.deg2rad(sat_az[i][0]), 
#				   90 - np.array(sat_alt[i][0]),
#				   linewidth = '3')
#		ax.annotate(globalstar[i].name[11:15], (np.deg2rad(sat_az[i][0]),90 - np.array(sat_alt[i][0])))
#		ax.plot(np.deg2rad(sat_az[i]), 90 - np.array(sat_alt[i]))
#		ax.plot(np.deg2rad(sat_az[i][-1]), 
#				90 - np.array(sat_alt[i][-1]),
#				linewidth = '2',
#				color = 'black',
#				marker = 'x'
#				)

#	ax.set_ylim(0,90)
#	ax.set_theta_direction(-1)
#	ax.set_theta_offset(np.pi / 2)
	#ax.yaxis.set_ticklabels([])
#	ax.grid(True)

	plt.show()

if __name__ == '__main__':
	main()