# Sensor for Correios - Brazilian postal service 
The correios platform allows one to track deliveries by [Correios](www.correios.com.br).

To get started put `/custom_components/hadockermon/binary_sensor.py` here:
`<config directory>/custom_components/hadockermon/binary_sensor.py`

**Example configuration.yaml:**
```yaml
sensor:
  - platform: correios
    code: OH194102423BR
    name: objeto
    scan_interval: 600
```

**Configuration variables:**
  
key | description
:--- | :---
**platform (Required)** | The platform name.
**code (Required)** | (13 digits) The track number.
**name (Optional)** | (String) The name to use when displaying this Transmission instance in the frontend. Defaults to correios.
**scan_interval (Optional)** | (integer) How frequently to query for new data. Defaults to 1800 seconds.

#### Sample overview
![Sample overview](images/correios.png)

