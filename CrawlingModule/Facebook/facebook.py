import requests  # pip install requests
import json
import xlrd  # pip install xlrd
from config import *
from CrawlingModule.Facebook.authorization import authorize
from DatabaseModule.FacebookWrapper.database_manipulation_facebook import save_to_mongo_facebook

def get_page_posts(ACCESS_TOKEN, page_id=None,limit = 100):

    if page_id:
        base_url = 'https://graph.facebook.com/'+page_id+"/posts"
        fields = ''
        #url = '%s?fields=%s&access_token=%s' % (base_url.strip(), fields, ACCESS_TOKEN)
        url = '%s?access_token=%s' % (base_url.strip(), ACCESS_TOKEN)
        print url
        result = []
        content = requests.get(url).json()
        num_results=len(content["data"])
        if num_results >= limit :
            return content["data"]

        result = content["data"]
        i=0
        #call for the rest of the posts
        while True:

            try:
                next = content["paging"]["next"]
                print("next: ",next)
                content = requests.get(next).json()
                result += content["data"]

            except Exception, e: # no next result
                print e.message
                break
            if len(result)>= limit:
                    break
        return result #json.dumps(content, indent=1)

def get_page_data(ACCESS_TOKEN, name):
    base_url = 'https://graph.facebook.com/'+name
    #fields = 'id,name,likes,talking_about_count'
    fields = ''
    url = '%s?include_hidden=true&fields=%s&access_token=%s' % (base_url.strip(), fields, ACCESS_TOKEN)
    #print url
    # Interpret the response as JSON and convert back
    # to Python data structures
    content = None
    try:
        content = requests.get(url).json()
        if content["name"]:
            pass
    #if the content is not a page
    except KeyError, e:
        pass
    else:
        return content



def sort_pages(pages, order="DESC"):
    """ Sorts the list of pages first by number of likes then by number of people talking about it
    :parameter pages - list of pages to sort
    :parameter order - order in which the list should be sorted. values: ASC and DESC
    :returns pages - sorted ist of pages
    """
    #debug_print("EXEC sort_pages method :")
    #print pages
    #sort statuses by likes, then by num of people talking about it
    if order == "DESC":
        for i in range(0, len(pages)):
            for j in range(i, len(pages)):
                if int(pages[i]['likes']) < int(pages[j]['likes']):
                    pages[i], pages[j] = pages[j], pages[i]
                elif int(pages[i]['likes']) == int(pages[j]['likes']):
                    if int(pages[i]['talking_about_count']) < int(pages[j]['talking_about_count']):
                        pages[i], pages[j] = pages[j], pages[i]
    elif order == "ASC":
         for i in range(0, len(pages)):
            for j in range(i, len(pages)):
                if int(pages[i]['likes']) > int(pages[j]['likes']):
                    pages[i], pages[j] = pages[j], pages[i]
                elif int(pages[i]['likes']) == int(pages[j]['likes']):
                    if int(pages[i]['talking_about_count']) > int(pages[j]['talking_about_count']):
                        pages[i], pages[j] = pages[j], pages[i]
    return pages


access_token = authorize()
# workbook = xlrd.open_workbook(filename=facebook_PAGES)
# sheet = workbook.sheet_by_index(0)
pages = []
# debug_print("Reading pages' names from file. Might take few minutes...")
# for cell in sheet.col_values(colx=3):
#     parts = cell.split("?")
#     #base url with the id or name
#     base = parts[0]
#     #get just the name or id
#     url_parts = base.split("/")
#     page_part = url_parts[len(url_parts)-2]
#     last = url_parts[len(url_parts)-1]
#     #print last
last = "AlvaCommunityCouncil"
if last: # move this later inside the for
    page = get_page_data(access_token, last+"")
    if page is not None:
        pages.append(dict(page)) #save json data about each page


pages = sort_pages(pages)
#print '{0:10}     {1:10}     {2:20} '.format("Likes", "Talking about", "Page")
for i in range(0, len(pages)):
    #print '{0:10}     {1:10}     {2:20} '.format(pages[i]['likes'], pages[i]['talking_about_count'], pages[i]['name'])
    #print json.dumps(pages[3], indent=1)
    #print pages[i]["id"]
    results = get_page_posts(access_token, pages[i]["id"]) #send id of page and access token to get posts
    print pages[i]['name'], len(results)

    print json.dumps(results, indent=1)
    save_to_mongo_facebook(mongo_db="facebook",mongo_db_coll=pages[i]['name'],data=results)
    #for res in results:
        #print res
        #print json.dumps(res, indent=1)

