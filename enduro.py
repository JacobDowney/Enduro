import consts
import helper
import pickle
from pythonstrava.strava import Strava
from tabulate import tabulate


### TODOS
# Top Description about private methods
# Move all sub storage_type methods to their own methods

# Eventually update enduros.json to different format


"""
There are currently 3 main storage systems that are being used to store different
activities, segments, and enduro attempts. There is pickle, database, and json.
There are two types of methods that are accessible for this class:

Get methods retreive currently stored information in one of the storage types.
These can be accessed from anywhere and should retrieve information quickly.
These methods consist of:
    - tabulate_enduro_attempts(enduro_name, storage_type=consts.PICKLE)
    - get_enduro_attempts(enduro_name, storage_type=consts.PICKLE)
    - get_enduro_segments(storage_type)
    - get_all_activities(storage_type=consts.JSON)
    - get_mtb_ride_activities(storage_type=consts.JSON)

Update and Generate methods retrive new information, typically through the
strava api. These updaters should only be accessed from controller.py which will
write to configs/updates.txt the time and method that is being accessed as a sort
of version control. These methods are very compute, memory, and request intensive
as they make numerous calls to the api and complete various operations. These
methods consist of:
    - update_enduro_attempts(storage_type=consts.PICKLE)
    - update_enduro_segments(strava_info, storage_type)
    - update_activities(strava_info, storage_type=consts.JSON, num_activities=200)
    - generate_new_activities(strava_info, storage_type=consts.JSON)
"""

################################################################################
###############################   GET METHODS   ################################
################################################################################


def tabulate_enduro_attempts(enduro_name, storage_type=consts.JSON):
    """Returns a string that is formatted for all the current enduro attempts.
    The most recent enduro attempts will be at the top. This does not read any
    new activities from strava, just current ones from get_enduro_attempts().
    Format will follow this format:
    NAME          DISTANCE   ELEVATION Track1 Track(n-1) Track(n) TOTAL TIME
    ------------- ---------- --------- ------ ---------- -------- ----------
    recovery ride 3.78 miles 1502 feet 1:12   3:04      2:22      6:38
    fun ride      9.48 miles 3420 feet 1:10   3:01      2:20      6:31

    Args:
        Required String: enduro_name // From enduros.json

    Returns:
        Returns a formatted string of the enduro attempts.

    Raises:
    """
    # Gets all the enduro attempts and iterates through formatting them.
    enduro_attempts = get_enduro_attempts(enduro_name, storage_type)
    data = []
    for enduro_attempt in enduro_attempts:
        distance = '{} miles'.format(str(round(enduro_attempt['distance'] * 0.000621371, 2)))
        elevation_gain = '{} feet'.format(str(int(enduro_attempt['total_elevation_gain'] * 3.28084)))
        sub_data = [enduro_attempt['name'], distance, elevation_gain]
        segment_attempts = enduro_attempt['segment_attempts']
        for segment_attempt_id in segment_attempts:
            sub_data.append(helper.to_min_sec_str(segment_attempts[segment_attempt_id]['elapsed_time']))
        sub_data.append(helper.to_min_sec_str(enduro_attempt['enduro_time']))
        data.append(sub_data)
    # Sets up the headers for each of the stages
    header = ['NAME', 'DISTANCE', 'ELEVATION']
    if len(enduro_attempts > 0):
        segment_attempts = enduro_attempts[0]['segment_attempts']
        for segment_attempt_id in segment_attempts:
            header.append(segment_attempts[segment_attempt_id]['name'])
    header.append('TOTAL TIME')
    return tabulate(data, headers=header)

def get_enduro_attempts(enduro_name, storage_type=consts.JSON):
    """Returns a list of enduro attempt dicts representing each enduro attempt.
    The source of these enduro attempts will be based upon the storage_type
    parameter.

    Args:
        Required String: enduro_name // From enduros.json
        Optional String: storage_type // pickle, database, json

    Returns:
        Returns a formatted string of the enduro attempts.

    Raises:
    """
    return helper.storage_type_functions(
        storage_type,
        pickle = helper.read_pickle(consts.enduro_attempts_pickle)[enduro_name],
        database = None,
        json = helper.read_json(consts.enduro_attempts_json)[enduro_name]
    )

def get_all_activities(storage_type=consts.JSON):
    """Returns a list of all strava activities (not only me activities)

    Args:
        Optional String: storage_type // pickle, database, json

    Returns:
        Returns a list of all strava activities

    Raises:
    """
    return helper.storage_type_functions(
        storage_type,
        pickle = None,
        database = None,
        json = helper.read_json(consts.all_activities_json)
    )

def get_mtb_ride_activities(storage_type=consts.JSON):
    """Returns a list of mtb strava activities

    Args:
        Optional String: storage_type // pickle, database, json

    Returns:
        Returns a list of mtb ride strava activities

    Raises:
    """
    return helper.storage_type_functions(
        storage_type,
        pickle = helper.filter_enduros(get_all_activities(storage_type)),
        database = helper.filter_enduros(get_all_activities(storage_type)),
        json = helper.read_json(consts.mtb_ride_activities_json)
    )


################################################################################
########################   UPDATE & GENERATE METHODS   #########################
################################################################################


def update_enduro_attempts(storage_type=consts.JSON):
    """Reads from the activities storage_type file and goes through each
    enduro and checks if the activity has each segment from the enduro. Takes
    the best segments from each of those activities and creates an enduro
    attempt. Adds the enduro attempt to the enduro_attempts dict entry for the
    enduro name. It updates this enduro attempt map to the given storage_type.
    Ex: enduro_attempts['teds'] = [enduro_attempt{...}, enduro_attempt{...}, ...]

    Args:
        Optional String: storage_type // pickle, database, json

    Returns:

    Raises:
    """
    activities = get_mtb_ride_activities(storage_type)
    enduros = helper.read_json(consts.enduros_json)
    updated_enduro_attempts = __get_updated_enduro_attempts(activities, enduros)
    helper.storage_type_functions(
        storage_type,
        pickle = None,
        database = None
        json = helper.write_to_json(enduro_attempts, consts.enduro_attempts_json)
    )

def update_enduro_segments(strava_info, storage_type=consts.JSON):
    """Reads from the enduros file and for each enduro gets the segment id for
    each segment. With each segment id it uses strava to get a detailed segment
    for that segment id and stores it in a detailed_segments dict. Writes this
    dict to whatever storage_type is provided.

    Args:
        Optional String: storage_type // pickle, database, json

    Returns:

    Raises:
    """
    strava = Strava(strava_info)
    # This doesn't depend on storage_type
    enduros = helper.read_json(consts.enduros_json)['enduros']
    detailed_segments = {}
    for enduro in enduros:
        for segment_id in enduros[enduro]:
            detailed_segments[segment_id] = strava.get_segment_by_id(segment_id)
    helper.storage_type_functions(
        storage_type,
        pickle = None,
        database = None,
        json = helper.write_to_json(detailed_segments, consts.detailed_segments_json)
    )

def update_activities(strava_info, storage_type=consts.JSON, num_activities=200):
    """Reaches out to the strava api to get the num_activities(200) most recent
    activities and inserts those into the given storage_type storage system.

    Args:
        Required Dict: strava_info // From consts
        Optional String: storage_type // pickle, database, json
        Optional int: num_activities // must be less than 200

    Returns:

    Raises:
    """
    num_activities = math.min(200, num_activities)
    strava = Strava(strava_info)
    all_activities = get_all_activities(storage_type)
    mtb_ride_activities = get_mtb_ride_activities(storage_type)
    new_activities = strava.get_logged_in_athlete_activities(page=1, per_page=num_activities)
    all_activities_sorted, mtb_ride_activities_sorted = __get_updated_activities_sorted(strava, all_activities, mtb_ride_activities, new_activities)
    helper.storage_type_functions(
        storage_type,
        pickle = None,
        database = None,
        json = write_to_jsons(all_activities_sorted, consts.all_activities_json, mtb_ride_activities_sorted, consts.mtb_ride_activities_json)
    )

def generate_new_activities(strava_info, storage_type=consts.JSON):
    """Reaches out to the strava api to get a dictionary of all summary
    activities and iterates through all them getting a detailed activity and
    storing those detailed activities in the given storage_type storage system.

    Args:
        Required Dict: strava_info // From consts
        Optional String: storage_type // pickle, database, json

    Returns:

    Raises:
    """
    strava = Strava(strava_info)
    # Getting all summary activites
    new_activities = {}
    page_num = 1
    activities = strava.get_logged_in_athlete_activities(page=page_num, per_page=200)
    while len(activities) != 0:
        page_num += 1
        for activity in activities:
            new_activities[activity['id']] = activity
        activities = strava.get_logged_in_athlete_activities(page=page_num, per_page=200)
    # Printing estimated times until completion
    print(f"Estimated Minutes Until Completion: {int((len(new_activities) / 98) * 15)}")
    all_activities_sorted, mtb_ride_activities_sorted = __get_updated_activities_sorted(strava, {}, {}, new_activities)
    # Complete strava calls and upload to storage_type
    helper.storage_type_functions(
        storage_type,
        pickle = None,
        database = None,
        json = write_to_jsons(all_activities_sorted, consts.all_activities_json, mtb_ride_activities_sorted, consts.mtb_ride_activities_json)
    )


################################################################################
################################################################################
################################################################################
###################   HELPER CLASSES AND METHODS (PRIVATE)   ###################
################################################################################
################################################################################
################################################################################


# Helper for update_enduro_attempts()
# Goes through each enduro in enduros and then goes through each segment in each
# activity and if the segment_id is in the enduro segments adds and it is either
# not in the best efforts or it is better then the best effort for that segment,
# it adds it to that best_attempts dict. If the best_attempts dict has all the
# segments it sorts them and adds it to enduro_attempts which is returned.
def __get_updated_enduro_attempts(activities, enduros):
    enduro_attempts = {}
    # Calculate all the best efforts for enduros
    for enduro_name in enduros['enduro_names']:
        segments = enduros['enduros'][enduro_name]
        for activity_id in activities:
            activity = activities[activity_id]
            best_attempts = {}
            for segment_effort in activity.get('segment_efforts', []):
                if 'segment' not in segment_effort or 'id' not in segment_effort['segment']:
                    print('segment or id not in segment_effort:', segment_effort)
                    continue
                segment_id = str(segment_effort['segment']['id'])
                if segment_id in segments and (segment_id not in best_attempts or best_attempts[segment_id].elapsed_time > segment_effort['elapsed_time']):
                    best_attempts[segment_id] = {
                        'segment_id': str(segment_effort['segment'].get('id', '')),
                        'segment_effort_id': str(segment_effort.get('id', 0)),
                        'name': str(segment_effort['segment'].get('name', '')),
                        'distance': int(segment_effort['segment'].get('distance', 0)),
                        'elapsed_time': int(segment_effort.get('elapsed_time', 0)),
                        'average_watts': int(segment_effort.get('average_watts', 0)),
                        'average_heartrate': int(segment_effort.get('average_heartrate', 0)),
                        'max_heartrate': int(segment_effort.get('max_heartrate', 0))
                    }
            # If there is a segment for every segment in the enduro, sort & add
            if len(best_attempts) == len(segments):
                sorted_segment_attempts = [best_attempts[segment_id] for segment_id in segments]
                if enduro_name not in enduro_attempts:
                    enduro_attempts[enduro_name] = []
                # Update activity for enduro_attempts
                activity['id'] = str(activity.get('id', ''))
                activity['distance'] = int(activity.get('distance', 0))
                activity['total_elevation_gain'] = int(activity.get('total_elevation_gain', 0))
                activity['max_speed'] = int(activity.get('max_speed', 0))
                activity['calories'] = int(int(activity.get('calories', 0))
                activity['segment_attempts'] = sorted_segment_attempts
                activity['enduro_time'] = sum(attempt.elapsed_time for attempt in segment_attempts)
                enduro_attempts[enduro_name].append(activity)
    return enduro_attempts

# Helper for update_activities() and generate_new_activities()
# Goes through each of the new activities and if they aren't in all_activities
# or mtb_ride_activities it calls stragva to get the detailed activity based on
# that activity id. It sorts those activities based on the upload_id and returns
def __get_updated_activities_sorted(strava, all_activities, mtb_ride_activities, new_activities):
    for new_activity in new_activities:
        # Adding new activities not in all_activities to it.
        if new_activity['id'] not in all_activities:
            all_activities[new_activity['id']] = strava.get_activity_by_id(new_activity['id'])
            # Adding new activities not in mtb_ride_activities to it.
        if new_activity['id'] not in mtb_ride_activities and helper.is_mtb_ride(new_activity):
            mtb_ride_activities[new_activity['id']] = all_activities[new_activity['id']]
    # Writing both of the dictionaries to their consts
    all_activities_sorted = dict(sorted(all_activities.items(), key=lambda act: act[1]['upload_id'], reverse=True))
    mtb_ride_activities_sorted = dict(sorted(mtb_ride_activities.items(), key=lambda act: act[1]['upload_id'], reverse=True))
    return all_activities_sorted, mtb_ride_activities_sorted
