from pyniryo import NiryoRobot  # Niryo's Python Package
import Tkinter as Tk

simulation_mode = True

DEFAULT_XYZ_STEP = 0.01
DEFAULT_RPY_STEP = 0.1
DEFAULT_JOINT_STEP = 0.1

# Set robot address
robot_ip_address_rpi = "10.10.10.10"
robot_ip_address_simulation = "127.0.0.1"
robot_ip_address = robot_ip_address_simulation if simulation_mode else robot_ip_address_rpi


class TkinterController(Tk.Tk):
    def __init__(self, niyro_robot):
        Tk.Tk.__init__(self)
        self.niyro_robot = niyro_robot
        self.niyro_robot.update_tool()

        self.xyz_step = DEFAULT_XYZ_STEP
        self.rpy_step = DEFAULT_RPY_STEP
        self.joint_step = DEFAULT_JOINT_STEP

        self.button_x_plus = Tk.Button(self, text="X+", command=self.x_plus).grid(row=0, column=0)
        self.button_x_minus = Tk.Button(self, text="X-", command=self.x_minus).grid(row=0, column=1)

        self.button_y_plus = Tk.Button(self, text="Y+", command=self.y_plus).grid(row=1, column=0)
        self.button_y_minus = Tk.Button(self, text="Y-", command=self.y_minus).grid(row=1, column=1)

        self.button_z_plus = Tk.Button(self, text="Z+", command=self.z_plus).grid(row=2, column=0)
        self.button_z_minus = Tk.Button(self, text="Z-", command=self.z_minus).grid(row=2, column=1)

        self.button_roll_plus = Tk.Button(self, text="roll+", command=self.roll_plus).grid(row=3, column=0)
        self.button_roll_minus = Tk.Button(self, text="roll-", command=self.roll_minus).grid(row=3, column=1)

        self.button_pitch_plus = Tk.Button(self, text="pitch+", command=self.pitch_plus).grid(row=4, column=0)
        self.button_pitch_minus = Tk.Button(self, text="pitch-", command=self.pitch_minus).grid(row=4, column=1)

        self.button_yaw_plus = Tk.Button(self, text="yaw+", command=self.yaw_plus).grid(row=5, column=0)
        self.button_yaw_minus = Tk.Button(self, text="yaw-", command=self.yaw_minus).grid(row=5, column=1)

        self.button_j1_plus = Tk.Button(self, text="j1+", command=self.j1_plus).grid(row=0, column=2)
        self.button_j1_minus = Tk.Button(self, text="j1-", command=self.j1_minus).grid(row=0, column=3)

        self.button_j2_plus = Tk.Button(self, text="j2+", command=self.j2_plus).grid(row=1, column=2)
        self.button_j2_minus = Tk.Button(self, text="j2-", command=self.j2_minus).grid(row=1, column=3)

        self.button_j3_plus = Tk.Button(self, text="j3+", command=self.j3_plus).grid(row=2, column=2)
        self.button_j3_minus = Tk.Button(self, text="j3-", command=self.j3_minus).grid(row=2, column=3)

        self.button_j4_plus = Tk.Button(self, text="j4+", command=self.j4_plus).grid(row=3, column=2)
        self.button_j4_minus = Tk.Button(self, text="j4-", command=self.j4_minus).grid(row=3, column=3)

        self.button_j5_plus = Tk.Button(self, text="j5+", command=self.j5_plus).grid(row=4, column=2)
        self.button_j5_minus = Tk.Button(self, text="j5-", command=self.j5_minus).grid(row=4, column=3)

        self.button_j6_plus = Tk.Button(self, text="j6+", command=self.j6_plus).grid(row=5, column=2)
        self.button_j6_minus = Tk.Button(self, text="j6-", command=self.j6_minus).grid(row=5, column=3)

        # Buttons Action
        self.button_reset = Tk.Button(self, text="Open", command=self.open_gripper).grid(row=6, column=0)
        self.button_quitter = Tk.Button(self, text="Close", command=self.close_gripper).grid(row=6, column=1)
        self.button_reset = Tk.Button(self, text="Reset", command=self.reset).grid(row=6, column=2)
        self.button_quitter = Tk.Button(self, text="Quitter", command=self.quit).grid(row=6, column=3)

        self.mainloop()

    def x_plus(self):
        self.niyro_robot.jog_pose(self.xyz_step, 0.0, 0.0, 0.0, 0.0, 0.0)

    def x_minus(self):
        self.niyro_robot.jog_pose(-self.xyz_step, 0.0, 0.0, 0.0, 0.0, 0.0)

    def y_plus(self):
        self.niyro_robot.jog_pose(0.0, self.xyz_step, 0.0, 0.0, 0.0, 0.0)

    def y_minus(self):
        self.niyro_robot.jog_pose(0.0, -self.xyz_step, 0.0, 0.0, 0.0, 0.0)

    def z_plus(self):
        self.niyro_robot.jog_pose(0.0, 0.00, self.xyz_step, 0.0, 0.0, 0.0)

    def z_minus(self):
        self.niyro_robot.jog_pose(0.0, 0.0, -self.xyz_step, 0.0, 0.0, 0.0)

    def roll_plus(self):
        self.niyro_robot.jog_pose(0.0, 0.0, 0.0, self.rpy_step, 0.0, 0.0)

    def roll_minus(self):
        self.niyro_robot.jog_pose(0.0, 0.0, 0.0, -self.rpy_step, 0.0, 0.0)

    def pitch_plus(self):
        self.niyro_robot.jog_pose(0.0, 0.0, 0.0, 0.0, self.rpy_step, 0.0)

    def pitch_minus(self):
        self.niyro_robot.jog_pose(0.0, 0.0, 0.0, 0.0, -self.rpy_step, 0.0)

    def yaw_plus(self):
        self.niyro_robot.jog_pose(0.0, 0.00, 0.0, 0.0, 0.0, self.rpy_step)

    def yaw_minus(self):
        self.niyro_robot.jog_pose(0.0, 0.0, 0.0, 0.0, 0.0, -self.rpy_step)

    def j1_plus(self):
        self.niyro_robot.jog_joints(self.joint_step, 0.0, 0.0, 0.0, 0.0, 0.0)

    def j1_minus(self):
        self.niyro_robot.jog_joints(-self.joint_step, 0.0, 0.0, 0.0, 0.0, 0.0)

    def j2_plus(self):
        self.niyro_robot.jog_joints(0.0, self.joint_step, 0.0, 0.0, 0.0, 0.0)

    def j2_minus(self):
        self.niyro_robot.jog_joints(0.0, -self.joint_step, 0.0, 0.0, 0.0, 0.0)

    def j3_plus(self):
        self.niyro_robot.jog_joints(0.0, 0.00, self.joint_step, 0.0, 0.0, 0.0)

    def j3_minus(self):
        self.niyro_robot.jog_joints(0.0, 0.0, -self.joint_step, 0.0, 0.0, 0.0)

    def j4_plus(self):
        self.niyro_robot.jog_joints(0.0, 0.0, 0.0, self.joint_step, 0.0, 0.0)

    def j4_minus(self):
        self.niyro_robot.jog_joints(0.0, 0.0, 0.0, -self.joint_step, 0.0, 0.0)

    def j5_plus(self):
        self.niyro_robot.jog_joints(0.0, 0.0, 0.0, 0.0, self.joint_step, 0.0)

    def j5_minus(self):
        self.niyro_robot.jog_joints(0.0, 0.0, 0.0, 0.0, -self.joint_step, 0.0)

    def j6_plus(self):
        self.niyro_robot.jog_joints(0.0, 0.00, 0.0, 0.0, 0.0, self.joint_step)

    def j6_minus(self):
        self.niyro_robot.jog_joints(0.0, 0.0, 0.0, 0.0, 0.0, -self.joint_step)

    def reset(self):
        self.niyro_robot.set_jog_control(False)
        self.niyro_robot.move_joints(0.0, 0.0, 0.0, 0.0, -1.57, 0.0)
        self.niyro_robot.set_jog_control(True)

    def open_gripper(self):
        self.niyro_robot.set_jog_control(False)
        self.niyro_robot.open_gripper()
        self.niyro_robot.set_jog_control(True)

    def close_gripper(self):
        self.niyro_robot.set_jog_control(False)
        self.niyro_robot.close_gripper()
        self.niyro_robot.set_jog_control(True)


def process(niyro_robot):
    niyro_robot.move_joints(0.0, 0.0, 0.0, 0.0, -1.57, 0.0)
    niyro_robot.set_jog_control(True)

    TkinterController(niyro_robot)

    niyro_robot.set_jog_control(False)
    niyro_robot.set_learning_mode(True)


if __name__ == '__main__':
    # Connect to robot
    robot = NiryoRobot(robot_ip_address)
    # Calibrate robot if robot needs calibration
    robot.calibrate_auto()
    # Update tool
    robot.update_tool()
    # Launching main process
    process(robot)
    # Releasing connection
    robot.close_connection()
