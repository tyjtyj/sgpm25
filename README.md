# SGNEA home-assistant


Home Assistant Custom Component to get PM2.5 from Singapore National Enviroment Agency (SG NEA)


This file is modified from home assistant scraper.py


Home assistant
configuration.yaml file

```
sensor:
  - platform: sgnea
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
