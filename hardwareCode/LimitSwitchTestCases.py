def test_simple():
    from LimitSwitch import LimitSwitch
    import time
    
    def interrupt_handle_test():
        print("Interrupt was triggered...")

    limitSwitch = LimitSwitch(NO_pin=4, interrupt_handle_function=interrupt_handle_test, interrupt_handle_function_args_list=[])
    limitSwitch.init_interrupt_pin_and_service()
    
    while True:
        time.sleep(1) # Keep Running, until Keyboard Interrupt probably
        
    