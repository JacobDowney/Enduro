import enduro
import helper
import consts
from tabulate import tabulate

def main():


    #enduro.update_activity_jsons(strava_info)
    # print(enduro.tabulate_enduro_attempts('anderson'))
    # act = helper.read_json(consts.mtb_ride_activities_json)
    # for k in act:
    #     print(k, act[k])
    #     break
    # print(len(act.keys()))


    acts = helper.read_json(consts.mtb_ride_activities_json)
    for act in acts:
        print(act)
        a = acts[act]
        print(type(a['id']))   int->str
        print(type(a['distance'])) float ->int
        print(type(a['total_elevation_gain'])) float->int
        print(type(a['max_speed'])) float->int
        print(type(a['calories']))  float->int
        break
#
# self.id = str(activity.get('id', ''))
# self.name = str(activity.get('', ''))
# self.description = str(activity.get('', ''))
# self.device_name = str(activity.get('', ''))
# self.distance = int(activity.get('', 0))
# self.elapsed_time = int(activity.get('', 0))
# self.total_elevation_gain = int(activity.get('', 0))
# self.kudos_count = int(activity.get('', 0))
# self.max_speed = int(activity.get('', 0))
# self.calories = int(activity.get('', 0))
# self.photos = activity.get('', None)
# self.gear = activity.get('', None)

    # enduros = helper.read_json(consts.mtb_ride_activities_json)
    #
    # teds = []
    # for enduro in enduros:
    #     for segment in enduros[enduro]['segment_efforts']:
    #         if segment['name'] == 'Berms DH':
    #             teds.append(enduros[enduro])
    #             break
    #
    # rides = {}
    # for ted in teds:
    #     runs = {
    #         'Berms DH':                 0,
    #         'I otter\'d on Yo Face':    0,
    #         'Tech Rocks to Park Berms': 0,
    #         'Bowel Movement':           0,
    #         'DH to Meadowbrook':        0
    #     }
    #     for segment in ted['segment_efforts']:
    #         name = segment['name']
    #         if name in runs and (runs[name] == 0 or runs[name] > segment['elapsed_time']):
    #             runs[name] = segment['elapsed_time']
    #     rides[ted['id']] = {
    #         'name': ted['name'],
    #         'distance': ted['distance'],
    #         'elevation_gain': ted['total_elevation_gain'],
    #         'runs': runs
    #     }
    #
    # # Used to transform seconds integer into min:sec strign
    # def __to_min_sec_str(__time):
    #     __min = str(int(__time / 60))
    #     __sec = str(__time % 60)
    #     return '{}:{}'.format(__min, __sec.zfill(2))
    # data = []
    # for id in rides:
    #     ride = rides[id]
    #     distance = '{} miles'.format(str(round(int(ride['distance']) * 0.000621371, 2)))
    #     elevation_gain = '{} feet'.format(str(int(int(ride['elevation_gain']) * 3.28084)))
    #     sub_data = [ride['name'], distance, elevation_gain]
    #     for name in ride['runs']:
    #         sub_data.append(__to_min_sec_str(ride['runs'][name]))
    #     data.append(sub_data)
    # # Sets up the headers for each of the stages
    # header = ['NAME', 'DISTANCE', 'ELEVATION']
    # for id in rides:
    #     for name in rides[id]['runs']:
    #         header.append(name)
    #     break
    # tab = tabulate(data, headers=header)
    # print(tab)


if __name__ == "__main__":
    main()





# class EnduroAttempt():
#     def __init__(self, activity, segment_attempts):
#         self.id = str(activity.get('id', ''))
#         self.name = str(activity.get('name', ''))
#         self.description = str(activity.get('description', ''))
#         self.device_name = str(activity.get('device_name', ''))
#         self.distance = int(activity.get('distance', 0))
#         self.elapsed_time = int(activity.get('elapsed_time', 0))
#         self.total_elevation_gain = int(activity.get('total_elevation_gain', 0))
#         self.kudos_count = int(activity.get('kudos_count', 0))
#         self.max_speed = int(activity.get('max_speed', 0))
#         self.calories = int(activity.get('calories', 0))
#         self.photos = activity.get('photos', None)
#         self.gear = activity.get('gear', None)
#         self.segment_attempts = segment_attempts
#         self.enduro_time = sum(attempt.elapsed_time for attempt in segment_attempts)
#     def __str__(self):
#         return(f"{self.id}: {helper.to_min_sec_str(self.enduro_time)} - {self.name}")
#
# class SegmentAttempt():
#     def __init__(self, segment_effort):
#         if 'segment' not in segment_effort:
#             raise Exception('segment must be a key in segment effort')
#         # TODO(downeyj): implement effort id
#         # self.effort_id = str(segment_effort.get('id', ''))
#         # Segment information
#         self.segment_id = str(segment_effort['segment'].get('id', ''))
#         self.name = str(segment_effort['segment'].get('name', ''))
#         self.distance = int(segment_effort['segment'].get('distance', 0))
#         # Segment effort information
#         self.elapsed_time = int(segment_effort.get('elapsed_time', 0))
#         self.average_watts = int(segment_effort.get('average_watts', 0))
#         self.average_heartrate = int(segment_effort.get('average_heartrate', 0))
#         self.max_heartrate = int(segment_effort.get('max_heartrate', 0))
#     def __str__(self):
#         return(f"{self.segment_id}: {helper.to_min_sec_str(self.elapsed_time)} - {self.name}")
