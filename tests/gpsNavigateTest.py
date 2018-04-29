from drivers.mag.compass import Compass
from drivers.gps.gpsNavboard import GPS
from drivers.rovecomm import RoveComm
from drivers.driveBoard import DriveBoard
from algorithms.lidar import LiDAR

# Hardware Setup
rovecomm_node = RoveComm()

rovecomm_node.callbacks[ENABLE_AUTONOMY] = enable_autonomy
rovecomm_node.callbacks[DISABLE_AUTONOMY] = disable_autonomy
rovecomm_node.callbacks[ADD_WAYPOINT] = add_waypoint_handler

drive = DriveBoard(rovecomm_node)
gps = GPS(rovecomm_node)
mag = Compass(rovecomm_node)
lidar = LiDAR()

navigate = GPSNavigate(gps, mag, drive, lidar)

# RoveComm autonomy control DataIDs
ENABLE_AUTONOMY = 2576
DISABLE_AUTONOMY = 2577
ADD_WAYPOINT = 2578
CLEAR_WAYPOINTS = 2579
WAYPOINT_REACHED = 2580

# Assign callbacks for incoming messages
def add_waypoint_handler(packet_contents):
    latitude, longitude = struct.unpack("<dd", packet_contents)
    navigate.setWaypoint(GeoMath.Coordinate(latitude, longitude))
    print("Added waypoint %s" % (waypoint,))

def enable_autonomy(packet_contents):
    global autonomy_enabled
    autonomy_enabled = True
    print("Autonomy Enabled")
    drive.enable()

def disable_autonomy(packet_contents):
    global autonomy_enabled
    global drive
    autonomy_enabled = False
    print("Autonomy Disabled :(")
    drive.disable()

# Set waypoint to use and use a while loop for update thread

while True:
    while autonomy_enabled:
        if navigate.update_controls():
            autonomy_enabled = False
            drive.disable()
            print("Autonomy Finished! :)")
            rovecomm_node.send(WAYPOINT_REACHED, contents="")
        time.sleep(.1)
    time.sleep(2)