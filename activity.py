import numpy as np

class Activity:
    """ 
    Class that defines an Activity within the park simulation.
    This class stores activity characteristics, tracks visitors, 
    and maintains a log of historical data.
    """

    def __init__(self, activity_characteristics, random_seed=None):
        """  
        Initializes an activity with given characteristics.

        Parameters:
            activity_characteristics (dict): A dictionary containing attributes like 
                                             name, popularity, and mean time spent.
            random_seed (int, optional): A seed for random number generation 
                                         to ensure reproducibility in simulation.
        """

        self.activity_characteristics = activity_characteristics  # Store input characteristics
        self.state = {}  # Tracks the current state of the activity (e.g., visitors inside)
        self.history = {}  # Stores historical visitor counts over time
        self.random_seed = random_seed  # Random seed for reproducible behavior

        # Validate that popularity is an integer between 0 and 10
        if (
            type(self.activity_characteristics["popularity"]) != int 
            or self.activity_characteristics["popularity"] < 0
            or self.activity_characteristics["popularity"] > 10
        ):
            raise AssertionError(
                f"Activity {self.activity_characteristics['name']} 'popularity' value must be an integer between"
                " 0 and 10"
            )

        # Set up the activity
        self.initialize_activity()

    
    def initialize_activity(self):
        """ 
        Sets up the activity by defining its attributes and initializing 
        its state and history tracking.
        """

        # Extract basic characteristics from the input dictionary
        self.name = self.activity_characteristics["name"]  # Activity name
        self.popularity = self.activity_characteristics["popularity"]  # Popularity score (0-10)
        self.mean_time = self.activity_characteristics["mean_time"]  # Average time spent by a visitor

        # State variables to track visitors and their remaining time
        self.state["visitors"] = []  # List of visitor IDs currently in the activity
        self.state["visitor_time_remaining"] = []  # List of time left for each visitor

        # History dictionary to store visitor counts over time
        self.history["total_vistors"] = {}  # Tracks the total number of visitors per time unit
           

    def add_to_activity(self, agent_id, expedited_return_time):
        """ 
        Adds a visitor (agent) to the activity and determines how long they will stay.

        Parameters:
            agent_id (int): The unique ID of the visitor.
            expedited_return_time (int or None): If the visitor has a fast-track reservation, 
                                                 they must leave the activity before their ride time.
        """

        # Add the visitor to the list of current visitors
        self.state["visitors"].append(agent_id)

        # Generate a random stay duration using a normal distribution
        if self.random_seed:
            rng = np.random.default_rng(self.random_seed + agent_id)  # Use a reproducible random seed
            stay_time = int(
                max((rng.normal(self.mean_time, self.mean_time / 2, 1))[0], 1)
            )  # Ensure the stay time is at least 1
        else:
            stay_time = int(
                max((np.random.normal(self.mean_time, self.mean_time / 2, 1))[0], 1)
            )  # Sample from a normal distribution with mean `mean_time`

        # If the visitor has an expedited queue reservation, make them leave earlier
        if expedited_return_time:
            stay_time = min(max(1, expedited_return_time), stay_time)
        
        # Store the visitor's remaining time in the activity
        self.state["visitor_time_remaining"].append(stay_time)

    def force_exit(self, agent_id):
        """ 
        Forces a visitor to leave the activity (e.g., if their reserved ride time is ready).
        
        Parameters:
            agent_id (int): The unique ID of the visitor being removed.
        """

        # Find the index of the visitor in the list
        ind = self.state["visitors"].index(agent_id)
        
        # Remove the visitor and their remaining time
        del self.state["visitors"][ind]
        del self.state["visitor_time_remaining"][ind]

    def step(self, time):
        """ 
        Simulates the passing of time and removes visitors who have completed their stay.
        
        Parameters:
            time (int): The current simulation time.

        Returns:
            list: A list of visitor IDs who have exited the activity.
        """

        # Identify visitors who have completed their stay (remaining time = 0)
        exiting_agents = [
            (ind, agent_id) for ind, agent_id in enumerate(self.state["visitors"])
            if self.state["visitor_time_remaining"][ind] == 0
        ]

        # Reverse the list to ensure indices remain valid while removing elements
        exiting_agents.reverse()
        for ind, agent_id in exiting_agents:
            del self.state["visitors"][ind]
            del self.state["visitor_time_remaining"][ind]

        # Return the list of visitor IDs who have left
        return [agent_id for ind, agent_id in exiting_agents]

    def pass_time(self):
        """ 
        Advances time by one unit, reducing the remaining time for all visitors.
        """

        # Decrease the remaining time for each visitor by 1
        self.state["visitor_time_remaining"] = [
            visitor_time - 1 for visitor_time in self.state["visitor_time_remaining"]
        ]

    def store_history(self, time):
        """ 
        Records the number of visitors in the activity at a given time.

        Parameters:
            time (int): The current simulation time.
        """

        # Update the history log with the current visitor count
        self.history["total_vistors"][time] = len(self.state["visitors"])
