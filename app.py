
import watchdog.events 
import watchdog.observers 
import time 
from pathlib import Path
from test import processor
from watchdog.events import LoggingEventHandler
class Handler(LoggingEventHandler): 
  
    def on_created(self, event): 
        print("Watchdog received created event - % s." % event.src_path) 
       
        processor(event.src_path)
        
        #self.observer.stop() # stop watching
        #self.callback()
        # Event is created, Now process for model


    


  
  
if __name__ == "__main__": 
    src_path = 'media/master'
    event_handler = Handler() 
    observer = watchdog.observers.Observer() 
    observer.schedule(event_handler, path=src_path, recursive=True) 
    observer.start()
    print('observer initiated') 
    try: 
        while True: 
            time.sleep(1) 
    except KeyboardInterrupt: 
        observer.stop() 
        print('KeyboardInterrupt') 
    observer.join()