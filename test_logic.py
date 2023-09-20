from xbox_client import authenticate, get_x_token

# Approach 1 ------------------------------------------------
# Authenticate the user
token, authorization_header = authenticate("sanaullah.softtik@outlook.com", "slanty123")

print("Token:\n", token)
print("authorization_header:\n", authorization_header)
xuid_parse = authorization_header.split(";")[0]
xuid = xuid_parse.split("=")[1]
print("XUID: ",xuid)


# Approach 2 ------------------------------------------------
get_x_token()
