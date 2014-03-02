from bs4 import BeautifulSoup #HTML parsing
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

		parsed_html = BeautifulSoup(html)
		food_items = parsed_html.find_all(self.__food_item_row)
		food_dict = {}
		for item in food_items:
			food_name = str(item.find_all('td')[1].text)
			food_id = int(str(item.find_all('td')[1]['onmouseover'])[47:55])
			food_category = self.__get_item_category(item)
			food_dict[food_id] = {'name': food_name, 'menuID': menuCode, 'category': food_category}
		return food_dict

	def __food_item_row(self, tag):
		return tag.name == 'tr' and tag.has_attr('class') and 'cbo_nn_item' in str(tag['class'])
	def __food_category_row(self, tag):
		return tag.name == 'td' and tag.has_attr('class') and 'cbo_nn_itemGroupRow' in str(tag['class'])
	def __get_item_category(self, item):
		tag = item.previous_sibling
		while (not self.__food_category_row(tag.td)):
			tag = tag.previous_sibling
		return str(tag.td.text.strip())

	def getNutritionalInformation(self, menuCode, foodCode):
		self.getMenu(menuCode)

		values = {'detailOid': foodCode}
		url = "http://eatsmart.housing.illinois.edu/NetNutrition/Home.aspx/NutritionDetail.aspx/ShowItemNutritionLabel"
		data = urllib.urlencode(values)
		headers = {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"}
		req = urllib2.Request(url, data, headers)
		r = self.opener.open(req)

		html = r.read()
		parsed_html = BeautifulSoup(html)
		return parsed_html

if __name__ == "__main__":
	menuCode = 513635 #dinner at FAR on March 9th
	foodCode = 43305418 # Tiramisu

	fig = FoodInfoGrabber()
	#print fig.getMenu(menuCode)
	print fig.getNutritionalInformation(menuCode,foodCode)