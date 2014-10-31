#!/usr/bin/env python

# A Python script to convert .pwx files from the Timex Global Trainer watch to .gpx format to import into Garmin Connect, Strava, etc
# V20141029 by blackshoals

import os
import time
from xml.dom import minidom
from xml.dom.minidom import parse
from datetime import datetime
from datetime import timedelta

############ User Configuration ################################################################################
rootdir = "/home/Timex/" #choose the folder where the .pwx files to be converted are located
fileclean="N" #enter "Y" or "N" to delete the files after converting                           
################################################################################################################

tz=time.altzone/(60*60)		#calculate the current timezone with Daylight Savings

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
		if file[-3:]=="pwx": #check if the file is a .pwx format
			sourcefile= os.path.join(subdir, file)
			targetfilename=os.path.join(subdir,file[:-4]+".gpx")

			frpwx = parse(sourcefile)
			togpx = minidom.Document()

			time = frpwx.getElementsByTagName("time")[0] #break the time into components so that the .pwx time offsets can be added to it
			stime=(time.firstChild.data)

			yyyy=int(stime[:4])
			mo=int(stime[5:7])
			dd=int(stime[8:10])
			hh=int(stime[11:13])
			mm=int(stime[14:16])
			ss=int(stime[17:19])
			
			sportType= frpwx.getElementsByTagName("sportType")[0] #use the Timex sportType for the Trk name in the .gpx file
			sportname=(sportType.firstChild.data)			
						
			out_gpx=open(targetfilename,"wt") #open a new file and write the elements from .pwx format to .gpx
			 
			out_gpx.write( """<?xml version="1.0" encoding="UTF-8"?>
			<gpx version="1.1" creator="PWX to GPX converter"
			  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"
			  xmlns="http://www.topografix.com/GPX/1/1"
			  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
			  xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			   <metadata>
					<link href="connect.garmin.com">
					<text>Garmin Connect</text>
					</link>
				</metadata>
			<trk>\n""")

			out_gpx.write("\t<name>"+sportname+"</name>\n")
			out_gpx.write("\t<trkseg>\n")

			for i in frpwx.getElementsByTagName('sample'):
				
				# gather the elements from the .pwx file
				toff = i.getElementsByTagName("timeoffset")[0] 
				try:
					hr = i.getElementsByTagName("hr")[0]
				except:
					hr=""
				try:
					lat = i.getElementsByTagName("lat")[0]
				except:
					lat=""
				try:
					lon = i.getElementsByTagName("lon")[0]
				except:
					lon=""
				try:
					alt = i.getElementsByTagName("alt")[0]
				except:
					alt=""
				
				#calculate the time by adding the .pwx time offsets to the start time

				timestamp = datetime(yyyy,mo,dd,hh,mm,ss)+ timedelta(hours=tz,seconds=int(float(toff.firstChild.data)))
				gpxtime=timestamp.strftime("%Y-%m-%d")+"T"+timestamp.strftime("%H:%M:%S")+".000Z"
			
				#write the trackpoint section of the .gpx file	
				try:
					out_gpx.write("\t\t<trkpt lon='"+lon.firstChild.data+"'  lat='"+lat.firstChild.data+"'>\n")
				except:
					out_gpx.write('\t\t<trkpt lon="" lat="">\n')
					
				try:	
					out_gpx.write("\t\t\t<ele>"+alt.firstChild.data+"</ele>\n")
				except:
					pass
					
				out_gpx.write("\t\t\t<time>"+gpxtime+"</time>\n")
				
				try:
					hrate=hr.firstChild.data
					out_gpx.write("\t\t\t<extensions>\n")
					out_gpx.write("\t\t\t\t<gpxtpx:TrackPointExtension>\n")
					out_gpx.write("\t\t\t\t\t<gpxtpx:hr>"+hrate+"</gpxtpx:hr>\n")
					out_gpx.write("\t\t\t\t</gpxtpx:TrackPointExtension>\n")
					out_gpx.write("\t\t\t</extensions>\n")
				except:
					pass

				out_gpx.write("\t\t</trkpt>\n")
				
			out_gpx.write("</trkseg>\n</trk>\n</gpx>")
			out_gpx.close()

			# if "Y", delete the original .pwx file
			if fileclean=="Y":
				os.remove(sourcefile)
