from HTMLParser import HTMLParser
import urllib, urllib2, cookielib
try :
    import json # Python >=2.6.x
except ImportError :
    import simplejson as json # Python < 2.6

class FoodInfoGrabber:
	def __init__(self):
		#Create CookieJar to hold session cookies
		self.cj = cookielib.CookieJar()
		#Build opener with CookieJar
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		#Get initial ASP session cookies. Cookies will be store in cj
		r = self.opener.open("http://eatsmart.housing.illinois.edu/NetNutrition/46")

	def getMenu(self, menuCode):
		menuCode = 513635 #dinner at FAR on March 9th

		# (for some reason) this call needs to be made first
		values = {'unitOid': 2} # this code doesn't matter
		data = urllib.urlencode(values)
		req = urllib2.Request("http://eatsmart.housing.illinois.edu/NetNutrition/Unit.aspx/SelectUnitFromChildUnitsList", data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
		r = self.opener.open(req)

		#Now menu can be fetched
		values = {'menuOid' : menuCode}
		data = urllib.urlencode(values)
		req = urllib2.Request("http://eatsmart.housing.illinois.edu/NetNutrition/Menu.aspx/SelectMenu", data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
		r = self.opener.open(req)
		#Response is in JSON
		foods = json.loads(r.read())

		html = foods['panels'][0]['html']

		parser = MenuHTMLParser()
		parser.feed(html)

	def getNutritionalInformation(self, foodCode):
		foodCode = 43162606 # Fruit Tray

		values = {'detailOid': foodCode}
		url = "http://eatsmart.housing.illinois.edu/NetNutrition/Home.aspx/NutritionDetail.aspx/ShowItemNutritionLabel"
		data = urllib.urlencode(values)
		headers = {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"}
		req = urllib2.Request(url, data, headers)
		r = self.opener.open(req)

		return r.read()

class MenuHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		print "Encountered a start tag:", tag
	def handle_endtag(self, tag):
		print "Encountered an end tag :", tag
	def handle_data(self, data):
		print "Encountered some data  :", data

if __name__ == "__main__":
	fig = FoodInfoGrabber();
	print fig.getMenu(504603)