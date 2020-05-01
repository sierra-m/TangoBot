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

        # Positions of encoders
        self.position_front_left = 0
        self.position_back_left = 0
        self.position_front_right = 0
        self.position_back_right = 0

        self.left_vel = 0
        self.right_vel = 0

        self.ds_values = []

    def write_motors(self):
        self.front_left_motor.setVelocity(self.left_vel)
        self.back_left_motor.setVelocity(self.left_vel)
        self.front_right_motor.setVelocity(self.right_vel)
        self.back_right_motor.setVelocity(self.right_vel)

    def stop_motors(self):
        self.left_vel = 0
        self.right_vel = 0
        self.write_motors()

    def capture_position(self):
        # Left positions
        self.position_front_left = self.enc_front_left.getValue()
        self.position_back_left = self.enc_back_left.getValue()

        # Right positions
        self.position_front_right = self.enc_front_right.getValue()
        self.position_back_right = self.enc_back_right.getValue()

    def check_left_moved(self, distance):
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

    def check_right_moved(self, distance):
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

    def make_turn(self, left_dist, right_dist):
        self.write_motors()
        self.capture_position()
        while self.robot.step(TIME_STEP) != -1:
            left_moved = self.check_left_moved(left_dist)
            right_moved = self.check_right_moved(right_dist)

            if left_moved and right_moved:
                break

    def move_dist(self, distance):
        self.write_motors()
        self.capture_position()
        while self.robot.step(TIME_STEP) != -1:
            left_moved = self.check_left_moved(distance)
            right_moved = self.check_right_moved(distance)

            if left_moved and right_moved:
                break

    def load_distance_values(self):
        self.ds_values = []
        for ds in self.ds:
            self.ds_values.append(ds.getValue())

    def init_sensors(self):
        for i in range(0, 5):
            if self.robot.step(TIME_STEP) == -1:
                break

            for ds in self.ds:
                ds.getValue()
            self.enc_front_left.getValue()
            self.enc_front_right.getValue()
            self.enc_back_left.getValue()
            self.enc_back_right.getValue()

    def setup(self):
        print('Initializing...')
        self.init_sensors()
        self.left_vel = 3
        self.right_vel = 3
        self.write_motors()

    def mainloop(self):
        print('Running...')
        self.move_dist(8)
        self.left_vel = 3
        self.right_vel = 0.1
        self.make_turn(4.5, 0)
        self.left_vel = 1
        self.right_vel = 3.5
        self.make_turn(3, 10)
        # while self.robot.step(TIME_STEP) != -1:
        #     self.load_distance_values()
        #     print('FL: {} FR: {}'.format(self.ds_values[DS_L], self.ds_values[DS_R]))
        #
        #     if self.ds_values[DS_L] < DS_WALL_STOP and self.ds_values[DS_R] < DS_WALL_STOP:
        #         break

    def cleanup(self):
        self.stop_motors()
        print('Finished drawing.')

    def run(self):
        self.setup()
        self.mainloop()
        self.cleanup()


print('Loading robot...')
scribbles = ScribbleBot()
scribbles.run()
