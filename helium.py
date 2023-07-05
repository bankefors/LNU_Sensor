import struct
import binascii
import time
from LoRaWAN import lora

lora = lora()

DEV_EUI = "70B3D57ED005EE71"
APP_EUI = "0000000000001234"
APP_KEY = "8EF1CEFC557FAE64FFD7D5EC91C3A7FC"

lora.configure(DEV_EUI, APP_EUI, APP_KEY)

lora.startJoin()
print("Start Join.....")
RetryCount = 1
while not lora.checkJoinStatus() and RetryCount < 21:
  print("attempting to join: {0}".format(RetryCount))
  time.sleep(10)
  RetryCount = RetryCount + 1
if  lora.checkJoinStatus():
  print("Join success!")
else:
  print("Join failed!")

