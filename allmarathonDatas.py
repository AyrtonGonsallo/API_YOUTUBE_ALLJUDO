import random

import mysql.connector
from bson.json_util import dumps, loads
import requests
import json
from main import Video, getVideoDetails, getVideoDuration

# parametres youtube
racine_recherche_generale = "https://www.googleapis.com/youtube/v3/search"
sortby = "relevance"
urls = "https://www.youtube.com/watch?v="
orders = ["searchSortUnspecified", "date", "rating", "relevance", "title", "viewCount"]


class DataMysql2:
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
        """cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database='v83j6wh7_alljudo'
        )"""
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
            "SELECT * FROM youtube_data_api_chaines2 limit 2"
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
            "SELECT * FROM youtube_data_api_videos2"
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
            "SELECT * FROM youtube_data_api_chaines2"
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

        return self.getChannelsVideosSuggestions(total, save)

    def saveVideo(self, video):
        print('Mysql: Enregistrement de la video ', video['videoID'])
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "INSERT INTO youtube_data_api_videos2(categorie_id, channel_id, channel_title, description, title, duration, image, tags, url, video_id,date_pub) "
            "VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s)"
        )
        curseur.execute(requette,
                        (video['categorieId'], video['channelId'], video['channelTitle'], video['description'],
                         video['title'], video['duration'], video['image'], str(video['tags']),
                         video['url'], video['videoID'], video['date_pub'])
                        )
        self.connexion.commit()

    def getChannelsVideosSuggestions(self, total, save):
        cursorchaines = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT * FROM youtube_data_api_chaines2"
        )
        cursorchaines.execute(requette)
        chaines = cursorchaines.fetchall()
        nombredechaines = cursorchaines.rowcount
        if (total > nombredechaines):
            vpc = (total // nombredechaines)
            vdc = total - (vpc * (nombredechaines - 1))
        else:
            vpc = 1
            vdc = 1
        print("nombre de chaines ", nombredechaines)
        print("videos par chaines ", vpc)
        print("videos sur la derniere chaine ", vdc)
        results = {}
        reponse = {}
        nombredevideos = 0
        for i in range(nombredechaines):
            n = vpc
            if i == (nombredechaines - 1):
                n = vdc

            id = chaines[i][1]
            order = random.choice(orders)
            # order = sortby
            # print(i," chaine d'id ",id," tri par ",order)
            response = requests.get(
                racine_recherche_generale + "?" + "key=" + self.apikey[1] + "&type=video&channelId=" +
                id + "&order=" + order + "&maxResults=" + str(n))

            try:
                if (len(response.json()["items"]) < 1):
                    reponse[
                        str(i) + " - Chaine d'id " + id] = str(
                        i) + " - La chaine d'id " + id + " a recherché par " + order + " et n'a rien renvoyé"
                    # print("La chaine d'id ",id," n'a rien renvoyé")
                    continue
                for data in response.json()["items"]:
                    # video = Video(data["id"], urls + data["id"]["videoId"])
                    try:
                        reponse[str(i) + " - Chaine d'id " + id] += " et la video d'id " + \
                                                                    data["id"]["videoId"]
                    except:
                        reponse[str(i) + " - Chaine d'id " + id] = str(
                            i) + ": La chaine d'id " + id + " a recherché par " + order + " et renvoie la video d'id " + \
                                                                   data["id"]["videoId"]
                    # print(i,": La chaine d'id ",id," renvoi la video d'id ",data["id"]["videoId"])
                    videosInfos = getVideoDetails(data)
                    # print(getVideoDetails(data))
                    tags = None
                    try:
                        tags = videosInfos["tags"]
                    except KeyError:
                        tags = None
                    results[nombredevideos] = {'categorieId': videosInfos["categoryId"],
                                               'channelId': videosInfos["channelId"],
                                               'date_pub': videosInfos["publishedAt"],
                                               'channelTitle': videosInfos["channelTitle"],
                                               'description': videosInfos["description"], 'title': videosInfos["title"],
                                               'duration': str(getVideoDuration(data)),
                                               'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                                               'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
                    nombredevideos += 1
            except Exception as err:
                if response.json()["error"]["code"] == 403:
                    return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
                try:
                    data = data
                except Exception:
                    data = None
                erreur = {"cause de l'erreur": str(err), "numero de chaine": i, "reponse": response.json(),
                          "data": data if data else None, "mode de recherche": order}
                try:
                    reponse[str(i) + " - Erreur chaine d'id " + id] += erreur
                except KeyError:
                    reponse[str(i) + " - Erreur chaine d'id " + id] = erreur
                return reponse
        if total < len(results):
            r = total - 1
            while (r < len(results)):
                del results[r]
                r += 1
        print("video trouvées", len(results))
        reponse["video trouvées"] = len(results)
        if save == 1:
            print("sauvegarde...")
            for video in list(results.items()):
                self.saveVideo(video[1])
            return json.dumps(list(reponse.items()), ensure_ascii=False).encode('utf8')

        return json.dumps(list(reponse.items()), ensure_ascii=False).encode('utf8')

    def saveLastVideo(self, video):
        print('Mysql: Enregistrement de la video ', video['videoID'])
        self.connexion.reconnect()
        curseur = self.connexion.cursor(buffered=True)
        requette = (
            "INSERT INTO youtube_data_api_last_videos2(categorie_id, channel_id, channel_title, description, title, duration, image, tags, url, video_id,date_pub) "
            "VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s)"
        )
        curseur.execute(requette,
                        (video['categorieId'], video['channelId'], video['channelTitle'], video['description'],
                         video['title'], video['duration'], video['image'], str(video['tags']),
                         video['url'], video['videoID'], video['date_pub'])
                        )
        self.connexion.commit()

    def ajouterVideosRecentes(self, total, save):
        self.connexion.reconnect()
        cursorchaines = self.connexion.cursor(buffered=True)
        requette = (
            "SELECT * FROM youtube_data_api_chaines2"
        )
        cursorchaines.execute(requette)
        chaines = cursorchaines.fetchall()

        nombredechaines = cursorchaines.rowcount
        cursorchaines.close()
        if (total > nombredechaines):
            vpc = (total // nombredechaines)
            vdc = total - (vpc * (nombredechaines - 1))
        else:
            vpc = 1
            vdc = 1
        print("nombre de chaines ", nombredechaines)
        print("videos par chaines ", vpc)
        print("videos sur la derniere chaine ", vdc)
        results = {}
        reponse = {}
        nombredevideos = 0
        for i in range(nombredechaines):
            n = vpc
            if i == (nombredechaines - 1):
                n = vdc

            id = chaines[i][1]
            order = orders[1]
            # order = sortby
            # print(i," chaine d'id ",id," tri par ",order)
            response = requests.get(
                racine_recherche_generale + "?" + "key=" + self.apikey[1] + "&type=video&channelId=" +
                id + "&order=" + order + "&maxResults=" + str(n))

            try:
                if (len(response.json()["items"]) < 1):
                    reponse[
                        str(i) + " - Chaine d'id " + id] = str(
                        i) + " - La chaine d'id " + id + " a recherché par " + order + " et n'a rien renvoyé"
                    # print("La chaine d'id ",id," n'a rien renvoyé")
                    continue
                for data in response.json()["items"]:
                    # video = Video(data["id"], urls + data["id"]["videoId"])
                    try:
                        reponse[str(i) + " - Chaine d'id " + id] += " et la video d'id " + \
                                                                    data["id"]["videoId"]
                    except:
                        reponse[str(i) + " - Chaine d'id " + id] = str(
                            i) + ": La chaine d'id " + id + " a recherché par " + order + " et renvoie la video d'id " + \
                                                                   data["id"]["videoId"]
                    # print(i,": La chaine d'id ",id," renvoi la video d'id ",data["id"]["videoId"])
                    videosInfos = getVideoDetails(data)
                    # print(getVideoDetails(data))
                    tags = None
                    try:
                        tags = videosInfos["tags"]
                    except KeyError:
                        tags = None
                    results[nombredevideos] = {'categorieId': videosInfos["categoryId"],
                                               'channelId': videosInfos["channelId"],
                                               'date_pub': videosInfos["publishedAt"],
                                               'channelTitle': videosInfos["channelTitle"],
                                               'description': videosInfos["description"], 'title': videosInfos["title"],
                                               'duration': str(getVideoDuration(data)),
                                               'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                                               'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
                    nombredevideos += 1
            except Exception as err:
                if (response.json()["error"]["code"] == 403):
                    return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
                try:
                    data = data
                except Exception:
                    data = None
                erreur = {"cause de l'erreur": str(err), "numero de chaine": i, "reponse de l'api": response.json(),
                          "data": data if data else None, "mode de recherche": order}
                try:
                    reponse[str(i) + " - Erreur chaine d'id " + id] += erreur
                except KeyError:
                    reponse[str(i) + " - Erreur chaine d'id " + id] = erreur
                return reponse
        longueur_init=len(results)
        print("video trouvées avant filtrage",longueur_init )
        if total < longueur_init:
            r = total
            while (r < longueur_init):
                del results[r]
                r += 1
        print("video trouvées apres filtrage", len(results))
        reponse["video trouvées"] = len(results)
        reponse["videos"] = list(results.items())
        if save == 1:
            print("sauvegarde...")
            for video in list(results.items()):
                self.saveLastVideo(video[1])
            return json.dumps(list(reponse.items()), ensure_ascii=False).encode('utf8')

        return json.dumps(list(reponse.items()), ensure_ascii=False).encode('utf8')

    def ajouterVideosRecentesOneChannel(self, chaineID,total, save):

        print("chaine", chaineID)
        print("videos ", total)
        results = {}
        reponse = {}
        nombredevideos = 0
        id=chaineID
        i=0
        order = orders[1]
        response = requests.get(
            racine_recherche_generale + "?" + "key=" + self.apikey[1] + "&type=video&channelId=" +
            id + "&order=" + order + "&maxResults=" + str(total))

        try:
            if (len(response.json()["items"]) < 1):
                reponse[
                    str(i) + " - Chaine d'id " + id] = str(
                    i) + " - La chaine d'id " + id + " a recherché par " + order + " et n'a rien renvoyé"
                # print("La chaine d'id ",id," n'a rien renvoyé")
                return reponse
            for data in response.json()["items"]:
                # video = Video(data["id"], urls + data["id"]["videoId"])
                try:
                    reponse[str(i) + " - Chaine d'id " + id] += " et la video d'id " + \
                                                                data["id"]["videoId"]
                except:
                    reponse[str(i) + " - Chaine d'id " + id] = str(
                        i) + ": La chaine d'id " + id + " a recherché par " + order + " et renvoie la video d'id " + \
                                                               data["id"]["videoId"]
                # print(i,": La chaine d'id ",id," renvoi la video d'id ",data["id"]["videoId"])
                videosInfos = getVideoDetails(data)
                # print(getVideoDetails(data))
                tags = None
                try:
                    tags = videosInfos["tags"]
                except KeyError:
                    tags = None
                results[nombredevideos] = {'categorieId': videosInfos["categoryId"],
                                           'channelId': videosInfos["channelId"],
                                           'date_pub': videosInfos["publishedAt"],
                                           'channelTitle': videosInfos["channelTitle"],
                                           'description': videosInfos["description"], 'title': videosInfos["title"],
                                           'duration': str(getVideoDuration(data)),
                                           'image': videosInfos["thumbnails"]["default"]["url"], 'tags': tags,
                                           'url': urls + data["id"]["videoId"], 'videoID': data["id"]["videoId"]}
                nombredevideos += 1
        except Exception as err:
            if (response.json()["error"]["code"] == 403):
                return {"erreur": "limite journalière de requêtes autorisées par Youtube atteinte", "code": 403}
            try:
                data = data
            except Exception:
                data = None
            erreur = {"cause de l'erreur": str(err), "numero de chaine": i, "reponse de l'api": response.json(),
                      "data": data if data else None, "mode de recherche": order}
            try:
                reponse[str(i) + " - Erreur chaine d'id " + id] += erreur
            except KeyError:
                reponse[str(i) + " - Erreur chaine d'id " + id] = erreur
            return reponse

        print("video trouvées", len(results))
        reponse["video trouvées"] = len(results)
        reponse["videos"] = list(results.items())
        if save == 1:
            print("sauvegarde...")
            for video in list(results.items()):
                self.saveLastVideo(video[1])
            return json.dumps(list(reponse.items()), ensure_ascii=False).encode('utf8')

        return json.dumps(list(reponse.items()), ensure_ascii=False).encode('utf8')
