from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate

test_service_uuid = "0000aaa0-0000-1000-8000-aabbccddeeff"
test_service_char_uuid = "0000aaa2-0000-1000-8000-aabbccddeeff"
complete_local_name = "WanchuanPhone"


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)


scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(5.0)

n = 0
target_n = -1
addr = []
NotificationFlag = 0

with open('output.txt', 'w') as file:
    file.write('')

for dev in devices:
    print("%d: Device %s (%s), RSSI=%d dB" %
          (n, dev.addr, dev.addrType, dev.rssi))
    with open('output.txt', 'a') as file:
        file.write("%d: Device %s (%s), RSSI=%d dB\n" %
                   (n, dev.addr, dev.addrType, dev.rssi))

    addr.append(dev.addr)
    for (adtype, desc, value) in dev.getScanData():
        print(" %s = %s" % (desc, value))
        with open('output.txt', 'a') as file:
            file.write(" %s = %s\n" % (desc, value))

        if (desc == "Complete Local Name" and value == complete_local_name):
            print("Found ", complete_local_name)
            target_n = n

    n += 1


print("target device number", target_n)

# number = input('Enter your device number: ')
number = target_n

print('Device', number)
print(addr[number])
#
print("Connecting...")
dev = Peripheral(addr[number], 'random')


#
Services = dev.getServices()
for svc in Services:
    print(str(svc))
#
Chars = dev.getCharacteristics(startHnd=1, endHnd=0xFFFF, uuid=None)
for ch in Chars:
    print(str(ch))
#
print("Handle   UUID                                Properties")
print("-------------------------------------------------------")
for ch in Chars:
    print("  0x" + format(ch.getHandle(), '02X') + "   " +
          str(ch.uuid) + " " + ch.propertiesToString())
#
Descriptors = dev.getDescriptors(startHnd=1, endHnd=0xFFFF)
for desc in Descriptors:
    print(str(desc.uuid), str(desc))

#
test_service = dev.getServiceByUUID(UUID(test_service_uuid))
test_char = test_service.getCharacteristics(
    UUID(test_service_char_uuid))[0]

for desriptor in test_char.getDescriptors():
    if (desriptor.uuid == 0x2902):
        print("Client Characteristic Configuration found at uuid 0x",
              str(desriptor.uuid),
              " with handle 0x",
              format(desriptor.handle, '02X'))

        CCCD_handle = desriptor.handle

        print("Before writing to CCCD:", end="")
        print(dev.readCharacteristic(CCCD_handle))

        dev.writeCharacteristic(
            CCCD_handle, bytes([0, 2]), withResponse=True)

        print("After writing to CCCD:", end="")
        print(dev.readCharacteristic(CCCD_handle))
        # Turn notifications on by setting bit0 in the CCC more info on:
        # https://developer.bluetooth.org/gatt/descriptors/Pages/DescriptorViewer.aspx?u=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
        if (dev.readCharacteristic(CCCD_handle) == bytes([0, 0])):
            print("Notification is turned off")
        else:
            NotificationFlag = 1
            print("Notification is turned on")

        if (NotificationFlag == 1):
            print("Waiting for notifications")
            NotificationCount = 0
            while True:
                if dev.waitForNotifications(1.0):
                    # handleNotification() was called
                    NotificationCount += 1
                    print("Notification count:", NotificationCount)
                    continue
