def insertToDB(datestamp, connected, ap_prop_iface):
    """Write down Access Point parameters to database"""
    import MySQLdb
    
    #connect do DB and open a cursor. Specify your db connection parameters.
    db = MySQLdb.connect(host="localhost", user="root", passwd="sqlsql", db="AccessPoints", charset='utf8')
    cursor = db.cursor()
    
    #Access Point parameters
    encryption = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "Flags" )
    wpa_flags = encodeSecFlags( ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "WpaFlags" ) )
    rsn_flags = encodeSecFlags( ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "RsnFlags" ) )
    ssid = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "Ssid", byte_arrays=True )
    freq = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "Frequency" )
    hwaddr = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "HwAddress")
    mode = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "Mode")
    maxbitrate = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "MaxBitrate")
    strength = ord(str(ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "Strength")))
    
    #preparing and execution of SQL query
    cursor.execute("""insert into ap(
    datestamp, connected, encryption, wpa_flags, rsn_flags, ssid, freq, hwaddr, mode, maxbitrate, strength )
    values (
    '%(datestamp)s', '%(connected)i', '%(encryption)i', '%(wpa_flags)s', '%(rsn_flags)s', '%(ssid)s', '%(freq)i', '%(hwaddr)s', '%(mode)i', '%(maxbitrate)i', '%(strength)s' )""" 
    %{"datestamp":datestamp, "connected":connected, "encryption":encryption, "wpa_flags":wpa_flags, "rsn_flags":rsn_flags, "ssid":ssid, "freq":freq, "hwaddr":hwaddr, "mode":mode, "maxbitrate":maxbitrate, "strength":strength}
    )
    
    db.commit()
    
def encodeSecFlags( flags ):
    """Encode integer value of wpa and rsn flags"""
    #Security capabilities of the access point
    sec_flags = [
                 ( '', 0 )
                 , ( 'pairwise 40-bit WEP encryption', 1 )
                 , ( 'pairwise 104-bit WEP encryption', 2  )
                 , ( 'pairwise TKIP encryption', 4 )
                 , ( 'pairwise CCMP encryption', 8 )
                 , ( 'group 40-bit WEP cipher', 10 )
                 , ( 'group 104-bit WEP cipher', 20 )
                 , ( 'group TKIP cipher', 40 )
                 , ( 'group CCMP cipher', 80 )
                 , ( 'PSK key management', 100 )
                 , ( '802.1x key management', 200 )
                 ]

    sec_capabilities = []
    
    while flags > 1:
        temp = []
        #Find max addendum and add to addendums list
        for sec_flag in sec_flags:
            i = flags - sec_flag[1]
            if i >= 0:
                addendum = sec_flag[1]
                temp.append(sec_flag[0])
        sec_capabilities.append(temp[-1])
        flags = flags - addendum
        
    return ", ".join("%s" % (sec) for sec in sec_capabilities)


from datetime import datetime

import dbus
bus = dbus.SystemBus()

# Get a proxy for the base NetworkManager object
proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")

# Get all network devices
devices = manager.GetDevices()
for d in devices:
    dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
    prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

    # Make sure the device is enabled before we try to use it
    state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
    if state <= 2:
        continue

    # Get device's type; we only want wifi devices
    iface = prop_iface.Get("org.freedesktop.NetworkManager.Device", "Interface")
    dtype = prop_iface.Get("org.freedesktop.NetworkManager.Device", "DeviceType")
    if dtype == 2:   # WiFi
        # Get a proxy for the wifi interface
        wifi_iface = dbus.Interface(dev_proxy, "org.freedesktop.NetworkManager.Device.Wireless")
        wifi_prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

        # Get the associated AP's object path
        connected_path = wifi_prop_iface.Get("org.freedesktop.NetworkManager.Device.Wireless", "ActiveAccessPoint")

        # Get all APs the card can see
        aps = wifi_iface.GetAccessPoints()
        
        for path in aps:
            ap_proxy = bus.get_object("org.freedesktop.NetworkManager", path)
            ap_prop_iface = dbus.Interface(ap_proxy, "org.freedesktop.DBus.Properties")
            #Find out if we are connected to current AP
            connected = 1 if path == connected_path else 0
            insertToDB (datetime.now(), connected, ap_prop_iface)
