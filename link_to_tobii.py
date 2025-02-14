# %%
import tobii_research as tr
import time

# %%
address = "tet-tcp://169.254.53.181"
address = "http://169.254.53.181/"
address = "http://tg03b-080201140731.local"
eyetracker = tr.EyeTracker(address)
print(eyetracker)
# %%
print(tr.__version__)
found_eyetrackers = tr.find_all_eyetrackers()
print(found_eyetrackers)
my_eyetracker = found_eyetrackers[0]
print("Address: " + my_eyetracker.address)
print("Model: " + my_eyetracker.model)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
print("Serial number: " + my_eyetracker.serial_number)
