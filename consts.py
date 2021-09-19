# Files needed
prefix = "configs/"
enduros_json               = prefix + "enduros.json"
updates_txt                = prefix + "updates.txt"
all_activities_json        = prefix + "all_activities.json"
mtb_ride_activities_json   = prefix + "mtb_ride_activities.json"
enduro_attempts_json       = prefix + "enduro_attempts.json"
detailed_segments_json     = prefix + "detailed_segments.json"
enduro_attempts_pickle     = prefix + "enduro_attempts.p"

# Strava Athlete information
athlete_id = '33719269'
# Strava Information
strava_info = {
    'client_id'       : '65128',
    'client_secret'   : '5c5310cdc850bbb385539831b6c07d7d19cc2730',
    'refresh_token'   : 'ae87c5d5b420a4019007a66815324b74dcd0f11d',
    'grant_type'      : 'refresh_token'
}

# Storage Types
PICKLE = "PICKLE"
DATABASE = "DATABASE"
JSON = "JSON"
DEFAULT_STORAGE_TYPE = PICKLE
