pi_arduino
==========

### This is my raspberry pi temperature sensor code.  

This includes the backend process (log_temp.py) that collects the temperature and logs it into the sqlite database, -ignore the misspelling *tempature.db**-. I am running the backend process with supervisord and redirecting standard out to log folder.

The webserver includes a FLASK app that serves the bootstrap/d3.js/rickshaw front end that shows the current temperature and the 24 trend graph.

You can read about this project at www.brettdangerfield.com

### What's next?

- Add more temp sensors 
- Insert admin page to name each sensor by room
- Add each sensor's trend to the graph and show current temps by room
- Allow the chart to be controlled for time range and y-axis min/max

**Long Term**

- Get a wifi enabled thermostat
- control thermostat with pi
- create rules base on time/temp in each room
