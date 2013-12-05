import config
import activity_info
import urls
import authenticate

session = authenticate.authenticate(config)

if session == False:
    print "Auth error:"
else:
    print activity_info.activity_info(config, session, "7436288143")

