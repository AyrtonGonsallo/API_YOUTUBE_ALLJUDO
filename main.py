import isodate
import requests
import json
import pprint
from pymongo import MongoClient
from bson.json_util import dumps, loads

# ----------- google
google_images_url = "https://google-search3.p.rapidapi.com/api/v1/image/q=tesla"

headers = {
    "X-User-Agent": "desktop",
    "X-Proxy-Location": "EU",
    "X-RapidAPI-Key": "18cbd7bc5bmsh652e91d57f01727p1ec081jsn3258f190cd8e",
    "X-RapidAPI-Host": "google-search3.p.rapidapi.com"
}


# ---------- you tube


def init_mongo():
    client = MongoClient(
        "mongodb+srv://ayrtongonsallo:madagascar@cluster0.am70a4l.mongodb.net/?retryWrites=true&w=majority")
    db = client.AllJudoPythonVideos
    return db


def getAPIKey():
    db = init_mongo()
    keys = db.Keys.find()
    listKeys = list(keys)
    apiKey = listKeys[0]["youtube4"]
    print("MongoDB: clé 1 recupérée", apiKey)
    return apiKey


apiKey = getAPIKey()
racine_recherche_generale = "https://www.googleapis.com/youtube/v3/search"
recherche_video_part = "snippet"
recherche_video_part2 = "contentDetails"
racine_recherche_chaines = "https://www.googleapis.com/youtube/v3/channels"
racine_recherche_video = "https://www.googleapis.com/youtube/v3/videos"
urls = "https://www.youtube.com/watch?v="
keyword = "best fight scenes in tv shows"
# date rating relevance  title  videoCount  viewCount
sortby = "relevance"
# any long short medium
duration = "medium"
# any episode movies
type = "any"
# pip freeze > requirements.txt
'''response = requests.get(
    racine_recherche_generale + "?" + "key=" + apiKey + "&type=video&videoDuration=" + duration + "&videoType=" + type + "&q=" + keyword + "&order=" + sortby)
'''
# recuperer la reponse totale
# print("toute la reponse", response.json())
# recuperer les items
# print("items: ", response.json()["items"])
# iteration
'''for video in response.json()["items"]:
    print(video["id"], " url:", urls + video["id"]["videoId"])'''


def getImages(keyword, total):
    results = {}
    url = "https://google-search3.p.rapidapi.com/api/v1/image/q=" + keyword + "&num=" + total + "&lr=lang_fr"
    response = requests.request("GET", url, headers=headers)
    i = 0
    for data in response.json()["image_results"]:
        # video = Video(data["id"], urls + data["id"]["videoId"])
        # results[i] = video
        i += 1
        results[i] = {'id': i, 'src': data["image"]["src"], 'titre': data["link"]["title"]}

    return json.dumps(list(results.items()))


def getGoogleSearchResultsByKeyword(keyword, total):
    url = "https://google-search3.p.rapidapi.com/api/v1/search/q=" + keyword + "&num=" + total + "&lr=lang_fr"
    results = {}
    headers = {
        "X-User-Agent": "desktop",
        "X-Proxy-Location": "EU",
        "X-RapidAPI-Key": "18cbd7bc5bmsh652e91d57f01727p1ec081jsn3258f190cd8e",
        "X-RapidAPI-Host": "google-search3.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    i = 0
    for data in response.json()["results"]:
        i += 1
        results[i] = {'id': i, 'src': data["link"], 'description': data["description"], 'titre': data["title"]}

    return json.dumps(list(results.items()))


def getVideoDetails(videoData):
    try:
        response = requests.get(
            racine_recherche_video + "?part=" + recherche_video_part + "&id=" + videoData["id"][
                "videoId"] + "&key=" + apiKey
        )
        return response.json()["items"][0]["snippet"]
    except Exception as err:
        print("erreur recuperation details video",err)


def getVideoDuration(videoData):
    try:
        response = requests.get(
            racine_recherche_video + "?part=" + recherche_video_part2 + "&id=" + videoData["id"][
                "videoId"] + "&key=" + apiKey
        )
        duration = response.json()["items"][0]["contentDetails"]["duration"]
        dur = isodate.parse_duration(duration)
        # print(dur)
        return dur
    except Exception as err:
        print("Erreur recuperation duree video",err)


def getChannels(keyword, total):
    results = {}
    i = 0
    response = requests.get(
        racine_recherche_generale + "?" + "key=" + apiKey + "&type=channel&part=" + recherche_video_part + "&q=" + keyword + "&maxResults=" + str(
            total))
    try:
        for data in response.json()["items"]:
            url='https://www.youtube.com/channel/'+data["snippet"]["channelId"]
            results[i] = {'id': i, 'idchaine': data["snippet"]["channelId"], 'titre': data["snippet"]["title"],
                          'description': data["snippet"]["description"],
                          'datePub':data["snippet"]["publishTime"],
                         'url':url,
                          'image': data["snippet"]["thumbnails"]["default"]["url"]}
            i += 1
    except Exception:
        if response.json()["error"]["code"] == 403:
            return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
        return response.json()
    return json.dumps(list(results.items()))


def getChannelsDetails(listeId):
    results = {}
    i = 0
    response = requests.get(
        racine_recherche_chaines + "?part=snippet&key=" + apiKey + "&id=" + listeId )
    try:
        for data in response.json()["items"]:
            try:
                url='https://www.youtube.com/c/'+data["snippet"]["customUrl"].replace("@","")
            except Exception:
                url='https://www.youtube.com/channel/'+data["id"]
            results[i] = {'id': i, 'idchaine': data["id"],'titre': data["snippet"]["title"],
                          'description': data["snippet"]["description"],
                          'datePub':data["snippet"]["publishedAt"],
                         'url':url,
                          'image': data["snippet"]["thumbnails"]["default"]["url"].split("=")[0]}
            i += 1
    except Exception as err:
        print("erreur",err)
        if response.json()["error"]["code"] == 403:
            return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}

        return response.json()
    return json.dumps(list(results.items()))


def getAndSaveChannels(keyword, total):
    results = {}
    i = 0
    response = requests.get(
        racine_recherche_generale + "?" + "key=" + apiKey + "&type=channel&part=" + recherche_video_part + "&q=" + keyword + "&maxResults=" + str(
            total))
    try:
        for data in response.json()["items"]:
            results[i] = {'id': i, 'idchaine': data["snippet"]["channelId"], 'titre': data["snippet"]["title"],
                          'description': data["snippet"]["description"],
                          'image': data["snippet"]["thumbnails"]["default"]["url"]}

            addChannel(data["snippet"]["description"], data["snippet"]["title"], data["snippet"]["channelId"],
                       data["snippet"]["thumbnails"]["default"]["url"])
            i += 1
    except Exception:
        if response.json()["error"]["code"] == 403:
            return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
        return response.json()
    return json.dumps(list(results.items()))


def getVideos():
    results = {}
    response = requests.get(
        racine_recherche_generale + "?" + "key=" + apiKey + "&type=video&videoDuration=" + duration + "&videoType=" + type + "&q=" + keyword + "&order=" + sortby)
    i = 0
    for data in response.json()["items"]:
        # video = Video(data["id"], urls + data["id"]["videoId"])
        # results[i] = video
        i += 1
        results[i] = {'type': data["id"]["kind"], 'url': urls + data["id"]["videoId"]}
    return results


def getChannelVideos(name, total):
    results = {}
    response = requests.get(
        racine_recherche_generale + "?" + "key=" + apiKey + "&type=video&channelId=" + name + "&order=" + sortby + "&maxResults=" + str(
            total))
    i = 0
    try:
        for data in response.json()["items"]:
            video = Video(data["id"], urls + data["id"]["videoId"])
            # results[i] = video
            i += 1
            videosInfos = getVideoDetails(data)
            # print(getVideoDetails(data))
            tags = None
            try:
                tags = videosInfos["tags"]
            except KeyError:
                tags = None
            results[i] = {'categorieId': videosInfos["categoryId"], 'channelId': videosInfos["channelId"],
                          'channelTitle': videosInfos["channelTitle"], '': videosInfos["description"],
                          'description': videosInfos["description"], 'title': videosInfos["title"],
                          'duration': str(getVideoDuration(data)),
                          'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                          'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
    except Exception:
        return response.json()

    return json.dumps(list(results.items()))


def getChannelsVideos(total):
    db = init_mongo()
    chaines = db.Chaines.find()
    listChaines = list(chaines)
    results = {}
    i = 0
    for chaine in listChaines:
        if i > int(total):
            break
        response = requests.get(
            racine_recherche_generale + "?" + "key=" + apiKey + "&type=video&channelId=" + chaine[
                "idchaine"] + "&order=" + sortby + "&maxResults=" + str(5))
        try:
            for data in response.json()["items"]:
                video = Video(data["id"], urls + data["id"]["videoId"])
                # results[i] = video
                i += 1
                videosInfos = getVideoDetails(data)
                # print(getVideoDetails(data))
                tags = None
                try:
                    tags = videosInfos["tags"]
                except KeyError:
                    tags = None
                results[i] = {'categorieId': videosInfos["categoryId"], 'channelId': videosInfos["channelId"],
                              'channelTitle': videosInfos["channelTitle"], '': videosInfos["description"],
                              'description': videosInfos["description"], 'title': videosInfos["title"],
                              'duration': str(getVideoDuration(data)),
                              'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                              'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
        except Exception as err:
            print("erreur recuperation duree: ",err)
            return response.json()
    return json.dumps(list(results.items()))


def getVideosByKeyword(key, total):
    results = {}
    response = requests.get(
        racine_recherche_generale + "?" + "key=" + apiKey + "&type=video&videoDuration=" + duration + "&videoType=" + type + "&q=" + key + "&order=" + sortby + "&maxResults=" + str(
            total))
    i = 0
    try:
        for data in response.json()["items"]:
            video = Video(data["id"], urls + data["id"]["videoId"])
            # results[i] = video
            i += 1
            videosInfos = getVideoDetails(data)
            # print(getVideoDetails(data))
            tags = None
            try:
                tags = videosInfos["tags"]
            except KeyError:
                tags = None
            results[i] = {'categorieId': videosInfos["categoryId"], 'channelId': videosInfos["channelId"],
                          'channelTitle': videosInfos["channelTitle"], '': videosInfos["description"],
                          'description': videosInfos["description"], 'title': videosInfos["title"],
                          'duration': str(getVideoDuration(data)),
                          'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                          'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
    except Exception:
        if response.json()["error"]["code"] == 403:
            return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
        return response.json()
    return json.dumps(list(results.items()))


def getVideoDetailsById(id):
    try:
        response = requests.get(
            racine_recherche_video + "?part=" + recherche_video_part + "&id=" + id + "&key=" + apiKey
        )
        # pour la duree
        response2 = requests.get(
            racine_recherche_video + "?part=" + recherche_video_part2 + "&id=" + id + "&key=" + apiKey
        )
        duration = response2.json()["items"][0]["contentDetails"]["duration"]
        dur = isodate.parse_duration(duration)
        data = response.json()["items"][0]
        videosInfos = response.json()["items"][0]["snippet"]
        res = {'categorieId': videosInfos["categoryId"], 'channelId': videosInfos["channelId"],
               'channelTitle': videosInfos["channelTitle"],
               'description': videosInfos["description"], 'title': videosInfos["title"], 'duration': str(dur),
               'image': videosInfos["thumbnails"]["default"]["url"],
               'imagehigh': videosInfos["thumbnails"]["high"]["url"],
               'url': urls + data["id"], 'videoID': data["id"]}
    except Exception as err:
        try:
            errcode=response.json()["error"]["code"]
        except KeyError:
            errcode=None
        if errcode == 403:
            return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
        return response.json()

    return {"res":res,"code":200}


def loadData():
    db = init_mongo()
    response = requests.get(
        racine_recherche_generale + "?" + "key=" + apiKey + "&type=video&videoDuration=" + duration + "&videoType=" + type + "&q=" + keyword + "&order=" + sortby)
    i = 0
    for data in response.json()["items"]:
        i += 1
        video = {'id': i, 'type': data["id"]["kind"], 'url': urls + data["id"]["videoId"]}
        videos = db.Videos
        video_id = videos.insert_one(video).inserted_id
        print("Video d'id ", video_id, " inserée")


def getStoredVideos():
    db = init_mongo()
    videosCursor = db.Videos.find()
    l = list(videosCursor)  # Converts object to list
    d = dumps(l, indent=2)
    return d


def getStoredVideos():
    db = init_mongo()
    videosCursor = db.Videos.find()
    l = list(videosCursor)  # Converts object to list
    d = dumps(l, indent=2)
    return d


def getStoredChannels():
    db = init_mongo()
    chaines = db.Chaines.find()
    l = list(chaines)
    d = dumps(l, indent=2)
    return d


def addVideo(type, url):
    db = init_mongo()
    videomaxID = db.Videos.find().sort("id", -1)[0]
    pprint.pprint(videomaxID)
    i = videomaxID["id"] + 1
    video = {'id': i, 'type': type, 'url': url}
    video_id = db.Videos.insert_one(video).inserted_id
    return "video d'id " + str(i) + " inseree !"


def addChannel(description, titre, id, image):
    db = init_mongo()
    chainemaxID = None
    try:
        chainemaxID = db.Chaines.find().sort("id", -1)[0]
        pprint.pprint(chainemaxID)
    except Exception as e:
        print(e)
    if (chainemaxID):
        i = chainemaxID["id"] + 1
    else:
        i = 0
    chaine = {'id': i, 'idchaine': id, 'titre': titre, 'description': description, 'image': image}
    chaine_id = db.Chaines.insert_one(chaine).inserted_id
    return "chaine d'id " + str(i) + " inseree !"


def deleteVideo(id):
    db = init_mongo()
    deletequery = {"id": int(id)}
    db.Videos.delete_one(deletequery)
    deleted = dumps({"id": id}, indent=2)
    return deleted


def deleteChannel(id):
    db = init_mongo()
    deletequery = {"id": int(id)}
    chaine = db.Chaines.delete_one(deletequery)
    deleted = dumps({"id": id}, indent=2)
    return deleted


class Video:
    def __init__(self, id, url):
        self.id = id
        self.url = url

#        docker build -t alljudo-python-youtube-api .
#docker images
#docker tag dd61fafcfbea registry.heroku.com/alljudo-python-youtube-api/web
#docker push registry.heroku.com/alljudo-python-youtube-api/web
#heroku container:release web -a alljudo-python-youtube-api

