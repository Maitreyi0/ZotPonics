# test functions for the test cases

def greet_user(name):
    print(f"Hello, {name}!")
    
def greet_user_return_str(name):
    return f"Hello, {name}!"

def add_numbers(a, b):
    print(f"The sum of {a} and {b} is {a + b}")
    
def add_numbers_return_str(a, b):
    return f"The sum of {a} and {b} is {a + b}"

def delay_loop(duration):
    import time
    """
    Delays execution by continually passing a loop until the specified duration is met.
    :param duration: Duration in seconds to delay.
    """
    start_time = time.time()  # Record the start time
    while (time.time() - start_time) < duration:
        pass  # Continually pass the loop
    
def thread_1(menu_system):
    print("Thread 1 enqueueing delay...")
    menu_system.enqueue_command("delay", 1)
    print("Thread 1 enqueueing add...")
    menu_system.enqueue_command("add", 3, 5)
    print("Thread 1 enqueueing greet...")
    menu_system.enqueue_command("greet", "Ivan")

def thread_2(menu_system):
    import time
    time.sleep(0.5)
    print("Thread 2 enqueueing greet...")
    menu_system.enqueue_command("greet", "Ivan")
    print("Thread 2 enqueueing again...")
    menu_system.enqueue_command("add", 5, 3)

def single_thread_test_case():
    from MenuManagementSystem import MenuManagementSystem
    # Create an instance of MenuManagementSystem with a 5-command queue size
    menu_system = MenuManagementSystem(max_queue_size=5)

    # Add options to the menu system with arguments
    menu_system.add_option("greet 1", greet_user)
    menu_system.add_option("add 1", add_numbers)
    menu_system.add_option("greet 2", greet_user_return_str)
    menu_system.add_option("add 2", add_numbers_return_str)
    menu_system.add_option("delay", delay_loop)
    

    # Start the menu system's queue processing in a separate thread
    menu_system.start_processing()

    # Enqueue commands with or without additional arguments
    menu_system.enqueue_command("greet 1", "Alice")  # Uses stored argument ("Alice")
    menu_system.enqueue_command("add 1", 1, 2)  # Overrides stored args, prints sum of 3 and 7
    menu_system.enqueue_command("delay", 1) # delay command
    print(menu_system.enqueue_command("greet 2"))
    print(menu_system.enqueue_command("add 2"))

    # Stop the menu system when needed
    menu_system.stop_processing()
    print("Menu processing has stopped.")
    
def multi_thread_test_case():
    import threading
    from MenuManagementSystem import MenuManagementSystem
    # Create an instance of MenuManagementSystem with a 5-command queue size
    menu_system = MenuManagementSystem(max_queue_size=5)

    # Add options to the menu system with arguments
    menu_system.add_option("add", add_numbers)
    menu_system.add_option("greet", greet_user)
    menu_system.add_option("delay", delay_loop)

    # Start the menu system's queue processing
    menu_system.start_processing()

    # Run threads to enqueue commands concurrently
    t1 = threading.Thread(target=thread_1, args=(menu_system,))
    t2 = threading.Thread(target=thread_2, args=(menu_system,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # Stop the menu system when needed
    menu_system.stop_processing()
    print("Menu processing has stopped.")