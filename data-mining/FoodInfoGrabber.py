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

nutTypes = ["Calories", "Total Fat", "Saturated Fat", "Polyunsaturated Fat", "Monounsaturated Fat", "Cholesterol", "Sodium", "Total Carbohydrate", "Dietary Fiber", "Vitamin A", "Vitamin C", "Calcium", "Iron", "Protein", "Sugars"]

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
        values = {'unitOid': 1} # this code doesn't matter
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
        header = parsed_html.find_all(self.__header)[0].text.encode('utf8')
        parsed_header = self.__parse_header(header)
        (facility_name, date_string, meal, menu_name) = parsed_header
        food_items = parsed_html.find_all(self.__food_item_row)
        menu = {'date_string': date_string,
                'facility': facility_name,
                'meal': meal,
                'menu_name': menu_name,
                'id': menuCode,
                'food': {}}

        for item in food_items:
            food_name = str(item.find_all('td')[1].text)
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
        regex = re.compile(r'Menu\sFor  -  ([a-zA-Z\s]*) -  ([a-zA-Z0-9\s\,]*) -  ([a-zA-Z\s]*) -  ([a-zA-Z\s]*)', re.UNICODE)
        matches = regex.match(header)
        return matches.groups()

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

if __name__ == "__main__":
    #menuCode = 513665 #dinner at FAR on March 9th
    #menuCode = 514650 #dinner at Busey on March 21st
    #foodCode = 43305418 # Tiramisu
    
    menuCode = int(sys.argv[1])

    fig = FoodInfoGrabber()
    menu = fig.getMenu(menuCode)
    for foodID, foodInfo in menu['food'].items():
        menu['food'][foodID]['nutrition'] = fig.getNutritionalInformation(menuCode,foodID)
            
    db = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", user="**********", passwd="********", db="cs411backend_food")
    
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

    db.commit();
    print menu
    print menu['meal'], "|", menu['menu_name'], "|", menu['date_string']
