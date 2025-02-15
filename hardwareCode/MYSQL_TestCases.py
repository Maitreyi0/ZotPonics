import MYSQL

def test_insert_and_delete():
    """
    Test inserting and deleting afterwards (ideally the same entry)
    """
    
    print(f"The initial number of entries in the requests table is: {MYSQL.retrieve_current_number_of_requests()}")
    
    print("Inserting command into requests table...")
    MYSQL.insert_requests_table(command="set_pwm_duty_cycle", arguments=[50])
    
    print(f"After insertion, the number of entries in the requests table is: {MYSQL.retrieve_current_number_of_requests()}")
    
    print("Popping request from requests table...")
    retrieved_request = MYSQL.pop_most_recent_request()
    
    print(f"Retrieved request: {retrieved_request}")
    
    print(f"After retrieval, the number of entries in the requests table is: {MYSQL.retrieve_current_number_of_requests()}")
    
    exit()