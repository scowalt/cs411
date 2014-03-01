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

	def getMenu(self, facilityCode, menuCode):
		facilityCode = 2 #Busey-Evans
		menuCode = 504603 #dinner at Busey-Evans dinner on February 20th

		# (for some reason) this call needs to be made first
		values = {'unitOid': facilityCode}
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

		return foods

	def getNutritionalInformation(self, foodCode):
		foodCode = 42672740 # Roasted Turkey Breast

		values = {'detailOid': foodCode}
		data = urllib.urlencode(values)
		req = urllib2.Request("http://eatsmart.housing.illinois.edu/NetNutrition/Home.aspx/NutritionDetail.aspx/ShowItemNutritionLabel", data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
		r = self.opener.open(req)

		return r.read()

if __name__ == "__main__":
	fig = FoodInfoGrabber();
	print fig.getNutritionalInformation(2)