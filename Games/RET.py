import json

with open("response.txt", "r", encoding="utf-8") as f:
    response_text = f.read()

# Find the indices of all occurrences of "gamertag" in the response text
gamertag_indices = [i for i in range(len(response_text)) if response_text.startswith('"gamertag"', i)]

# Find the indices of all occurrences of "xuid" in the response text
xuid_indices = [i for i in range(len(response_text)) if response_text.startswith('"xuid"', i)]

# Extract all values of gamertag and xuid except for the first one using string slicing and manipulation
gamertags = []
for gamertag_index in gamertag_indices[1:]:
    gamertag_start = response_text.find('"', gamertag_index + len('"gamertag"')) + 1
    gamertag_end = response_text.find('"', gamertag_start)
    gamertags.append(response_text[gamertag_start:gamertag_end])

xuids = []
for xuid_index in xuid_indices[1:]:
    xuid_start = response_text.find('"', xuid_index + len('"xuid"')) + 1
    xuid_end = response_text.find('"', xuid_start)
    xuids.append(response_text[xuid_start:xuid_end])

# Save the extracted values to separate text files, appending a new line each time
with open("gamertags.txt", "a", encoding="utf-8") as f:
    for gamertag in gamertags:
        f.write(gamertag + "\n")

with open("xuids.txt", "a", encoding="utf-8") as f:
    for xuid in xuids:
        f.write(xuid + "\n")