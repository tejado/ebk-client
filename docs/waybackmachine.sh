#!/usr/bin/env bash
# Wayback machine downloader
#TODO: Remove redundancy (download only newest files in given time period - not all of them and then write over them)
# Source: https://gist.github.com/lazanet/872f88c9874e4a7a78fd
############################
clear

#Enter domain without http:// and www.
domain="api.ebay-kleinanzeigen.de"
#Set matchType to "prefix" if you have multiple subdomains, or "exact" if you want only one page 
matchType="domain"

#Set datefilter to 1 if you want to download data from specific time period
datefilter=0
from="20100101120001" #yyyyMMddhhmmss
to="20300101120001" #yyyyMMddhhmmss

#Set this to 1 if your page has lots of captured pages with ? in url (experimental)
swapurlarguments=0
usersign='&' #sign to replace ? with

##############################################################
# Do not edit after this point
##############################################################
#Getting snapshot list
full="http://web.archive.org/cdx/search/cdx?url="
full+="$domain"
full+="&matchType=$matchType"
	if [ $datefilter = 1 ]
		then
			full+="&from=$from&to=$to"
		fi
full+="&output=json&fl=timestamp,original&fastLatest=true&filter=statuscode:200&collapse=original"  #Form request url

curl -o rawlist.json $full #Get snapshot list to file rawlist.json


#Do parsing and downloading stuff
sed 's/\"//g' rawlist.json  > list.json #Remove " from file for easier processing
rm rawlist.json #Remove unnecessary file
i=0; #Set file counter to 0
numoflines=$(cat list.json | wc -l ) #Fill numoflines with number of files to download
while read line;do # For every file
        rawcurrent="${line:1:${#line}-3}" #Remove brackets from JSON line
	IFS=', ' read -a current <<< "$rawcurrent" #Separate timestamp and url
	timestamp="${current[0]}"
	originalurl="${current[1]}"
	waybackurl="http://web.archive.org/web/$timestamp" 
	waybackurl+="id_/$originalurl" #Form request url
	file_path="$domain/"
	sufix="$(echo $originalurl | grep / | cut -d/ -f2- | cut -d/ -f3-)"
	 [[ $sufix = "" ]] && file_path+="index.html" || file_path+="$sufix" #Determine local filename
clear
echo " $i out of $numoflines" #Show progress
echo "$file_path"
mkdir -p -- "${file_path%/*}" && touch -- "$file_path" #Make local file for data to be written
	curl -o $file_path $waybackurl #Download actual file
	((i++))
done < list.json

#If user chose, replace ? with usersign
	if [ $swapurlarguments = 1 ]
		then
			cd $domain
			for i in *; do mv "$i" "`echo $i | sed "s/\?/\$usersign/g"`"; done #Replace ? in filenames with usersign
			find ./ -type f -exec sed -i "s/\?/\$usersign/g" {} \; #Replace ? in files with usersign
		fi