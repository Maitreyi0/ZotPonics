def test_motion_simple():
    from StepperMotor import StepperMotor
    import GPIO_Utility
    import time
    
    # Temp pins for the current test
    DIR_PIN = 27
    STEP_PIN = 17

    # Horizontal Stepper Motor 1
    stepperMotor = StepperMotor(step_pin=STEP_PIN, dir_pin=DIR_PIN)
    
    # Rotate one full revolution, reverse directions, and another full revolution
    stepperMotor.perform_full_revolution()
    stepperMotor.set_direction(clockwise=True)
    time.sleep(1)
    stepperMotor.perform_full_revolution()
    
    # Perform One Step
    # stepperMotor.step()