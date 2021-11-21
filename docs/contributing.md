:construction: This page is a work in progress :construction:
# How to Contribute

Hi! Thank you for looking into how to contribute. 

The following is a guideline on how to contribute towards:

- [Bug Reports](#bug-reports)

- [Bug Patches](#bug-patches)

- [New Features](#new-features)

- [New Databases](#new-databases)

## Bug Reports

- Ensure the bug has not already been reported in our [issues](https://github.com/ESIPFed/LakePy/issues).
- If the bug has not been reported, please feel free to open a [new issue](https://github.com/ESIPFed/LakePy/issues/new).
In the new issue, please include a **title and clear description** of the bug. 
  Also include as much *relevant* information as possible, a **code example** 
  that caused the bug, and the **error warning**.
  
## Bug Patches
- Open a [pull request](https://github.com/ESIPFed/LakePy/compare) with the patch.
- Fully describe the problem the patch is meant to fix. It would also be helpful to 
link to the relevant [issue](https://github.com/ESIPFed/LakePy/issues).

## New Features
if you have an idea for new methods to be added to the Lake() class, we would love to hear them!
The current state of LakePy mainly deals with accessing the actual lake level data from the disparate
data sources that have been collated to our AWS MySQL database. However, it would always be great to give
more options and methods to our users. We are sure many of you have great ideas on how this data can be used in ways we
never thought of!

- We currently use issues and PR for bug patches. if you have an idea about a new feature please send a **description
and code example** to [jhgearon@iu.edu](mailto:jhgearon@iu.edu).
- After discussions, revisions, and approval, feel free to open a new
  [pull request](https://github.com/ESIPFed/LakePy/compare) with the same title.
  
## New Databases
Adding new lakes to our database is possibly the most helpful thing to this project. We currently source our data from:

- [United States Geological Survey National Water Information System](https://waterdata.usgs.gov/nwis)
- [United States Department of Agriculture: Foriegn Agricultural Service's G-REALM Database](https://ipad.fas.usda.gov/cropexplorer/global_reservoir/)
- [Theia's HydroWeb Database](http://hydroweb.theia-land.fr/)

These are currently some of the largest lake databases, but no database is too big or small for our project! Whether a
a new lake data is a country, state, or county, if it is public data, we would love to add it to LakePy. First, please
do check to make sure the lakes you wish to add are not already a part of LakePy.

Adding a new data source is fairly resource intensive and occurs on our backend. Please reach out to us at
[jhgearon@iu.edu](mailto:jhgearon@iu.edu) to get started on adding a new data source.


We appreciate taking the time to look into how to contribute towards LakePy.

Thanks,

*James Gearon & John Franey*

**LakePy is Funded by the Earth Science Information Partners (ESIP) Winter 2020 Grant and the charitable contribution of Derek Masaki and Farial Shahnaz.**

_See the funded proposal [here](https://www.esipfed.org/wp-content/uploads/2020/04/Gearon.pdf)._