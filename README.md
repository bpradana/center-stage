# SPOTLIGHT SCENE

## Installing
1. Install [Python](https://www.python.org/) 3.6 or later and PIP
   ```bash
   sudo apt install python3
   sudo apt install python3-pip
   ```
2. Create [Python Virtual Environment](https://docs.python.org/3/library/venv.html)
   ```bash
   pip3 install virtualenv
   python3 -m venv env
   source env/bin/activate
   ```
3. Install required Python packages
   ```bash
   pip3 install -r requirements.txt
   ```

## Running
1. Activate the Python virtual environment
   ```bash
   source env/bin/activate
   ```
2. Check available cameras
   ```bash
   python3 check_cam.py
   ```
3. Run the script
   ```bash
   python3 main.py --camera=<index of camera> --height=<height of video frame> --width=<width of video frame>
   ```