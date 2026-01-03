class Attraction:
    """ 
    Class representing an attraction in the theme park simulation.
    It stores attraction characteristics, manages visitor queues, 
    and tracks operational history.
    """

    def __init__(self, attraction_characteristics):
        """  
        Initializes the attraction with given characteristics.

        Parameters:
        - attraction_characteristics (dict): A dictionary containing 
                                             details about the attraction.
        """

        self.attraction_characteristics = attraction_characteristics  # Store attraction details
        self.state = {}  # Holds current queue and ride state
        self.history = {}  # Stores historical data like queue length over time

        # Validate that popularity is an integer between 1 and 10
        if (
            type(self.attraction_characteristics["popularity"]) != int 
            or self.attraction_characteristics["popularity"] < 1
            or self.attraction_characteristics["popularity"] > 10
        ):
            raise AssertionError(
                f"Attraction {self.attraction_characteristics['name']} 'popularity' value must be an integer between 1 and 10"
            )

        # Initialize the attraction’s state and parameters
        self.initialize_attraction()

    def initialize_attraction(self):
        """ 
        Sets up the attraction’s state, capacity, and queue system.
        """

        # Extract characteristics from input dictionary
        self.name = self.attraction_characteristics["name"]
        self.run_time = self.attraction_characteristics["run_time"]  # Duration of one ride cycle
        self.capacity = self.attraction_characteristics["hourly_throughput"] * (self.run_time / 60)  # Max visitors per cycle
        self.popularity = self.attraction_characteristics["popularity"]  # Popularity score (1-10)
        self.child_eligible = self.attraction_characteristics["child_eligible"]  # Can children ride?
        self.adult_eligible = self.attraction_characteristics["adult_eligible"]  # Can adults ride?
        self.run_time_remaining = 0  # Countdown timer for current ride cycle
        self.expedited_queue = self.attraction_characteristics["expedited_queue"]  # Fast-pass enabled?
        self.exp_queue_ratio = self.attraction_characteristics["expedited_queue_ratio"]  # Proportion of seats for fast-pass users
        self.exp_queue_passes = 0  # Number of available fast passes

        # Initialize queue states
        self.state["agents_in_attraction"] = []  # List of visitors currently on the ride
        self.state["queue"] = []  # List of visitors in the regular queue
        self.state["exp_queue"] = []  # List of visitors in the expedited queue
        self.state["exp_queue_passes_distributed"] = 0  # Track how many passes have been given out

        # Initialize history tracking
        self.history["queue_length"] = {}
        self.history["queue_wait_time"] = {}
        self.history["exp_queue_length"] = {}
        self.history["exp_queue_wait_time"] = {}

    def get_wait_time(self):
        """ 
        Calculates and returns the expected wait time for regular queue.
        """

        if self.expedited_queue:
            queue_len = len(self.state["queue"])
            exp_queue_len = len(self.state["exp_queue"])
            exp_seats = int(self.capacity * self.exp_queue_ratio)
            standby_seats = self.capacity - exp_seats

            runs = 0
            while queue_len >= self.capacity:
                if exp_queue_len > exp_seats:
                    exp_queue_len -= exp_seats
                    if queue_len > standby_seats:
                        queue_len -= standby_seats
                    else:
                        queue_len = 0
                else:
                    queue_len -= self.capacity - exp_queue_len
                    exp_queue_len = 0

                runs += 1

            return runs * self.run_time + self.run_time_remaining
        else:
            return (len(self.state["queue"]) // self.capacity) * self.run_time + self.run_time_remaining

    def get_exp_wait_time(self):
        """ 
        Calculates and returns the expected wait time for the expedited queue.
        """

        if self.expedited_queue:
            queue_len = len(self.state["queue"])
            exp_queue_len = len(self.state["exp_queue"])
            exp_seats = int(self.capacity * self.exp_queue_ratio)
            standby_seats = self.capacity - exp_seats

            runs = 0
            while exp_queue_len >= self.capacity:
                if exp_queue_len > exp_seats:
                    exp_queue_len -= exp_seats
                    if queue_len > standby_seats:
                        queue_len -= standby_seats
                    else:
                        queue_len = 0
                else:
                    queue_len -= self.capacity - exp_queue_len
                    exp_queue_len = 0

                runs += 1

            return runs * self.run_time + self.run_time_remaining
        else:
            return 0

    def add_to_queue(self, agent_id):
        """ 
        Adds an agent (visitor) to the regular queue.
        """
        self.state["queue"].append(agent_id)

    def add_to_exp_queue(self, agent_id):
        """ 
        Adds an agent (visitor) to the expedited queue and returns their estimated wait time.
        """
        self.state["exp_queue"].append(agent_id)
        expedited_wait_time = self.get_exp_wait_time()
        return expedited_wait_time

    def remove_pass(self):
        """ 
        Removes an expedited pass when it is redeemed.
        """
        self.exp_queue_passes -= 1
        self.state["exp_queue_passes_distributed"] += 1

    def return_pass(self, agent_id):
        """ 
        Cancels an expedited pass (if the visitor leaves the park before using it).
        """
        self.exp_queue_passes += 1
        self.state["exp_queue_passes_distributed"] -= 1
        self.state["exp_queue"].remove(agent_id)

    def step(self, time, park_close):
        """ 
        Handles ride operations:
        - Unloads visitors after ride cycle completion.
        - Loads visitors from the expedited and regular queue.
        - Begins the ride.
        """

        exiting_agents = []
        loaded_agents = []

        # Adjust fast-pass availability as the park closes
        if self.expedited_queue:
            if time < park_close:
                remaining_operating_hours = (park_close - time) // 60
                passed_operating_hours = time // 60
                self.exp_queue_passes = (
                    (self.capacity * (60 / self.run_time) * self.exp_queue_ratio * remaining_operating_hours) 
                    - max(
                        (
                            self.state["exp_queue_passes_distributed"] - 
                            (self.capacity * (60 / self.run_time) * self.exp_queue_ratio * passed_operating_hours)
                        ), 
                        0
                    )
                )
            else:
                self.exp_queue_passes = 0 

        if self.run_time_remaining == 0:
            # Unload previous riders
            exiting_agents = self.state["agents_in_attraction"]
            self.state["agents_in_attraction"] = []
            self.run_time_remaining = self.run_time

            # Assign available seats between expedited and regular queues
            max_exp_queue_agents = int(self.capacity * self.exp_queue_ratio)
            max_queue_agents = max(self.capacity - len(self.state["exp_queue"]), 0)

            # Load expedited queue riders first
            expedited_agents_to_load = self.state["exp_queue"][:max_exp_queue_agents]
            self.state["agents_in_attraction"] = expedited_agents_to_load
            self.state["exp_queue"] = self.state["exp_queue"][max_exp_queue_agents:]

            # Load regular queue riders
            agents_to_load = self.state["queue"][:max_queue_agents]
            self.state["agents_in_attraction"].extend(agents_to_load)
            self.state["queue"] = self.state["queue"][max_queue_agents:]

            loaded_agents = self.state["agents_in_attraction"]
        
        return exiting_agents, loaded_agents

    def pass_time(self):
        """ 
        Advances the ride timer by one minute.
        """
        self.run_time_remaining -= 1

    def store_history(self, time):
        """ 
        Records queue lengths and wait times for analysis.
        """
        self.history["queue_length"][time] = len(self.state["queue"])
        self.history["queue_wait_time"][time] = self.get_wait_time()
        self.history["exp_queue_length"][time] = len(self.state["exp_queue"])
        self.history["exp_queue_wait_time"][time] = self.get_exp_wait_time()
