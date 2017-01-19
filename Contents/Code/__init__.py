import bitport


NAME = 'Bitport'

ART = 'art-default.jpg'
ICON = 'icon-default.png'


def Start():
    Plugin.AddViewGroup('InfoList', viewMode = 'InfoList', mediaType = 'items')
    Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')
    Plugin.AddViewGroup('Photos', viewMode = 'List', mediaType = 'photos')
    
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    
    DirectoryItem.thumb = R(ICON)


@handler('/video/bitport', NAME, art = ART, thumb = ICON)
def MainMenu():
    return ParseDirectory(0, NAME)


@route('/video/bitport/directory/{id}')
def ParseDirectory(id, name):
    oc = ObjectContainer(title1 = name, view_group = 'InfoList')

    oc.add(PrefsObject(title = L('Preferences')))

    token = Prefs['access_token']
    if token == "":
        Log.Info("login olunmamis hic!")
        return ObjectContainer(header="Login", message="Enter your access token in Preferences.")

    client = bitport.Client(token)


    try:
        for f in client.File.list(id):
            if isinstance(f, client.Directory):
                oc.add(DirectoryObject(
                    key = Callback(ParseDirectory, id = f.id, name = f.name),
                    title = f.name))
            
            elif f.video:
                oc.add(VideoClipObject(
                    key = Callback(Lookup, id = f.id),
                    items = [ MediaObject(parts = [ PartObject(key = Callback(PlayMedia, url = f.stream_url)) ]) ],
                    rating_key = f.id,
                    title = f.name,
                    thumb = None))
            
            else:
                Log.Info("Unsupported file: '%s'" % f.name)
    except:
        Log.Exception("Files couldn't fetch. Access token is wrong or missing.")

    return oc


@route('/video/bitport/lookup')
def Lookup(id):
    oc = ObjectContainer()
#    uid = abs(hash(id))
    
    client = bitport.Client(Prefs['access_token'])
    f = client.File.get(id)
    
    if f.video:
        oc.add(VideoClipObject(
            key = Callback(Lookup, id = f.id),
            items = [ MediaObject(parts = [ PartObject(key = Callback(PlayMedia, url = f.stream_url)) ]) ],
            rating_key = f.id,
            title = f.name,
            thumb = None))
    
    else:
        Log.Info("Unsupported file: '%s'" % f.name)
    
    return oc


@route('/video/bitport/play')
def PlayMedia(url):
    return Redirect(url)
