import sys,os
import bjoern

current_path = os.path.abspath('./')
sys.path.append(current_path)
from ppaa import create_app
print(current_path)


if __name__ == "__main__":
    default_ip = "0.0.0.0"
    default_port = 8080

    ip = default_ip
    port = default_port
    app = create_app(DEBUG=False)
    bjoern.run(app,ip,port)


    

