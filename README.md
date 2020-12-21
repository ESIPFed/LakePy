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
and on-demand.

## Software Used
<b>Built with</b>
- [Python](https://www.python.org/)
- [Amazon Aurora Serverless](https://aws.amazon.com/rds/aurora/serverless/)
- [Amazon Aurora Serverless Data API](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html)

## Quickstart

### Installation
```
pip install lakepy
```
if you are using conda for package management you can
 [still use pip!](https://medium.com/@msarahan/anaconda-also-comes-with-pip-and-you-can-use-it-to-install-pypi-packages-into-conda-environments-9e7f021509f7)
 ### Searching the Global Lake Level Database
 The database can be searched using a name, a source ("grealm", "hydroweb", or "usgs"), or an identification number
 . The best practice for searching is to first specify a name.
 
 Let's search for [Lake Mead](https://en.wikipedia.org/wiki/Lake_Mead) instantiating a Lake() object.
```
import lakepy as lk
my_lake = lk.search("mead")
```
If there is more than one Lake matching "Mead", the search function will return a

> "Search Result: 'Mead' has more than 1 Result. Showing the 2 most relevant results.
Specify 'id_No' or narrow search name."

|    |   id_No | source   | lake_name                           |
|---:|--------:|:---------|:------------------------------------|
|  0 |     138 | hydroweb | Mead                                |
|  1 |    1556 | usgs     | MEAD LAKE WEST BAY NEAR WILLARD, WI |

We will select id_No 138 corresponding to Lake Mead from HydroWeb's database and re-run our search 1 of 2 ways:
- Specify the **id_No** explicitly as a string

```
my_lake = lk.search(id_No = "138")
```

- Specify a **name** and a **source**
```
my_lake = lk.search(name="mead", source="hydroweb")
```
We _highly recommend_ specifying an id_No _whenever possible_ to avoid issues with similarly named lakes. Either way
, the search returns a metadata markdown dataframe

|    |   id_No | source   | lake_name   | basin    | status   | country   | end_date         |   latitude |   longitude | identifier   | start_date       |
|---:|--------:|:---------|:------------|:---------|:---------|:----------|:-----------------|-----------:|------------:|:-------------|:-----------------|
|  0 |     138 | hydroweb | Mead        | Colorado | research | USA       | 2014-12-29 00:21 |      36.13 |     -114.45 | L_mead       | 2000-06-14 10:22 |

It is important to note that different databases will return different types and amounts of metadata. Currently

LakePy allows for native time series plotting as well as map-view plots
```
my_lake.plot_timeseries()
```
```
my_lake.plot_mapview()
```

## Code Example
Show what the library does as concisely as possible, developers should be able to figure out **how** your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise.




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