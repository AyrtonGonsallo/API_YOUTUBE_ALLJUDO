import mysql.connector
from bson.json_util import dumps, loads
import requests
import json
from main import Video, getVideoDetails, getVideoDuration

# parametres youtube
racine_recherche_generale = "https://www.googleapis.com/youtube/v3/search"
sortby = "relevance"
urls = "https://www.youtube.com/watch?v="


class DataMysql:
    def __init__(self, keyID, apikey, connexion, totalKeys):
        self.keyID = keyID
        self.connexion = self.init_mysql()
        self.apikey = self.getAPIKey(self.keyID)
        self.totalKeys = self.getTotalKeys()

    def init_mysql(self):
        cnx = mysql.connector.connect(
            host="lhcp2091.webapps.net",
            user="v83j6wh7_alljudo",
            password="Om~WAZgp]Gb4",
            database='v83j6wh7_alljudo'
        )
        return cnx

    def getAPIKey(self, id):
        cles = self.connexion.cursor(buffered=True)
        requette2 = (
            "SELECT * FROM youtube_data_api_keys"
        )
        cles.execute(requette2)
        listKeys = list(cles)
        apiKey = listKeys[int(id) - 1]
        print("MYSQL: nombre de clés", len(listKeys))
        print("MYSQL: clé ", id, " recupérée", apiKey)
        return apiKey

    def getChannels(self):
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT * FROM youtube_data_api_chaines limit 2"
        )
        curseur.execute(requette)
        for chaine in curseur:
            print(chaine)

    def getTotalKeys(self):
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT count(*) as total FROM youtube_data_api_keys"
        )
        curseur.execute(requette)
        return curseur.fetchone()[0]

    def changekey(self, id):
        if 0 < id <= self.totalKeys:
            self.apikey = self.getAPIKey(id)
            return 0
        else:
            return -1

    def getMysqlStoredVideos(self):
        results = {}
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT * FROM youtube_data_api_videos"
        )
        curseur.execute(requette)
        i = 0
        for data in curseur:
            results[i] = {'ID': data[0],
                          'categorie_id': data[1],
                          'channel_id': data[2],
                          'channel_title': data[3],
                          'description': data[4],
                          'title': data[5],
                          'duration': data[6],
                          'image': data[7],
                          'tags': data[8],
                          'url': data[9],
                          'video_id': data[10],
                          }
            i += 1
        return results

    def getMysqlStoredChannels(self):
        results = {}
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT * FROM youtube_data_api_chaines"
        )
        curseur.execute(requette)
        i = 0
        for data in curseur:
            results[i] = {'ID': data[0],
                          'idchaine': data[1],
                          'titre': data[2],
                          'description': data[3],
                          'image': data[4]
                          }
            i += 1
        return results

    def ajouterVideosSuggestions(self, total, save):

        return self.getChannelsVideos(total,save)

    def saveVideo(self, video):
        print('Mysql: Enregistrement de la video ',video['videoID'])
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "INSERT INTO youtube_data_api_videos(categorie_id, channel_id, channel_title, description, title, duration, image, tags, url, video_id) "
            "VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"
        )
        curseur.execute(requette,(video['categorieId'],video['channelId'],video['channelTitle'],video['description'],
                        video['title'],video['duration'],video['image'],str(video['tags']),
                        video['url'],video['videoID'])
                        )
        self.connexion.commit()

    def getChannelsVideos(self, total, save):
        cursorchaines = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT * FROM youtube_data_api_chaines"
        )
        cursorchaines.execute(requette)
        chaines = cursorchaines.fetchall()
        nombredechaines = cursorchaines.rowcount
        if(total>nombredechaines):
          vpc = (total // nombredechaines)
          vdc = total - (vpc * nombredechaines)
        else:
          vpd=1
          vdc=1
        print("nombre de chaines ", nombredechaines)
        print("videos par chaines ", vpc)
        print("videos sur la derniere chaine ", vdc)
        results = {}
        for i in range(nombredechaines):
            n = vpc
            if i == (nombredechaines - 1):
                n = vdc

            id = chaines[i][1]
            response = requests.get(
                racine_recherche_generale + "?" + "key=" + self.apikey[1] + "&type=video&channelId=" +
                id + "&order=" + sortby + "&maxResults=" + str(n))
            try:
                for data in response.json()["items"]:
                    video = Video(data["id"], urls + data["id"]["videoId"])

                    videosInfos = getVideoDetails(data)
                    # print(getVideoDetails(data))
                    tags = None
                    try:
                        tags = videosInfos["tags"]
                    except KeyError:
                        tags = None
                    results[i] = {'categorieId': videosInfos["categoryId"], 'channelId': videosInfos["channelId"],
                                  'channelTitle': videosInfos["channelTitle"],
                                  'description': videosInfos["description"], 'title': videosInfos["title"],
                                  'duration': str(getVideoDuration(data)),
                                  'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                                  'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
            except Exception:
                return response.json()
        if save == 1:
            print("sauvegarde")
            for video in list(results.items()):
                self.saveVideo(video[1])
        if(total>nombredechaines):
            return json.dumps(list(results.items()))
        else:
          return json.dumps(list(results.items())[0:total])
