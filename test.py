import config
import activity_info
import urls
import authenticate

session = authenticate.authenticate(config)

print activity_info.activity_info(config, session, "7436288143")

