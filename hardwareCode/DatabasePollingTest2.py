import time
from Database_Polling import DatabasePolling
from MenuManagementSystem import MenuManagementSystem

def testargument():
    print("Testargument function ran.")

class PumpWater:
    def manual_turn_off_pump(self):
        print('Pump is turned off.')

    def set_pwm_duty_cycle(self, cycles):
        print(f"PWM duty cycle set to: {cycles}")




menu_system = MenuManagementSystem(max_queue_size=5)
menu_system.add_option("testcommand", testargument)
menu_system.add_option("[PumpWater]-manual_turn_on_pump", PumpWater.manual_turn_off_pump)
menu_system.add_option("[PumpWater]-set_pwm_duty_cycle", PumpWater.set_pwm_duty_cycle)



def test_database_polling():
    '''
    thread test
    '''
    db_polling = DatabasePolling(menu_system)
    db_polling.start_polling()
    time.sleep(20)
    db_polling.stop_polling()

def test_database_basic():
    '''
    regular code test
    '''
    db_polling = DatabasePolling(menu_system)
    db_polling.request()


# Run the test
test_database_polling()
#test_database_basic()
print("Registered commands:", menu_system.options)

