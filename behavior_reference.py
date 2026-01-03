# This file defines behavior archetypes for agents (park visitors) in a theme park simulation.
# Each archetype represents a different type of visitor behavior.

# Parameters:
#   stay_time_preference: The average total time (in minutes) that the agent wants to stay in the park.
#                         This value is drawn from a normal distribution.
#   allow_repeats: Determines whether an agent is willing to revisit the same attraction.
#   attraction_preference: A value between 0 and 1. Higher values mean the agent prefers attractions over activities.
#   wait_threshold: The maximum number of minutes the agent is willing to wait in a queue.
#                   If a queue exceeds this wait time, the agent will seek an expedited pass.
#   percent_no_child_rides: The proportion of agents in this archetype who do not go on child rides.
#   percent_no_adult_rides: The proportion of agents in this archetype who do not go on adult rides.
#   percent_no_preference: The proportion of agents in this archetype with no ride preference.

BEHAVIOR_ARCHETYPE_PARAMETERS = {
    # Ride Enthusiast:
    # - Stays in the park for a long time (540 minutes).
    # - Focuses mainly on attractions and does not visit activities.
    # - Has no issue with waiting in long queues.
    "ride_enthusiast": {
        "stay_time_preference": 540,
        "allow_repeats": True,
        "attraction_preference": 0.6,  # Strong preference for attractions.
        "wait_threshold": 480,  # Willing to wait up to 8 hours in queues.
        "percent_no_child_rides": 0.0,  # Can go on child rides.
        "percent_no_adult_rides": 1.0,  # Prefers adult rides.
        "percent_no_preference": 0.0  # No general preference.
    },

    # Ride Favorer:
    # - Similar to Ride Enthusiast but occasionally visits activities.
    # - Still highly attraction-focused.
    "ride_favorer": {
        "stay_time_preference": 480,  # Stays in the park for 8 hours.
        "allow_repeats": True,
        "attraction_preference": 0.5,  # Still prefers attractions, but less than Ride Enthusiast.
        "wait_threshold": 420,  # Will wait for up to 7 hours.
        "percent_no_child_rides": 0.0,
        "percent_no_adult_rides": 1.0,
        "percent_no_preference": 0.0
    },

    # Park Tourer:
    # - Stays in the park for a long time (7 hours).
    # - Equally enjoys attractions and activities.
    # - Has a reasonable tolerance for wait times.
    "park_tourer": {
        "stay_time_preference": 420,
        "allow_repeats": False,  # Does not revisit attractions.
        "attraction_preference": 0.4,  # Balanced preference between attractions and activities.
        "wait_threshold": 360,  # Will wait up to 6 hours in a queue.
        "percent_no_child_rides": 0.0,
        "percent_no_adult_rides": 1.0,
        "percent_no_preference": 0.0
    },

    # Park Visitor:
    # - Spends less time in the park (6 hours).
    # - Likes attractions and activities equally.
    # - Impatient about long wait times.
    "park_visitor": {
        "stay_time_preference": 360,  # Stays in the park for 6 hours.
        "allow_repeats": False,
        "attraction_preference": 0.3,  # Prefers attractions slightly more than activities.
        "wait_threshold": 240,  # Will wait only up to 4 hours.
        "percent_no_child_rides": 0.0,
        "percent_no_adult_rides": 1.0,
        "percent_no_preference": 0.0
    },

    # Activity Favorer:
    # - Spends about 5 hours in the park.
    # - Prefers activities over attractions.
    # - Has a moderate tolerance for waiting in lines.
    "activity_favorer": {
        "stay_time_preference": 300,
        "allow_repeats": False,
        "attraction_preference": 0.2,  # Prefers activities more than attractions.
        "wait_threshold": 180,  # Will wait up to 3 hours in queues.
        "percent_no_child_rides": 0.0,
        "percent_no_adult_rides": 1.0,
        "percent_no_preference": 0.0
    },

    # Activity Enthusiast:
    # - Spends only 4 hours in the park.
    # - Primarily visits activities and ignores most attractions.
    # - Has a low tolerance for waiting in queues.
    "activity_enthusiast": {
        "stay_time_preference": 240,  # Stays in the park for 4 hours.
        "allow_repeats": False,
        "attraction_preference": 0.2,  # Strong preference for activities over attractions.
        "wait_threshold": 90,  # Will wait only up to 1.5 hours.
        "percent_no_child_rides": 0.0,
        "percent_no_adult_rides": 1.0,
        "percent_no_preference": 0.0
    },
}
