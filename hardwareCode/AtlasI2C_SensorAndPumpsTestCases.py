def testCase():
    from AtlasI2C_SensorAndPumps import AtlasI2C_SensorAndPumps
    
    pH_UpPin = 22
    pH_DownPin = 23
    baseA_Pin = 20
    baseB_Pin = 21
    
    sensorAndPumpsSubsystem = AtlasI2C_SensorAndPumps("ecSubsystem", baseA_Pin, "baseA", baseB_Pin, "baseB", "EC", False, True, False, True)
    
    sensorAndPumpsSubsystem.addToListCondThreadTuplesGeneral(">", 100, False, sensorAndPumpsSubsystem.sensor.turnOnLED_TestCallback, [], "Will turn on LED for 5 seconds and then turn back off")
    sensorAndPumpsSubsystem.addToListCondThreadTuplesPumpDuration(">", 100, "baseA", True, "turn on baseA pump")
    
    sensorAndPumpsSubsystem.status.updateStatusDict()
    sensorAndPumpsSubsystem.status.updateStatusString(includeHorizontalLines=True)
    
    print(sensorAndPumpsSubsystem.status.statusString)
    
    input("Input anything to start cont poll and cond threads: ")
    
    sensorAndPumpsSubsystem.startSensorContPollThread()
    sensorAndPumpsSubsystem.startSensorCondThread()
    
    input("Input anything to end program: ")

    sensorAndPumpsSubsystem.shutDownSystem()