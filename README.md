## LakePy
LakePy is the pythonic user-centered front-end to the [Global Lake Level Database](link). This package can instantly
 deliver lake water levels for some 2000+ lakes scattered across the globe. Data comes from three sources (so far!)
 - [United States Geological Survey National Water Information System](https://waterdata.usgs.gov/nwis)
 - [United States Department of Agriculture: Foriegn Agricultural Service's G-REALM Database](https://ipad.fas.usda.gov/cropexplorer/global_reservoir/)
 - [Theia's HydroWeb Database](http://hydroweb.theia-land.fr/)

 
**Funding for this work comes from the Earth Science Information Partners (ESIP) Winter 2020 Grant**

_See the funded proposal [here](https://www.esipfed.org/wp-content/uploads/2020/04/Gearon.pdf)_

## Motivation
Lake level data is incredibly important to federal and local governments, scientists, and citizens. Until now,
accessing lake level data involves laborious data-preparation and wrangling. We aim to provide this data quickly
and on-demand

## Screenshots
Include logo/demo screenshot etc.

## Software Used
<b>Built with</b>
- [Python](https://www.python.org/)
- [Amazon Aurora Serverless](https://aws.amazon.com/rds/aurora/serverless/)
- [Amazon Aurora Serverless Data API](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html)

## Features
```
import lakepy as lk
my_lake = lk.search("Ayakkum")
```
LakePy allows for native time series plotting as well as map-view plots
```
my_lake.plot_timeseries()
```
```
my_lake.plot_mapview()
```

## Code Example
Show what the library does as concisely as possible, developers should be able to figure out **how** your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise.

## Installation
Provide step by step series of examples and explanations about how to get a development env running.

## API Reference

Depending on the size of the project, if it is small and simple enough the reference docs can be added to the README. For medium size to larger projects it is important to at least provide a link to where the API reference docs live.

## How to use?
If people like your project they’ll want to learn how they can use it. To do so include step by step guide to use your project.

## Contribute

Let people know how they can contribute into your project. A [contributing guideline](https://github.com/zulip/zulip-electron/blob/master/CONTRIBUTING.md) will be a big plus.

## Credits
Give proper credits. This could be a link to any repo which inspired you to build this project, any blogposts or links to people who contrbuted in this project. 

#### Anything else that seems useful

## License

MIT © [James Hooker Gearon & John Daniel Franey](https://github.com/ESIPFed/GlobalLakeLevelDatabase/blob/master/LICENSE)