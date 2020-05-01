from controller import Robot

TIME_STEP = 64

DS_L = 0
DS_R = 1

DS_WALL_STOP = 400


class ScribbleBot:
    def __init__(self):
        self.robot = Robot()

        # Define and enable distance sensors
        self.ds = [self.robot.getDistanceSensor(name) for name in ['ds_left', 'ds_right']]
        for sensor in self.ds:
            sensor.enable(TIME_STEP)

        # Define motors
        self.front_left_motor = self.robot.getMotor('wheel1')
        self.front_right_motor = self.robot.getMotor('wheel2')
        self.back_left_motor = self.robot.getMotor('wheel3')
        self.back_right_motor = self.robot.getMotor('wheel4')

        # Group motors for easy access
        self.motors = [
            self.front_left_motor,
            self.front_right_motor,
            self.back_left_motor,
            self.back_right_motor
        ]

        # Enable motors
        for motor in self.motors:
            motor.setPosition(float('inf'))
            motor.setVelocity(0.0)

        # Define encoders
        self.enc_front_left = self.robot.getPositionSensor('front left position')
        self.enc_front_right = self.robot.getPositionSensor('front right position')
        self.enc_back_left = self.robot.getPositionSensor('back left position')
        self.enc_back_right = self.robot.getPositionSensor('back right position')

        # Enable encoders
        self.enc_front_left.enable(TIME_STEP)
        self.enc_front_right.enable(TIME_STEP)
        self.enc_back_left.enable(TIME_STEP)
        self.enc_back_right.enable(TIME_STEP)

        # Line generator
        self.pen = self.robot.getPen('pen')
        self.pen.write(True)

        # Positions of encoders
        self.position_front_left = 0
        self.position_back_left = 0
        self.position_front_right = 0
        self.position_back_right = 0

        # Internal velocities, one per side
        self.left_vel = 0
        self.right_vel = 0

        # List for distance sensor values
        self.ds_values = []

    def write_motors(self):
        """Write the current velocities into motor objects"""
        self.front_left_motor.setVelocity(self.left_vel)
        self.back_left_motor.setVelocity(self.left_vel)
        self.front_right_motor.setVelocity(self.right_vel)
        self.back_right_motor.setVelocity(self.right_vel)

    def stop_motors(self):
        """Helper util to stop motors"""
        self.left_vel = 0
        self.right_vel = 0
        self.write_motors()

    def capture_position(self):
        """Capture current encoder values in position variables"""
        # Left positions
        self.position_front_left = self.enc_front_left.getValue()
        self.position_back_left = self.enc_back_left.getValue()

        # Right positions
        self.position_front_right = self.enc_front_right.getValue()
        self.position_back_right = self.enc_back_right.getValue()

    def check_left_moved(self, distance: float) -> bool:
        """
        Manages a left side distance move. If either motor has achieved
        distance required, it is manually stopped. If both have, function
        returns `True`
        """
        front_moved = abs(self.enc_front_left.getValue() - self.position_front_left) > distance
        back_moved = abs(self.enc_back_left.getValue() - self.position_back_left) > distance

        if front_moved:
            self.front_left_motor.setVelocity(0)

        if back_moved:
            self.back_left_motor.setVelocity(0)

        both = front_moved and back_moved

        if both:
            self.left_vel = 0

        return both

    def check_right_moved(self, distance: float) -> bool:
        """
        Manages a right side distance move. If either motor has achieved
        distance required, it is manually stopped. If both have, function
        returns `True`
        """
        front_moved = abs(self.enc_front_right.getValue() - self.position_front_right) > distance
        back_moved = abs(self.enc_back_right.getValue() - self.position_back_right) > distance

        if front_moved:
            self.front_right_motor.setVelocity(0)

        if back_moved:
            self.back_right_motor.setVelocity(0)

        both = front_moved and back_moved

        if both:
            self.right_vel = 0

        return both

    def make_turn(self, left_dist: float, right_dist: float):
        """
        Makes a turn based on velocities and encoder positions. Blocking.

        Velocities must be set outside function call. Each wheel is moved
        to corresponding side distance and stopped
        """
        self.write_motors()
        self.capture_position()
        while self.robot.step(TIME_STEP) != -1:
            left_moved = self.check_left_moved(left_dist)
            right_moved = self.check_right_moved(right_dist)

            if left_moved and right_moved:
                break

    def make_left_turn(self, distance: float):
        """
        Make a left turn by a distance. Blocking.

        Velocities must be set outside function call. `distance`
        pertains to right wheel, left wheel distance is calculated from this
        and velocity ratio for perfect arcing turn
        """
        ratio = self.left_vel / self.right_vel
        self.make_turn(ratio * distance, distance)

    def make_right_turn(self, distance: float):
        """
        Make a right turn by a distance. Blocking.

        Velocities must be set outside function call. `distance`
        pertains to left wheel, right wheel distance is calculated from this
        and velocity ratio for perfect arcing turn
        """
        ratio = self.right_vel / self.left_vel
        self.make_turn(distance, ratio * distance)

    def move_dist(self, distance: float):
        """
        Move a distance forward. Blocking.

        Velocities must be set outside function call
        """
        self.write_motors()
        self.capture_position()
        while self.robot.step(TIME_STEP) != -1:
            left_moved = self.check_left_moved(distance)
            right_moved = self.check_right_moved(distance)

            if left_moved and right_moved:
                break

    def load_distance_values(self):
        """Load current distance values from `self.ds` into `self.ds_values`"""
        self.ds_values = []
        for ds in self.ds:
            self.ds_values.append(ds.getValue())

    def init_sensors(self):
        """Initialize sensors to avoid error values like NaN"""
        for i in range(0, 5):
            if self.robot.step(TIME_STEP) == -1:
                break

            for ds in self.ds:
                ds.getValue()
            self.enc_front_left.getValue()
            self.enc_front_right.getValue()
            self.enc_back_left.getValue()
            self.enc_back_right.getValue()

    def do_the_wave(self):
        """Do the waaaaave"""
        # Entry turn to the right
        self.left_vel = 3
        self.right_vel = 0.1
        self.make_right_turn(6)

        # Arcing main turn to the left
        self.left_vel = 1
        self.right_vel = 3.5
        self.make_left_turn(15.8)

        # Exiting turn to the right
        self.left_vel = 3
        self.right_vel = 0.5
        self.make_right_turn(4.5)

        # Aligning turn to the right, slow and precise
        self.left_vel = 1
        self.right_vel = 0.2
        self.make_right_turn(1.94)

    def search_for_wall(self):
        """Drive forward until wall is found"""
        print('Finding end wall...')
        self.left_vel = 3
        self.right_vel = 3
        self.write_motors()
        while self.robot.step(TIME_STEP) != -1:
            self.load_distance_values()
            # print('FL: {} FR: {}'.format(self.ds_values[DS_L], self.ds_values[DS_R]))

            if self.ds_values[DS_L] < DS_WALL_STOP and self.ds_values[DS_R] < DS_WALL_STOP:
                break

    def setup(self):
        """Pre-movement initializations. Runs once"""
        print('Initializing...')
        self.init_sensors()
        self.left_vel = 3
        self.right_vel = 3
        self.write_motors()

    def main(self):
        """Main code. Usually a loop or series of loops"""
        print('Running...')
        self.move_dist(7)

        for i in range(4):
            self.do_the_wave()

        self.search_for_wall()

    def cleanup(self):
        """Post-movement finishing code"""
        self.stop_motors()
        print('Finished drawing.')

    def run(self):
        """Primary running method"""
        self.setup()
        self.main()
        self.cleanup()


print('Loading robot...')
scribbles = ScribbleBot()
scribbles.run()
