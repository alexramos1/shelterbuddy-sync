# retrieve one animal - for debugging purposes
from chalicelib.shelterbuddy import ShelterBuddyConnection
import json
import sys
from chalicelib.shelterbuddy import DecimalEncoder

conn = ShelterBuddyConnection()

info = conn.fetchAnimal(sys.argv[1])

print(json.dumps(info, indent=4, cls=DecimalEncoder))
