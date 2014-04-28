#line 2 MUST stay in order to be able to read utf-8 webpages
#coding: utf-8
from bs4 import BeautifulSoup #HTML parsing
import re #regex
import urllib, urllib2, cookielib
import sys
try :
    import json # Python >=2.6.x
except ImportError :
    import simplejson as json # Python < 2.6
import MySQLdb
import datetime
import threading

nutTypes = ["Calories", "Total Fat", "Saturated Fat", "Polyunsaturated Fat", "Monounsaturated Fat", "Cholesterol", "Sodium", "Total Carbohydrate", "Dietary Fiber", "Vitamin A", "Vitamin C", "Calcium", "Iron", "Protein", "Sugars"]

facilities = [{"name":"Busey Evans", "id":1, "parts":[2]}, {"name":"Florida Avenue", "id":5, "parts":[6]}, {"name":"Ikenberry", "id":10, "parts":[12, 13, 14, 15, 16, 17, 18, 19]}, {"name":"Illinois Street", "id":23, "parts":[24]}, {"name":"Lincoln Avenue", "id":28, "parts":[29]}, {"name":"PAR", "id":33, "parts":[34, 35, 36, 37, 38]}]

mealTypes = ["Breakfast", "Lunch", "Dinner"]

class FoodInfoGrabber:
    facilityUrl = "http://eatsmart.housing.illinois.edu/NetNutrition/Unit.aspx/SelectUnitFromUnitsList"
    partUrl = "http://eatsmart.housing.illinois.edu/NetNutrition/Unit.aspx/SelectUnitFromChildUnitsList"
    menuUrl = "http://eatsmart.housing.illinois.edu/NetNutrition/Menu.aspx/SelectMenu" 
    nutUrl = "http://eatsmart.housing.illinois.edu/NetNutrition/Home.aspx/NutritionDetail.aspx/ShowItemNutritionLabel"

    def __init__(self):
        #Create CookieJar to hold session cookies
        self.cj = cookielib.CookieJar()
        #Build opener with CookieJar
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        #Get initial ASP session cookies. Cookies will be store in cj
        r = self.opener.open("http://eatsmart.housing.illinois.edu/NetNutrition/46")

    def makeRequest(self, values, url):
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"})
        r = self.opener.open(req)
        return json.loads(r.read())

    def getFacilityParts(self, facilityCode):
        values = {'unitOid': facilityCode}
        parts = self.makeRequest(values, self.facilityUrl)
        for panel in parts['panels'] :
            if panel['id'] == "childUnitsPanel" :
                html = panel['html']
                break
        parsed_html = BeautifulSoup(html)
        print(parsed_html.prettify())

    def getMenus(self, facilityCode, partCode): 
        values = {'unitOid': facilityCode}
        self.makeRequest(values, self.facilityUrl)
        values = {'unitOid': partCode}
        menus = self.makeRequest(values, self.partUrl)
        for panel in menus['panels'] :
            if panel['id'] == "menuPanel" :
                html = panel['html']
                break
        parsed_html = BeautifulSoup(html)
        menuIdList = []
        for menu in parsed_html.find_all("a"):
            if menu.string in mealTypes :
                onClick = menu.get("onclick")
                onClick = onClick.replace("javascript:menuListSelectMenu(", "");
                onClick = onClick.replace(");", "");
                menuIdList.append(int(onClick))
        return menuIdList

    def getMenu(self, facilityCode, menuCode):
        # (for some reason) this call needs to be made first
        values = {'unitOid': facilityCode} # this code doesn't matter
        self.makeRequest(values, self.partUrl)
        
        #Now menu can be fetched
        values = {'menuOid' : menuCode}
        #Response is in JSON
        foods = self.makeRequest(values, self.menuUrl)

        html = foods['panels'][0]['html']
        
        parsed_html = BeautifulSoup(html)
        header = parsed_html.find_all(self.__header)[0].text.encode('utf8')
        parsed_header = self.__parse_header(header)
        (facility_name, date_string, meal) = parsed_header
        food_items = parsed_html.find_all(self.__food_item_row)
        menu = {'date_string': date_string,
                'facility_id': facilityCode,
                'facility': facility_name,
                'meal': meal,
                'id': menuCode,
                'food': {}}

        for item in food_items:
            food_name = item.find_all('td')[1].text.encode('utf-8').replace('"', '')
            food_id = int(str(item.find_all('td')[1]['onmouseover'])[47:55])
            food_category = self.__get_item_category(item)
            menu['food'][food_id] = {'name': food_name, 'category': food_category}
        return menu

    def __food_item_row(self, tag):
        return tag.name == 'tr' and tag.has_attr('class') and 'cbo_nn_item' in str(tag['class'])
    def __food_category_row(self, tag):
        return tag.name == 'td' and tag.has_attr('class') and 'cbo_nn_itemGroupRow' in str(tag['class'])
    def __get_item_category(self, item):
        tag = item.previous_sibling
        while (not self.__food_category_row(tag.td)):
            tag = tag.previous_sibling
        return str(tag.td.text.strip())
    def __header(self, tag):
        return tag.name == 'div' and tag.has_attr('class') and 'cbo_nn_itemHeaderDiv' in str(tag['class'])
    def __parse_header(self, header): 
        regex = re.compile(r'Menu\sFor  -  ([a-zA-Z\s]*) -  ([a-zA-Z0-9\s\,]*) -  ([a-zA-Z\s]*)', re.UNICODE)
        matches = regex.match(header)
        return matches.groups()

    def getNutritionalInformation(self, facilityCode, menuCode, foodCode):
        self.getMenu(facilityCode, menuCode)
        values = {'detailOid': foodCode}
        data = urllib.urlencode(values)
        headers = {"Host":"eatsmart.housing.illinois.edu", "Origin":"http://eatsmart.housing.illinois.edu","Referer":"http://eatsmart.housing.illinois.edu/NetNutrition/46"}
        req = urllib2.Request(self.nutUrl, data, headers)
        r = self.opener.open(req)

        html = r.read()
        parsed_html = BeautifulSoup(html)
        vitamins = parsed_html.find_all(self.__vitamin)
        nutrients = parsed_html.find_all(self.__nutrient)
        nutrient_info = {}
        for nutrient in nutrients:
            info = nutrient.contents
            key = info[0].text.encode('utf8').replace(':', '')
            value = info[len(info)-1].text.encode('utf8').strip().replace('\xc2\xa0', '')
            nutrient_info[key] = value
        for vitamin in vitamins:
            info = vitamin.text.encode('utf8').split(':\xc2\xa0')
            key = info[0].replace(':', '')
            value = None
            if (len(info) >= 2):
                value = info[1]
            else:
                value = '0%'
            nutrient_info[key] = value
        return nutrient_info

    def __nutrient(self, tag):
        return tag.name == 'td' and tag.has_attr('class') and 'cbo_nn_LabelDetail' in str(tag['class'])

    def __vitamin(self, tag):
        return tag.name == 'td' and tag.has_attr('class') and 'cbo_nn_SecondaryNutrientLabel' in str(tag['class'])
   
def commitMenuAndFoods(menu, semaphore):
    semaphore.acquire()
    print "Thread Committing", menu['date_string'], menu['meal'], "at", menu['facility']

    db = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", user="cs411backend_jsu", passwd="cs411pass", db="cs411backend_food")
    fig = FoodInfoGrabber()
    for foodID, foodInfo in menu['food'].items():
        menu['food'][foodID]['nutrition'] = fig.getNutritionalInformation(menu['facility_id'], menu['id'], foodID)
    
    cur = db.cursor()
    
    foods = menu["food"]
    facility = menu["facility"]
    menuId = menu["id"]
    dateStr = menu['date_string'] 
    date = datetime.datetime.strptime(dateStr, "%A, %B %d, %Y").date()
    mealStr = menu['meal']
    cur.execute("INSERT IGNORE INTO menus(menus_id, date, facility_id, meal_type) SELECT \"" + str(menuId) + "\", \"" + date.isoformat() + "\", facility_id, \"" + mealStr + "\" FROM facilities WHERE name = \"" + str(facility) + "\"")
    
    for foodId in foods.keys():
        foodObj = foods[foodId]
        category = foodObj['category']
        cur.execute("INSERT IGNORE INTO categories(category_name) VALUES (\"" + category + "\")") 
        cur.execute("INSERT IGNORE INTO food_items(food_name, category_name) VALUES (%s, %s)", (foodObj['name'], foodObj['category']))
        cur.execute("INSERT IGNORE INTO menus_have_food_items(menus_id, food_name) VALUES (" + str(menuId) + ", \"" + foodObj['name'] + "\")");
        foodNut = foodObj["nutrition"]
        nutList = []
        nutList.append(foodObj['name'])
        for item in nutTypes :
             try :
                nutList.append(foodNut[item])
             except KeyError :
                nutList.append("NULL")
        nutTup = tuple(nutList);

        cur.execute("INSERT IGNORE INTO nutritional_information(food_name, calories, total_fat, saturated_fat, polyunsaturated_fat, monounsaturated_fat, cholesterol, sodium, total_carbohydrate, dietary_fiber, vitamin_a, vitamin_c, calcium, iron, protein, sugar) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", nutTup)

    db.commit()
    semaphore.release()

if __name__ == "__main__":
    db = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", user="cs411backend_jsu", passwd="cs411pass", db="cs411backend_food")
    
    fig = FoodInfoGrabber()
    threads = []
    semaphore = threading.Semaphore(15)
    for facility in facilities :
        menuIds = []
        for part in facility['parts']:
            menuIds = menuIds + fig.getMenus(facility['id'], part)
        menus = []
        for menuId in menuIds :
            menu = fig.getMenu(facility['id'], menuId)
            found = False
            for prevMenu in menus :
                if prevMenu["date_string"] == menu["date_string"] and prevMenu["meal"] == menu["meal"] :
                    prevMenu['food'] = dict(prevMenu['food'].items() + menu['food'].items())
                    found = True
                    break
            if not found :
                menus.append(menu)
        for item in menus :
            t = threading.Thread(target=commitMenuAndFoods, args = (item, semaphore))
            t.daemon = True
            threads.append(t)
            t.start()

    for thread in threads:
        t.join()
