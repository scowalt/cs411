import urllib, urllib2, cookielib
try :
    import json
except ImportError :
    import simplejson as json

#Create CookieJar to hold session cookies
cj = cookielib.CookieJar()
#Build opener with CookieJar
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#Get initial ASP session cookies. Cookies will be store in cj
r = opener.open("http://eatsmart.housing.illinois.edu/NetNutrition/46")

#Uncomment if you want to see the cookies
"""
for cookie in cj :
    print cookie
"""

#For some reason, this call needs to be done first before getting the actual menu. May be something they're doing in the ASP on their server.
#unitOid corresponds to a facility; 2 is Busey-Evans
values = {'unitOid': 2}
data = urllib.urlencode(values)
req = urllib2.Request("http://eatsmart.housing.illinois.edu/NetNutrition/Unit.aspx/SelectUnitFromChildUnitsList", data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
r = opener.open(req)

#Now menu can be fetched
#menuOid corresponds to a day and a meal; 504603 is dinner at Busey-Evans dinner on February 20th. I haven't taken the time to figure out the scheme.
values = {'menuOid' : 504603}
data = urllib.urlencode(values)
req = urllib2.Request("http://eatsmart.housing.illinois.edu/NetNutrition/Menu.aspx/SelectMenu", data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
r = opener.open(req)
#Response is in JSON
foods = json.loads(r.read())
#JSON is structured with a list of the panels on the webpage, each in HTML
#We're going to have to parse this into something usable.
print foods["panels"][0]["html"]

#Fetching nutritional information
#detailOid corresponds to a food item/dish; 42672740 is Roasted Turkey Breast
values = {'detailOid': 42672740}
data = urllib.urlencode(values)
req = urllib2.Request("http://eatsmart.housing.illinois.edu/NetNutrition/Home.aspx/NutritionDetail.aspx/ShowItemNutritionLabel", data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
r = opener.open(req)
#This time the response is just the HTML of the nutrition box
#Again, parsing will have to be done
print r.read()
