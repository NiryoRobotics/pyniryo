from pyniryo import NiryoRobot
from pyniryo.vision import uncompress_image, show_img_and_wait_close

# Connecting to robot
robot = NiryoRobot('<robot_ip_address>')

# Getting image
img_compressed = robot.get_img_compressed()
# Uncompressing image
img = uncompress_image(img_compressed)

# Displaying
show_img_and_wait_close("img_stream", img)