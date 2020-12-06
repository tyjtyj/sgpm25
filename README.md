# SGNEA 1Hour PM2.5 home-assistant


**this intergration is broken due to api changed/removed. I will come back next time haze hit again

Home Assistant Custom Component to get PM2.5 from Singapore National Enviroment Agency (SG NEA)


This file is modified from home assistant scraper.py


Home assistant
configuration.yaml file

```
sensor:
  - platform: sgpm25
    name: 'SG 1Hour PM2.5'
    area: 'YOURLOCATION'
```


Location List:
- Replace YOURLOCATION with the locations below. 

```
national
north
south
east
west
central
```

Recomended additional automation. The data appears to update around the 9th minute hourly. 
```
- alias: 'Hourly Update'
  initial_state: on
  trigger:
    - platform: time_pattern
      minutes: 10
  action:
    - service: homeassistant.update_entity
      entity_id: sensor.sg_1hour_pm2_5
```
