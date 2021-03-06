from subprocess import check_output
import json

root = "http://127.0.0.1:8080"
root = "http://swansonbfinalproject.appspot.com"
#root = "http://swansonbassign4.appspot.com"

snippets = [
    [
        {
            "title":"hertz1",
            "notes":"check this out",
            "videoID":"ByQD6tAE2yU",
            "startTime":0,
            "endTime":15
        },
        {
            "title":"heartz2",
            "videoID":"ByQD6tAE2yU",
            "startTime":30,
            "endTime":55
        },
        {
            "title":"ute",
            "notes":"here is a different lookout",
            "videoID":"YLZoPcGKq7M",
            "startTime":65,
            "endTime":120
        }
    ],
    [
        {
            "title":"top of the morning",
            "videoID":"TLBIufF7G1I",
            "startTime":0,
            "endTime":5
        },
        {
            "title":"jack truck",
            "notes":"super truck super truck super truck super truck",
            "videoID":"TLBIufF7G1I",
            "startTime":20,
            "endTime":400
        },
        {
            "title":"punch the like button",
            "notes":"<Like a Boss!!!!>",
            "videoID":"TLBIufF7G1I",
            "startTime":882,
            "endTime":887
        }
    ],
    [
        {
            "title":"short computerphile",
            "videoID":"vrjAIBgxm_w",
            "startTime":20,
            "endTime":21
        }
    ],
    [
        {
            "title":"Wythecombe",
            "videoID":"Z4Mfx59GA6I",
            "startTime":72,
            "endTime":90,
            "notes": "When I started my first degree this building was still boarded up"
        },
        {
            "title":"OMG Goats",
            "videoID":"Z4Mfx59GA6I",
            "startTime":178,
            "endTime":182
        },
        {
            "title":"KBVR-FM production studio",
            "videoID":"FHKNBl1RxZc",
            "startTime":236,
            "endTime":250,
            "notes": "I used to work here, with that guy"
        },
        {
            "title":"This is the only building shown in the brochure",
            "videoID":"5NZikvFrfEM",
            "startTime":14,
            "endTime":15,
            "notes": "Aint that the truth, It's just a dorm"
        }
    ]

]


testPlaylists = [
    {"title":"Lookouts"},
    {"title": "Super Truck", "public":None},
    {"title": "Computerphile", "public":None},
    {"title": "OSU Tour"}
]

class user:
    def __init__(self):
        pass

jack = user()
jack.name = {"name":"JackABoy", "password":"jpass"}
jack.playlists = zip(testPlaylists[:2], snippets[:2])

brandon = user()
brandon.name = {"name":"Brandon", "password":"bpass"}
brandon.playlists = zip(testPlaylists[2:], snippets[2:])
users = [jack, brandon]

def sendCurl(st, data=None, headers=None):

    if data:
        data = ["--data", "\"%s\""%"&".join("%s=%s"%(k,v) for k,v in data.items())]
    else:
        data = []

    headArray = []
    if headers:
        for k,v in headers.items():
            headArray.append("-H \"%s:%s\""%(k,v))


    args = ["curl"] + headArray + data + st.split(' ')
    print "SENDING CURL CALL: ", " ".join(args)
    return check_output(' '.join(args), shell=True)

#########SIGN UP USERS#########

##create users###
for u in users:
    res = sendCurl("-X POST %s%s"%(root, "/register"), data=u.name)
    print res
    res = json.loads(res)
    #print res.has_key("token") or in works
    if "token" in res and "userid" in res:
        u.tokenDir={"id":res["userid"], "token":res["token"]}
    else:
        res = sendCurl("-X POST %s%s" % (root, "/login"), data=u.name)
        print res
        res = json.loads(res)
        if "token" not in res or "userid" not in res:
            print "CRITICAL FAILURE, user not able to reg or log in"
            exit()
        u.tokenDir={"id":res["userid"], "token":res["token"]}


#######GET all current playlists#############
public_playlists = sendCurl(root + "/playlist.json")
print "PUBLIC PLAYLISTS"
print public_playlists

# #get users playlists and delete them
for u in users:
    plst = sendCurl(root + "/playlist.json", headers=u.tokenDir)
    print plst
    plst = json.loads(plst)

    for p in plst:
        print sendCurl("-X DELETE %s%s" % (root, p['url']), headers=u.tokenDir)

    print "Expected no more playlist for user"
    print sendCurl(root + "/playlist.json", headers=u.tokenDir)

print "Expected no more public playlists"
print sendCurl(root + "/playlist.json")

#create playlists
for u in users:
    for p,snpts in u.playlists:
        res = sendCurl("-X POST %s"%root, data=p, headers=u.tokenDir)
        print res
        p.update(json.loads(res))

        for s in snpts:
            res = sendCurl("-X POST %s%s" % (root, p['url']), data=s, headers=u.tokenDir)
            print res

        #check playlist  #far too verbose
        # print "Retrieveing %s playlist <%s> without auth"%("PUBLIC" if "public" in p else "", p["title"])
        # res = sendCurl("%s%s"%(root, pjson))
        # print res
        # # res = sendCurl("%s%s"%(root,purl))
        # # print res
        #
        # print "Retrieveing %s playlist <%s> with auth" % ("PUBLIC" if "public" in p else "", p["title"])
        # res = sendCurl("%s%s" % (root, pjson), headers=u.tokenDir)
        # print res
        # # res = sendCurl("%s%s" % (root, purl), headers=u.tokenDir)
        # # print res

#check public playlists
public_playlists = sendCurl(root + "/playlist.json")
print "PUBLIC PLAYLISTS"
print public_playlists
check_output('google-chrome ' + root, shell=True)


#test public/private GET of playlist HTML/JSON
print "JACKS PlAYLISTS"
print sendCurl(root + "/playlist.json", headers=jack.tokenDir)
for p, snpts in jack.playlists:
    check_output('google-chrome ' + root + p['url'], shell=True)
    if "public" in p:
        print "retrieve public playlist json without auth"
        print sendCurl("%s%s"%(root, p['json']))
    else:
        print "retrieve PRIVATE playlist json without auth"
        print sendCurl("%s%s" % (root, p['json']))

        print "retrieve PRIVATE playlist json with wrong auth"
        print sendCurl("%s%s" % (root, p['json']), headers=brandon.tokenDir)

        print "retrieve PRIVATE playlist json with auth"
        print sendCurl("%s%s" % (root, p['json']), headers=jack.tokenDir)


#test put and delete for snippet
p = jack.playlists[1][0]
playlist = json.loads(sendCurl("%s%s" % (root, p['json']), headers=jack.tokenDir))
#delete jacktruck clip
snpturl = playlist['snippets'][1]['url']
#unauth
print sendCurl("-X DELETE %s%s" % (root, snpturl))
#wrongAuth
print sendCurl("-X DELETE %s%s" % (root, snpturl), headers=brandon.tokenDir)
#correctAuth
print sendCurl("-X DELETE %s%s" % (root, snpturl), headers=jack.tokenDir)
#snippet doesnt exist
print sendCurl("-X DELETE %s%s" % (root, snpturl), headers=jack.tokenDir)

#modify last clip
snpturl = playlist['snippets'][-1]['url']
#unauth
data = {"title":"Updated Title", "startTime":"870", "notes": "Updated noetes"}
print sendCurl("-X PUT %s%s" % (root, snpturl), data=data)
#wrongAuth
print sendCurl("-X PUT %s%s" % (root, snpturl), headers=brandon.tokenDir, data=data)
#correctAuth
print sendCurl("-X PUT %s%s" % (root, snpturl), headers=jack.tokenDir, data=data)
#snippet doesnt exist
print sendCurl("-X PUT %s%s" % (root, snpturl), headers=jack.tokenDir, data=data)

print sendCurl("%s%s" % (root, p['json']), headers=jack.tokenDir)
check_output('google-chrome ' + root + p['url'], shell=True)
