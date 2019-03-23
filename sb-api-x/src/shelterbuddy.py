from urllib.request import Request, urlopen
import urllib
import json
from decimal import Decimal
from os import getenv
from urllib.parse import quote

class ShelterBuddyConnection:
    "Connects to ShelterBuddy API"
    
    uriCache = {}

    def __init__(self, shelterbuddyUrl=None, username=None, password=None):
        if shelterbuddyUrl is None:
            shelterbuddyUrl = getenv("SHELTERBUDDY_API_URL")
            username = quote(getenv("SHELTERBUDDY_API_USER"))
            password = quote(getenv("SHELTERBUDDY_API_PASSWORD"))
        self.shelterbuddyUrl = shelterbuddyUrl
        self.token = self.authenticate(username, password)
    
    def authenticate(self, username, password):
        query = "/api/v2/authenticate?username=" + username + "&password=" + password
        req = Request(self.shelterbuddyUrl + query);
        req.add_header('Content-Type', 'application/json')
        r = urlopen(req)
        return json.loads(r.read())
        
    def loadAnimals(self, target, cutoff):
        self._loadAnimals(target, cutoff, lambda x: [(yield a) for a in x], lambda x:x)
        
    def _loadAnimals(self, target, cutoff, actionFunction, checkpointFunction):
        
        postparm = ("{ 'UpdatedSinceUTC':'" + cutoff + "'}").encode('utf-8')
    
        while target != None:
            
            print(target)
            
            req = Request(self.shelterbuddyUrl + target, method='POST', data=postparm)
            
            req.add_header("sb-auth-token", self.token)
            req.add_header("content-type", "application/json")
            r = urlopen(req)
            
            data = json.loads(r.read(), parse_float=Decimal)
            
            actionFunction(data['Data'])
            
            target = data['Paging']['Next']
            try:   
                last = max([animal['LastUpdatedUtc'] for animal in data['Data']])
            except:
                last = cutoff         

            checkpointFunction(target, last, cutoff)
            
            for animal in data['Data']:
                yield animal
    
    def fetchUri(self, uri):
        if not(uri in self.uriCache):
            req = Request(self.shelterbuddyUrl + uri)
            
            req.add_header("sb-auth-token", self.token)
            req.add_header("content-type", "application/json")
            
            r = urlopen(req)
            self.uriCache[uri] = json.loads(r.read())

        return self.uriCache[uri]
    
    def fetchPhotos(self, animalId):
        
        postparam = urllib.parse.urlencode({"AnimalId": animalId})
        print(postparam)
        url = self.shelterbuddyUrl + "/api/v2/animal/photo/list?page=1&pageSize=100"
        req = Request(url, method='POST', data=postparam.encode('utf-8'))
        req.add_header("sb-auth-token", self.token)
        req.add_header("content-type", "application/x-www-form-urlencoded")
        
        r = urlopen(req)
        
        obj = json.loads(r.read(), parse_float=Decimal)

        for photo in obj['Data']:
            del photo['Animal'] 
        
        return obj['Data']