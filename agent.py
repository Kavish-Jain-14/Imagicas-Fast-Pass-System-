import random  # Used for random number generation in decision-making
import numpy as np  # Used for probability distributions in behavior modeling

from behavior_reference import BEHAVIOR_ARCHETYPE_PARAMETERS  # Import predefined behavior archetypes

class Agent:
    """ 
    Class representing an agent (visitor) in the park simulation. 
    Tracks agent's state, decisions, and history of actions.
    """

    def __init__(self, random_seed):
        """ 
        Initializes the agent with a unique ID, state tracking, and behavior settings.

        Parameters:
        - random_seed (int): Seed for random number generation to ensure reproducibility.
        """

        self.agent_id = None  # Unique identifier for the agent
        self.state = {}  # Dictionary to store the agent's current state
        self.log = ""  # Text log of agent's activities for tracking behavior
        self.random_seed = random_seed  # Seed for generating random choices

        # Ensure behavior archetype probabilities add up to 1
        for behavior_type, behavior_dict in BEHAVIOR_ARCHETYPE_PARAMETERS.items():
            age_class_sum = (
                behavior_dict["percent_no_child_rides"] +
                behavior_dict["percent_no_adult_rides"] +
                behavior_dict["percent_no_preference"]
            )
            # Due to floating point precision, allow for small rounding errors (0.98 <= sum <= 1.0)
            if not 0.98 <= age_class_sum <= 1.0:
                raise AssertionError(
                    f"Behavior Archetype {behavior_type} characteristics must sum to 1."
                )

    def initialize_agent(
        self, 
        behavior_archetype_distribution, 
        exp_ability, 
        exp_wait_threshold,
        exp_limit,
        agent_id, 
        attraction_names, 
        activity_names
    ):
        """ 
        Initializes the agent's characteristics, state, and behavior.

        Parameters:
        - behavior_archetype_distribution (dict): Distribution of behavior archetypes
        - exp_ability (bool): Whether the agent can use an expedited pass
        - exp_wait_threshold (int): Maximum wait time the agent is willing to accept
        - exp_limit (int): Maximum number of expedited passes the agent can hold
        - agent_id (int): Unique identifier for the agent
        - attraction_names (list): List of all attractions in the park
        - activity_names (list): List of all activities (non-ride experiences)
        """

        self.agent_id = agent_id  # Assign unique ID to the agent

        # Initialize state variables
        self.state.update(
            {
                "arrival_time": None, 
                "exit_time": None, 
                "within_park": False,  # Whether the agent is currently in the park
                "current_location": None,  # The agent's current location (e.g., in queue, at an attraction)
                "current_action": None,  # The agent's current action (e.g., waiting, riding, eating)
                "time_spent_at_current_location": 0,
                "expedited_return_time": [],  # List of return times for expedited queue passes
                "expedited_pass": [],  # List of expedited passes the agent holds
                "expedited_pass_ability": exp_ability,  # Whether agent can get an expedited pass
                "exp_wait_threshold": exp_wait_threshold,  # Max wait time agent is willing to wait
                "exp_limit": exp_limit  # Max number of expedited passes the agent can hold
            }
        )

        # Initialize history of attractions visited
        self.state.update(
            {
                "attractions": {
                    attraction: {"times_completed": 0}  # Track how many times each attraction was visited
                    for attraction in attraction_names
                }
            }
        )

        # Initialize history of activities visited
        self.state.update(
            {
                "activities": {
                    activity: {"times_visited": 0, "time_spent": 0}  # Track visits and time spent at activities
                    for activity in activity_names
                }
            }
        )

        # Select the agent's behavior archetype based on probability distribution
        behavior_archetype = self.select_behavior_archetype(
            behavior_archetype_distribution=behavior_archetype_distribution,
            agent_id=agent_id,
        )

        # Assign age class based on selected behavior archetype
        self.state.update(
            {
                "age_class": self.select_age_class(
                    agent_id=agent_id,
                    behavior_archetype_dict=BEHAVIOR_ARCHETYPE_PARAMETERS[behavior_archetype]
                )
            }
        )

        # Ensure that an age class was assigned correctly
        if not self.state["age_class"]:
            assert True is False  # This will raise an AssertionError

        # Extract behavior parameters from the selected archetype
        parameters = BEHAVIOR_ARCHETYPE_PARAMETERS[behavior_archetype]
        rng = np.random.default_rng(self.random_seed + self.agent_id)
        stay_time_preference = int(
            max((rng.normal(parameters["stay_time_preference"], parameters["stay_time_preference"] / 4, 1))[0], 0)
        )

        # Store behavior traits in the agent
        self.behavior = {
            "archetype": behavior_archetype,  # The assigned behavior archetype
            "stay_time_preference": stay_time_preference,  # Preferred park visit duration
            "allow_repeats": parameters["allow_repeats"],  # Whether agent revisits attractions
            "attraction_preference": parameters["attraction_preference"],  # Probability of choosing attractions over activities
            "wait_threshold": parameters["wait_threshold"],  # Max wait time the agent is willing to tolerate
        }

    def select_behavior_archetype(self, agent_id, behavior_archetype_distribution):
        """ Selects a behavior archetype based on probability distribution. """
        rng = random.uniform(0, sum(behavior_archetype_distribution.values()))
        floor = 0.0
        for behavior_archetype, behavior_archetype_weight in behavior_archetype_distribution.items():
            floor += behavior_archetype_weight
            if rng < floor: 
                return behavior_archetype
    
    def select_age_class(self, agent_id, behavior_archetype_dict):
        """ Selects an age class based on behavior archetype settings. """
        age_class_distribution = {
            "no_child_rides": behavior_archetype_dict["percent_no_child_rides"],
            "no_adult_rides": behavior_archetype_dict["percent_no_adult_rides"],
            "no_preference": behavior_archetype_dict["percent_no_preference"]
        }
        rng = random.uniform(0, sum(age_class_distribution.values()))
        floor = 0.0
        for age_class, age_class_weight in age_class_distribution.items():
            floor += age_class_weight
            if rng < floor: 
                return age_class

    def arrive_at_park(self, time):
        """ Updates the agent state and log when they arrive at the park. """
        self.state["within_park"] = True
        self.state["arrival_time"] = time
        self.state["current_location"] = "gate"
        self.state["current_action"] = "idling"
        self.state["time_spent_at_current_location"] = 0
        self.log += f"Agent arrived at park at time {time}. "

    def decide_to_leave_park(self, time):
        """ Determines whether the agent should leave the park. """
        action, location = None, None
        if time != self.state["arrival_time"]:
            actual_preference_value = (time - self.state["arrival_time"]) - self.behavior["stay_time_preference"]           
            rng = np.random.default_rng(self.random_seed+self.agent_id+time)
            normal_coinflip = (rng.normal(0, 1, 1) * 60)[0]
            if actual_preference_value > normal_coinflip:
                action = "leaving"
                location = "gate"
        return action, location

    def pass_time(self):
        """ Advances time for the agent by one unit (1 minute). """
        if self.state["within_park"]:
            self.state["time_spent_at_current_location"] += 1
            if self.state["expedited_pass"]:
                self.state["expedited_return_time"] = [val - 1 for val in self.state["expedited_return_time"]]
