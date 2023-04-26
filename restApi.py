import os

from flask import Flask, request
from flask_cors import CORS, cross_origin
import main
from alljudoDatas import DataMysql
from allmarathonDatas import DataMysql2

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

main.getAPIKey()
dataMysql = DataMysql(4, None, None, None)
dataMysql2 = DataMysql2(2, None, None, None)

@app.route("/")
def home():
    return '''
    <h1>API ALLJUDO DE RECHERCHE YOUTUBE </h1>
    <h4>Urls MongoDB</h4>
    <ul>
        <li>getVideos <span style="color:red">recuperer l'ensemble des videos</span></li>
        <li>getVideosByKeyword/keyword/total <span style="color:red">recuperer l'ensemble des videos par mot clé</span></li>
        <li>getVideoDetailsById/id <span style="color:red">recuperer les infos d'une video</span></li>
        <li>getChannelsVideos/total <span style="color:red">recuperer l'ensemble des videos de toutes les chaines</span></li>
        <li>getChannelVideos/cid/total <span style="color:red">recuperer l'ensemble des videos d'une chaine</span></li>
        <li>getChannelsByKeyword/keyword/total/save <span style="color:red">recuperer l'ensemble des chaines par mot clé et les sauvegarder ou pas</span></li>
        <li>getGoogleSearchResultsByKeyword/keyword/total <span style="color:red">recuperer les resultats de google</span></li>
        <li>getImagesByKeyword/keyword/total <span style="color:red">recuperer l'ensemble des images google</span></li>
        <li>addChannel/description/titre/id/image <span style="color:red">ajouter une chaine</span></li>
        <li>deleteVideo <span style="color:red">supprimer une video</span></li>
        <li>deleteChannel <span style="color:red">supprimer une chaine</span></li>
        <li>getStoredChannels <span style="color:red">recuperer l'ensemble des chaines sauvegardées</span></li>
        <li>getChannelsDetailsByIds/listeId <span style="color:red">recuperer les details des chaines dont les ids sont passé</span></li>
        <li>getStoredVideos <span style="color:red">recuperer l'ensemble des videos sauvegardées</span></li>
        <li>postVideo <span style="color:red">ajouter une video</span></li>
    </ul>
    
    <br><br>
    
    <h4>Urls Mysql</h4>
    <ul>
        <li>changeAPIKey/keyID <span style="color:red">change la clé d'api utilisée si le nombre de requettes autorisées est dépassé</span></li>
        <li>getAPIKey <span style="color:red">Affiche la clé d'api courante</span></li>
        <li>getMysqlStoredChannels <span style="color:red">recuperer l'ensemble des chaines sauvegardées</span></li>
        <li>getMysqlStoredVideos <span style="color:red">recuperer l'ensemble des videos de suggestions sauvegardées dans la base</span></li>
        <li>ajouterVideosSuggestions/total/save <span style="color:red">ajouter des videos de suggestions sauvegardées</span></li>
        <li>getChannelsVideosSuggestions/total/save <span style="color:red">recuperer l'ensemble des videos de suggestions et les sauvegarder ou pas</span></li>
        <li>ajouterVideosRecentes/chaineID/total/save <span style="color:red">recuperer les dernieres videos des chaines suivies si chaineid=all ou de la chaine dont l'id est passé en parametre et les sauvegarder ou pas</span></li>
        <li>changeAPIKey2/keyID <span style="color:red">change la clé d'api utilisée si le nombre de requettes autorisées est dépassé (sur allmarathon)</span></li>
        <li>getAPIKey2 <span style="color:red">Affiche la clé d'api courante (sur allmarathon)</span></li>
        <li>getMysqlStoredChannels2 <span style="color:red">recuperer l'ensemble des chaines sauvegardées (sur allmarathon)</span></li>
        <li>getMysqlStoredVideos2 <span style="color:red">recuperer l'ensemble des videos de suggestions sauvegardées dans la base (sur allmarathon)</span></li>
        <li>ajouterVideosSuggestions2/total/save <span style="color:red">ajouter des videos de suggestions sauvegardées (sur allmarathon)</span></li>
        <li>getChannelsVideosSuggestions2/total/save <span style="color:red">recuperer l'ensemble des videos de suggestions et les sauvegarder ou pas (sur allmarathon)</span></li>
        <li>ajouterVideosRecentes2/chaineID/total/save <span style="color:red">recuperer les dernieres videos des chaines suivies si chaineid=all ou de la chaine dont l'id est passé en parametre et les sauvegarder ou pas (sur allmarathon)</span></li>

    </ul>
    '''


@app.route("/getVideos")
def getVideos():
    return main.getVideos()


@app.route("/changeAPIKey/<keyID>")
@cross_origin()
def changeAPIKey(keyID):
    res = dataMysql.changekey(int(keyID))
    if res == -1:
        return "mauvaise valeur pour l'index de la clé"
    else:
        return "Clé Actuelle: " + str(dataMysql.apikey)


@app.route("/changeAPIKey2/<keyID>")
@cross_origin()
def changeAPIKey2(keyID):
    res = dataMysql2.changekey(int(keyID))
    if res == -1:
        return "mauvaise valeur pour l'index de la clé"
    else:
        return "Clé Actuelle: " + str(dataMysql2.apikey)


@app.route("/getAPIKey")
@cross_origin()
def getAPIKey():
    return "Clé Actuelle: " + str(dataMysql.apikey)


@app.route("/getAPIKey2")
@cross_origin()
def getAPIKey2():
    return "Clé Actuelle: " + str(dataMysql2.apikey)


@app.route("/getVideosByKeyword/<keyword>/<total>")
@cross_origin()
def getVideosByKeyword(keyword, total):
    formattedkeyword = keyword.replace("_", " ")
    return main.getVideosByKeyword(formattedkeyword, total)


@app.route("/getVideoDetailsById/<id>")
@cross_origin()
def getVideoDetailsById(id):
    return main.getVideoDetailsById(id)


# envoyer les ids de chaines dans le corps
# ou les recuperer dans la base
@app.route("/getChannelsVideosSuggestions/<total>/<save>")
@cross_origin()
def getChannelsVideosSuggestions(total, save):
    return dataMysql.getChannelsVideosSuggestions(int(total), int(save))


@app.route("/getChannelsVideosSuggestions2/<total>/<save>")
@cross_origin()
def getChannelsVideosSuggestions2(total, save):
    return dataMysql2.getChannelsVideosSuggestions(int(total), int(save))


@app.route("/ajouterVideosRecentes/<chaineID>/<total>/<save>")
@cross_origin()
def ajouterVideosRecentes(total, chaineID, save):
    if (chaineID == "all"):
        return dataMysql.ajouterVideosRecentes(int(total), int(save))
    else:
        return dataMysql.ajouterVideosRecentesOneChannel(chaineID, int(total), int(save))


@app.route("/ajouterVideosRecentes2/<chaineID>/<total>/<save>")
@cross_origin()
def ajouterVideosRecentes2(total, chaineID, save):
    if (chaineID == "all"):
        return dataMysql2.ajouterVideosRecentes(int(total), int(save))
    else:
        return dataMysql2.ajouterVideosRecentesOneChannel(chaineID, int(total), int(save))


@app.route("/getChannelVideos/<cid>/<total>")
@cross_origin()
def getChannelVideos(cid, total):
    return main.getChannelVideos(cid, total)


@app.route("/getChannelsByKeyword/<keyword>/<total>/<save>")
@cross_origin()
def getChannelsByKeyword(keyword, total, save):
    if int(save) == 0:
        return main.getChannels(keyword, total)
    elif int(save) == 1:
        return main.getAndSaveChannels(keyword, total)
    else:
        return "3eme parametre invalide.\n Entrez 1 pour sauvegarder, 0 pour non"


@app.route("/getChannelsDetailsByIds/<listeId>")
@cross_origin()
def getChannelsDetailsById(listeId):
    return main.getChannelsDetails(listeId)


@app.route("/getGoogleSearchResultsByKeyword/<keyword>/<total>")
@cross_origin()
def getGoogleSearchResultsByKeyword(keyword, total):
    formattedkeyword = keyword.replace("_", " ")
    return main.getGoogleSearchResultsByKeyword(formattedkeyword, total)


@app.route("/getVideo/<id>")
@cross_origin()
def getVideo(id):
    return main.getVideo(id)


@app.route("/getImagesByKeyword/<keyword>/<total>")
@cross_origin()
def getImagesByKeyword(keyword, total):
    formattedkeyword = keyword.replace("_", " ")
    return main.getImages(formattedkeyword, total)


@app.route("/getStoredVideos")
@cross_origin()
def getStoredVideos():
    return main.getStoredVideos()


@app.route("/getStoredChannels")
@cross_origin()
def getStoredChannels():
    return main.getStoredChannels()


@app.route("/getMysqlStoredVideos")
@cross_origin()
def getMysqlStoredVideos():
    return dataMysql.getMysqlStoredVideos()


@app.route("/getMysqlStoredVideos2")
@cross_origin()
def getMysqlStoredVideos2():
    return dataMysql2.getMysqlStoredVideos()


@app.route("/getMysqlStoredChannels")
@cross_origin()
def getMysqlStoredChannels():
    return dataMysql.getMysqlStoredChannels()


@app.route("/getMysqlStoredChannels2")
@cross_origin()
def getMysqlStoredChannels2():
    return dataMysql2.getMysqlStoredChannels()


@app.route("/ajouterVideosSuggestions/<total>/<save>")
@cross_origin()
def ajouterVideosSuggestions(total, save):
    return dataMysql.ajouterVideosSuggestions(int(total), int(save))


@app.route("/ajouterVideosSuggestions2/<total>/<save>")
@cross_origin()
def ajouterVideosSuggestions2(total, save):
    return dataMysql2.ajouterVideosSuggestions(int(total), int(save))


# Endpoint pour la suppression d'une video
@app.route("/deleteVideo/<id>", methods=["DELETE"])
@cross_origin()
def deleteVideo(id):
    return main.deleteVideo(id)


@app.route("/deleteChannel/<id>", methods=["DELETE"])
@cross_origin()
def deleteChannel(id):
    return main.deleteChannel(id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return '''
                      <h1>The username value is: {}</h1>
                      <h1>The password value is: dsd{}$!&·%"·</h1>'''.format(username, password)

        # otherwise handle the GET request
    return '''
              <form method="POST">
                  <div><label>Username: <input type="text" name="username"></label></div>
                  <div><label>Password: <input type="password" name="password"></label></div>
                  <input type="submit" value="Submit">
              </form>'''


@app.route('/addVideo', methods=['GET', 'POST'])
def addVideo():
    if request.method == 'POST':
        type = request.form.get('type')
        url = request.form.get('url')
        res = main.addVideo(type, url)
        return '''
                      <h1>{}</h1>
                      <h5>The type value is: {}</h5>
                      <h5>The url value is: {}</h5>'''.format(res, type, url)

        # otherwise handle the GET request
    return '''
              <form method="POST">
                  <div><label>type: <input type="text" name="type"></label></div>
                  <div><label>url: <input type="text" name="url"></label></div>
                  <input type="submit" value="Submit">
              </form>'''


@app.route('/addChannel', methods=['GET', 'POST'])
def addChannel():
    if request.method == 'POST':
        titre = request.form.get('titre')
        description = request.form.get('description')
        id = request.form.get('id')
        image = request.form.get('image')
        res = main.addChannel(titre, description, id, image)
        return '''
                      <h1>{}</h1>
                      <h5>Titre: {}</h5>
                      <h5>description: {}</h5>
                      <h5>idchaine: {}</h5>
                      <h5>image: {}</h5>'''.format(res, titre, description, id, image)

        # otherwise handle the GET request
    return '''
              <form method="POST">
                  <div><label>titre: <input type="text" name="titre"></label></div>
                  <div><label>description: </label></div>
                  <div><textarea name="description" rows="10" cols="70"></textarea></div>
                  <div><label>idchaine: <input type="text" name="id"></label></div>
                  <div><label>image: <input type="text" name="image"></label></div>
                  <input type="submit" value="Submit">
              </form>'''


@app.route('/addChannel/<description>/<titre>/<id>/<image>', methods=['GET', 'POST'])
@cross_origin()
def addChannel2(description, titre, id, image):
    main.addChannel(description, titre, id, image)


@app.route('/postVideo', methods=['GET', 'POST'])
@cross_origin()
def postVideo():
    content = request.get_json(silent=True)
    main.addVideo(content["type"], content["url"])
    return "bien recu. Url=" + content['url'] + "& type=" + content['type']


'''

set FLASK_APP=restApi.py
set FLASK_ENV=developpement
flask run
'''

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
