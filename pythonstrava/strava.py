# import files
import helper
import math
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Strava:

    def __init__(self, strava_info):
        """Initializes a new Strava instance for completing api methods.

        Args:
            Required String: client_id // The application’s ID, obtained during
                                            registration.
            Required String: client_secret // The application’s secret, obtained
                                                during registration.
            Required String: refresh_token // The code parameter obtained in the
                                                redirect.
            Required String: grant_type // The grant type for the request. For =
                                            initial authentication, must always be
                                            "authorization_code".

        Returns:
            Returns a new Strava instance with all internal parameters set.

        Raises:
        """

        self.__client_id = strava_info['client_id']
        self.__client_secret = strava_info['client_secret']
        self.__refresh_token = strava_info['refresh_token']
        self.__grant_type = strava_info['grant_type']
        self.__payload = {
            'client_id':        self.__client_id,
            'client_secret':    self.__client_secret,
            'refresh_token':    self.__refresh_token,
            'grant_type':       self.__grant_type,
            'f':                'json'
        }
        self.__access_token = ''
        self.__urls = helper.read_json('pythonstrava/strava_method_urls.json')
        self.__strava_api_calls_path = 'pythonstrava/strava_api_calls.json'
        # Variables dealing with the queue for strava access time
        self.__times = []
        self.__last_index = None
        self.__15_mins = 900
        self.__24_hours = 86400
        self.__max_in_15_mins = 100 - 1
        self.__max_in_24_hours = 1000 - 1


    def __get_access_token(self):
        """Gets the current access token if it exists. If one doesn't exist, it
        generates and returns a new oauth token by making a request.

        Args:

        Returns:
            An access token string.

        Raises:
        """
        if self.__access_token == '':
            url = 'https://www.strava.com/oauth/token'
            response = requests.post(url, data=self.__payload, verify=False).json()
            self.__access_token = response['access_token']
        return self.__access_token

    def __header(self):
        """Returns an authorization header used for request with up to date
        oauth access token.

        Args:

        Returns:
            An authorization header dictionary used for request.

        Raises:
        """
        return {'Authorization': 'Bearer ' + self.__get_access_token()}

    def __url(self, method):
        """Returns the url for a method.

        Args:
            Required String: method // The method to map to a link

        Returns:

        Raises:
        """
        return 'https://www.strava.com/api/v3/' + self.__urls[method]

    def __get_rest_time_until_valid_call(self):
        """Strava API usage is limited on a per-application basis using both a
        15-minute and daily request limit. The default rate limit allows 100
        requests every 15 minutes, with up to 1,000 requests per day.

        Args:

        Returns:
            The time to wait until a call can be made.

        Raises:
        """
        # Reading the json file into function vars
        file_info = helper.read_json(self.__strava_api_calls_path)
        times = file_info['times']
        last_index = file_info['last_index']
        # Current time for this operation, floor because past implies present.
        current = math.floor(time.time())
        # Removing entries that are over 24 hours
        cut = 0
        while len(times) > cut and current - times[cut] > self.__24_hours:
            cut += 1
        times = times[cut:]
        last_index = last_index - cut
        # If there are more than max in a day, return diff until there isn't
        if len(times) > self.__max_in_24_hours:
            helper.write_to_json({"times": times, "last_index": last_index}, self.__strava_api_calls_path)
            return self.__24_hours - (current - times[0]) + 10
        # If this is the first time, setup accordingly
        if last_index == -1:
            last_index = 0
        else:
            # Move over the last_index pointer
            while current - times[last_index] > self.__15_mins and last_index < len(times) - 1:
                last_index += 1
            # Check to make sure not going over the max in 15 minutes
            if len(times) - last_index >= self.__max_in_15_mins:
                helper.write_to_json({"times": times, "last_index": last_index}, self.__strava_api_calls_path)
                return self.__15_mins - (current - times[last_index]) + 2
        # Going to make the call so add this current time.
        times.append(current)
        # Update json files with new times
        helper.write_to_json({"times": times, "last_index": last_index}, self.__strava_api_calls_path)
        return 0

    def __make_get_request(self, url, param):
        """Returns a dictionary of the results from a requests.get with the
        given url and params if within the strava api time limit.

        Args:
            Required String: url // The strava url to make a request to.
            Required dict: param // A dictionary of params for the request.

        Returns:
            a.) A dictionary of the json result from the request
            b.) A int representing the time needed to wait before next call.

        Raises:
        """
        rest_time = int(self.__get_rest_time_until_valid_call())
        if rest_time != 0:
            # If its not a valid call, rest it off and return the result then.
            print("STRAVA: Must rest", rest_time, "seconds because too many api calls.")
            time.sleep(rest_time)
            return self.__make_get_request(url, param)
        return requests.get(url, headers=self.__header(), params=param).json()

    def create_activity(self, activity_dict):
        """Creates a manual activity for an athlete. Requires activity:write
        scope.

        Args:
            activity_dict: {
                String: name // The name of the activity.
                String: type // Type of activity: Run, Ride, etc.
                Date: start_date_local // ISO 8601 formatted date time.
                Integer: elapsed_time // Time in seconds.
                String: description // Description of the activity.
                Float: distance // Distance in meters.
                Integer: trainer // Set 1 to mark as a trainer activity.
                Integer: commute // Set 1 to mark as commute.
            }

        Returns:
 .          The representation of a created activity.

        Raises:
        """
        # Post requests not yet supported
        return None

    def get_activity_by_id(self, id, include_all_efforts=True):
        """Returns the given activity that is owned by the authenticated
        athlete. Requires activity:read for Everyone and Followers activities.
        Requires activity:read_all for Only Me activities.

        Args:
            Required Long: id // The identifier of the activity.
            Boolean: include_all_efforts // The include all segment efforts.

        Returns:
            An instance of DetailedActivity.

        Raises:
        """
        url = self.__url('get_activity_by_id').format(id)
        param = {'id': id, 'include_all_efforts': include_all_efforts}
        return self.__make_get_request(url, param)

    def get_comments_by_activity_id(self, id, page=1, per_page=30):
        """Returns the comments on the given activity. Requires activity:read
        for Everyone and Followers activities. Requires activity:read_all for
        Only Me activities.

        Args:
            Required Long: id // The identifier of the activity/
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of Comment objects.

        Raises:
        """
        url = self.__url('get_comments_by_activity_id').format(id)
        param = {'id': id, 'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_kudoers_by_activity_id(self, id, page=1, per_page=30):
        """Returns the athletes who kudoed an activity identified by an
        identifier. Requires activity:read for Everyone and Followers
        activities. Requires activity:read_all for Only Me activities.

        Args:
            Required Long: id // The identifier of the activity.
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of SummaryAthlete objects.

        Raises:
        """
        url = self.__url('get_kudoers_by_activity_id').format(id)
        param = {'id': id, 'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_laps_by_activity_id(self, id):
        """Returns the laps of an activity identified by an identifier. Requires
        activity:read for Everyone and Followers activities. Requires
        activity:read_all for Only Me activities.

        Args:
            Required Long: id // The identifier of the activity

        Returns:
            An array of Lap objects.

        Raises:
        """
        url = self.__url('get_laps_by_activity_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_logged_in_athlete_activities(self, before=None, after=None, page=1, per_page=30):
        """Returns the activities of an athlete for a specific identifier.
        Requires activity:read. Only Me activities will be filtered out unless
        requested by a token with activity:read_all.

        Args:
            Integer: before // An epoch timestamp to use for filtering
                               activities that have taken place before a certain
                               time.
            Integer: after // An epoch timestamp to use for filtering activities
                              that have taken place after a certain time.
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30. Max
                                is 200.

        Returns:
            An array of SummaryActivity objects.

        Raises:
        """
        url = self.__url('get_logged_in_athlete_activities')
        param = {'per_page': per_page, 'page': page}
        if before != None:
            param['before'] = before
        if after != None:
            param['after'] = after
        return self.__make_get_request(url, param)

    def get_zones_by_activity_id(self, id):
        """Summit Feature. Returns the zones of a given activity. Require
        activity:read for Everyone and Followers activities. Requires
        activity:read_all for Only Me activities.

        Args:
            Required Long: id // The identifier of the activity

        Returns:
            An array of ActivityZone objects.

        Raises:
        """
        url = self.__url('get_zones_by_activity_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def update_activity_by_id(self, id, updatable_activity):
        """Updates the given activity that is owned by the authenticated
        athlete. Requires activity:write. Also requires activity:read_all in
        order to update Only Me activities.

        Args:
            Required Long: id // The identifier of the activity.


        Returns:
            The activity's detailed representation. An instance of
            DetailedActivity.

        Raises:
        """
        # Put requests currently not supported
        return None

    def get_logged_in_athlete(self):
        """Returns the currently authenticated athlete. Tokens with
        profile:read_all scope will receive a detailed athlete representation;
        all others will receive a summary representation.

        Args:

        Returns:
            Profile information for the authenticated athlete. An instance of
            DetailedAthlete.

        Raises:
        """
        url = self.__url('logged_in_athlete')
        param = {}
        return self.__make_get_request(url, param)

    def get_logged_in_athlete_zones(self):
        """Returns the the authenticated athlete's heart rate and power zones.
        Requires profile:read_all.

        Args:

        Returns:
            Heart rate and power zones. An instance of Zones.

        Raises:
        """
        url = self.__url('get_logged_in_athlete_zones')
        param = {}
        return self.__make_get_request(url, param)

    def get_stats(self, id):
        """Returns the activity stats of an athlete. Only includes data from
        activities set to Everyone visibilty.

        Args:
            Reuired Long: id // The identifier of the athlete. Must match the
                                authenticated athlete.

        Returns:
            Activity stats of the athlete. An instance of ActivityStats.

        Raises:
        """
        url = self.__url('get_stats').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def update_logged_in_athlete(self, weight):
        """Update the currently authenticated athlete. Requires profile:write
        scope.

        Args:
            Required Float: weight // The weight of the athlete in kilograms.

        Returns:
            Profile information for the authenticated athlete. An instance of
            DetailedAthlete.

        Raises:
        """
        # Put requests not yet supported
        return None

    def get_club_activities_by_id(self, id, page=1, per_page=30):
        """Retrieve recent activities from members of a specific club. The
        authenticated athlete must belong to the requested club in order to hit
        this endpoint. Pagination is supported. Athlete profile visibility is
        respected for all activities.

        Args:
            Required Long: id // The identifier of the club.
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of SummaryActivity objects.

        Raises:
        """
        url = self.__url('get_club_activities_by_id').format(id)
        param = {'id': id, 'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_club_admins_by_id(self, id, page=1, per_page=30):
        """Returns a list of the administrators of a given club.

        Args:
            Required Long: id // The identifier of the club.
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of SummaryAthlete objects.

        Raises:
        """
        url = self.__url('get_club_admins_by_id').format(id)
        param = {'id': id, 'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_club_by_id(self, id):
        """Returns a given club using its identifier.

        Args:
            Required Long: id // The identifier of the club

        Returns:
            The detailed representation of a club. An instance of DetailedClub.

        Raises:
        """
        url = self.__url('get_club_by_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_club_members_by_id(self, id, page=1, per_page=30):
        """Returns a list of the athletes who are members of a given club.

        Args:
            Required Long: id // The identifier of the club.
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of SummaryAthlete objects.

        Raises:
        """
        url = self.__url('get_club_members_by_id').format(id)
        param = {'id': id, 'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_logged_in_athlete_clubs(self, page=1, per_page=30):
        """Returns a list of the clubs whose membership includes the
        authenticated athlete.

        Args:
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of SummaryClub objects.

        Raises:
        """
        url = self.__url('get_logged_in_athlete_clubs')
        param = {'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_gear_by_id(self, id):
        """Returns an equipment using its identifier.

        Args:
            Required String: id // The iden of the gear.

        Returns:
            A representation of the gear. An instance of DetailedGear.

        Raises:
        """
        url = self.__url('get_gear_by_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_route_as_gpx(self, id):
        """Returns a GPX file of the route. Requires read_all scope for private
        routes.

        Args:
            Required Long: id // The identifier of the route.

        Returns:
            A GPX file with the route.

        Raises:
        """
        url = self.__url('get_route_as_gpx').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_route_as_tcx(self, id):
        """Returns a TCX file of the route. Requires read_all scope for private
        routes.

        Args:
            Required Long: id // The identifier for the route.

        Returns:
            A TCX file with the route.

        Raises:
        """
        url = self.__url('get_route_as_tcx').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_route_by_id(self, id):
        """Returns a route using its identifier. Requires read_all scope for
        private routes.

        Args:
            Required Long: id // The identifier of the route.

        Returns:
            A representation of the route. An instance of Route.

        Raises:
        """
        url = self.__url('get_route_by_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_routes_by_athlete_id(self, id, page=1, per_page=30):
        """Returns a list of the routes created by the authenticated athlete.
        Private routes are filtered out unless requested by a token with
        read_all scope.

        Args:
            Reuired Long: id // The identifier of the athlete. Must match the
                                authenticated athlete.
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of Route objects.

        Raises:
        """
        url = self.__url('get_routes_by_athlete_id').format(id)
        param = {'id': id, 'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_running_race_by_id(self, id):
        """Returns a running race for a given identifier.

        Args:
            Required Long: id // The identifier of the running race.

        Returns:
            Representation of a running race. An instance of RunningRace.

        Raises:
        """
        url = self.__url('get_running_race_by_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_running_races(self, year=None):
        """Returns a list running races based on a set of search criteria.

        Args:
            Integer: year // Filters the list by a given year.

        Returns:
            An array of RunningRace objects.

        Raises:
        """
        url = self.__url('get_running_races')
        param = {}
        if year != None:
            param['year'] = year
        return self.__make_get_request(url, param)

    def get_efforts_by_segment_id(self, segment_id, start_date_local=None, end_date_local=None, per_page=30):
        """Returns a set of the authenticated athlete's segment efforts for a
        given segment. Requires subscription.

        Args:
            Required Integer: segment_id // The identifier of the segment.
            Date: start_date_local // ISO 8601 formatted date time.
            Date: end_date_local // ISO 8601 formatted date time.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of DetailedSegmentEffort objects.

        Raises:
        """
        url = self.__url('get_efforts_by_segment_id')
        param = {'segment_id': segment_id, 'per_page': per_page}
        if start_date_local != None:
            param['start_date_local'] = start_date_local
        if end_date_local != None:
            param['end_date_local'] = end_date_local
        return self.__make_get_request(url, param)

    def get_segment_effort_by_id(self, id):
        """Returns a segment effort from an activity that is owned by the
        authenticated athlete. Requires subscription.

        Args:
            Required Long: id // The identifier of the segment effort.

        Returns:
            Representation of a segment effort. An instance of
            DetailedSegmentEffort.

        Raises:
        """
        url = self.__url('get_segment_effort_by_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def explore_segments(self, bounds, activity_type="riding", min_cat=None, max_cat=None):
        """Returns the top 10 segments matching a specified query.

        Args:
            Required array[Float]: bounds // The latitude and longitude for two
                                            points describing a rectangular
                                            boundary for the search: [southwest
                                            corner latitutde, southwest corner
                                            longitude, northeast corner
                                            latitude, northeast corner
                                            longitude].
            String: activity_type // Desired activity type. May take one of the
                                    following values: running, riding.
            Integer: min_cat // The minimum climbing category.
            Integer: max_cat // The maximum climbing category.

        Returns:
            List of matching segments. An instance of ExplorerResponse.

        Raises:
        """
        url = self.__url('explore_segments')
        param = {'bounds': bounds, 'activity_type': activity_type}
        if min_cat != None:
            param['min_cat'] = min_cat
        if max_cat != None:
            param['max_cat'] = max_cat
        return self.__make_get_request(url, param)

    def get_logged_in_athlete_starred_segments(self, page=1, per_page=30):
        """List of the authenticated athlete's starred segments. Private
        segments are filtered out unless requested by a token with read_all
        scope.

        Args:
            Integer: page // Page number. Defaults to 1.
            Integer: per_page // Number of items per page. Defaults to 30.

        Returns:
            An array of SummarySegment objects.

        Raises:
        """
        url = self.__url('get_logged_in_athlete_starred_segments')
        param = {'page': page, 'per_page': per_page}
        return self.__make_get_request(url, param)

    def get_segment_by_id(self, id):
        """Returns the specified segment. read_all scope required in order to
        retrieve athlete-specific segment information, or to retrieve private
        segments.

        Args:
            Required Long: id // The identifier of the segment

        Returns:
            Representation of a segment. An instance of DetailedSegment.

        Raises:
        """
        url = self.__url('get_segment_by_id').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def star_segment(self, id, starred):
        """Stars/Unstars the given segment for the authenticated athlete.
        Requires profile:write scope.

        Args:
            Required Long: id // The identif of the segment.
            Required Boolean: starred // If true, star the segment; if false,
                                        unstar the segment.

        Returns:
            Representation of a segment. An instance of DetailedSegment.

        Raises:
        """
        # Put requests not yet supported
        return None

    def get_activity_streams(self, id, keys, key_by_type=True):
        """Returns the given activity's streams. Requires activity:read scope.
        Requires activity:read_all scope for Only Me activities.

        Args:
            Required Long: id // The identifier of the activity.
            Required array[String]: keys // Desired stream types. May take one
                                            of the following values:
            Required Boolean: key_by_type // Must be true.

        Returns:
            The set of requested streams. An instance of StreamSet.

        Raises:
        """
        url = self.__url('get_activity_streams').format(id)
        param = {'id': id, 'keys': keys, 'key_by_type': key_by_type}
        return self.__make_get_request(url, param)

    def get_route_streams(self, id):
        """Returns the given route's streams. Requires read_all scope for
        private routes.

        Args:
            Required Long: id // The identifier of the route.

        Returns:
            The set of requested streams. An instance of StreamSet.

        Raises:
        """
        url = self.__url('get_route_streams').format(id)
        param = {'id': id}
        return self.__make_get_request(url, param)

    def get_segment_effort_streams(self, id, keys, key_by_type=True):
        """Returns a set of streams for a segment effort completed by the
        authenticated athlete. Requires read_all scope.

        Args:
            Required Long: id // The identifier of the segment effort.
            Required array[String]: keys // Desired stream types. May take one
                                            of the following values:
            Required Boolean: key_by_type // Must be true.

        Returns:
            The set of requested streams. An instance of StreamSet.

        Raises:
        """
        url = self.__url('get_segment_effort_streams').format(id)
        param = {'id': id, 'keys': keys, 'key_by_type': key_by_type}
        return self.__make_get_request(url, param)

    def get_segment_streams(self, id, keys, key_by_type):
        """Returns the given segment's streams. Requires read_all scope for
        private segments.

        Args:
            Required Long: id // The identifier of the segment.
            Required array[String]: keys // Desired stream types. May take one
                                            of the following values:
            Required Boolean: key_by_type // Must be true.

        Returns:
            The set of requested streams. An instance of StreamSet.

        Raises:

        """
        url = self.__url('get_segment_streams').format(id)
        param = {'id': id, 'keys': keys, 'key_by_type': key_by_type}
        return self.__make_get_request(url, param)

    def create_upload(self, file, name, description, trainer, commute, data_type, external_id):
        """Uploads a new data file to create an activity from. Requires
        activity:write scope.

        Args:
            File: file // The upload file.
            String: name // The desired name of the resulting activity.
            String: description // The desired description of the resulting
                                    activity.
            String: trainer // Whether the resulting activity should be marked
                                as having been performed on a trainer.
            String: commute // Whether the resulting activity should be tagged
                                as a commute.
            String: data_type // The format of the uploaded file. May take one
                                of the following values: fit, fit.gz, tcx,
                                tcx.gz, gpx, gpx.gz
            String: external_id // The desired external identifier of the
                                    resulting activity.

        Returns:
            A representation of the created upload. An instance of Upload.

        Raises:
        """
        # Post requests not yet supported
        return None

    def get_upload_by_id(self, uploadId):
        """Returns an upload for a given identifier. Requires activity:write
        scope.

        Args:
            Required Long: uploadId // The ident of the upload.

        Returns:
            Representation of the upload. An instance of Upload.

        Raises:
        """
        url = self.__url('get_upload_by_id').format(uploadId)
        param = {'uploadId': uploadId}
        return self.__make_get_request(url, param)
