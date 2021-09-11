---
title: 'LakePy: a Python Package for Accessing and Manipulating Lacustrine Time-Series Data'

tags:

- Python
- lakes
- timeseries
- remote sensing
- water level
- lacustrine
- AWS
- water management
- data availability

authors:

- name: James H. Gearon[^corresponding author]
  orcid: 0000-0002-0115-7937 affiliation: "1, 2"
- name: John Daniel Franey affiliation: 3
- name: The University of Texas at Austin, Dept. of Geological Sciences index: 1
- name: Indiana University, Dept. of Earth & Atmospheric Sciences index: 2
- name: The University of Texas at Austin, Bureau of Economic Geology index: 3 date: 11 September 2021 bibliography:
  paper.bib

---

# Summary

LakePy is a freely available, open-source python package which serves historical lake-level data, associated metadata,
and is equipped with several built-in lake analysis tools. The objective of LakePy is simple: to make accessing and
manipulating lake time-series data convenient, efficient, and fully open-source. Additionally, LakePy assumes no
previous Python knowledge for the end-user, aiming to include clear and instructive steps within the documentation and
associated Jupyter notebooks. LakePy is built on several open-source packages such
as [GeoPandas](https://geopandas.org/), [PyMySQL](https://pymysql.readthedocs.io/en/latest/)
, [Boto3](https://boto3.readthedocs.io/), and [LeafMap](https://github.com/giswqs/leafmap) [@Wu2021:2021] as well
as [Amazon Web Services](https://aws.amazon.com/) infrastructure.

# Statement of need

LakePy represents the **only** lake data centric Python package. Lake data are crucial to water resource management and
continued scientific research into limnological questions. Moreover, anthropogenic climate change is affecting lakes rapidly and in unexpected
ways [CITE], making easily-accessible and up-to-date lake level data even more important as climate change mitigation
efforts are rolled out. For the past decade, and increasingly so in the last few years, that data has been dutifully
warehoused across federal, state, local, academic, and private databases. The issue with these data is not their
existence, but their _ease of access_. These data are often behind registration walls, stored in text files on an old
server, or are sparsely documented to make data retrieval an extended process. Indeed, many researchers, government
officials, and concerned citizens who may want access to local lake level information may be unaware or unable to
interface with existing data infrastructure.

# Data Sources

LakePy serves as the user-centered front-end to
the [Global Lake Level Database](https://github.com/ESIPFed/Global-Lake-Level-Database). The Global Lake Level Database
was constructed as a part of the LakePy project and can be considered part of the package infrastructure. The Global
Lake Level Database utilizes an AWS MySQL Relational Database, AWS Lambda, and AWS API Gateway to query, house, and
serve lake level data from a suite of publicly available databases. Together with the Global Lake Level Database, LakePy
can instantly deliver lake water levels for some 2000+ lakes. So far, data come from three sources:

* [United States Geological Survey National Water Information System](https://waterdata.usgs.gov/nwis)
* [United States Department of Agriculture: Foriegn Agricultural Service's G-REALM Database](https://ipad.fas.usda.gov/cropexplorer/global_reservoir/)
* [Theia's HydroWeb Database](http://hydroweb.theia-land.fr/)

Each of these

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred citation) then you can do it
with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:

- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

This work is based on funding provided by the Earth Science Information Partners (ESIP) Lab with support from the
National Aeronautics and Space Administration (NASA), National Oceanic and Atmospheric Administration (NOAA) and the
United States Geologic Survey (
USGS).

# References

- [GeoPandas](https://geopandas.org/)
- [PyMySQL](https://pymysql.readthedocs.io/en/latest/)
- [Boto3](https://boto3.readthedocs.io/)

* [Amazon MySQL RDS](https://aws.amazon.com/rds/mysql/)
* [Amazon API Gateway](https://aws.amazon.com/api-gateway/)
* [Amazon Lambda](https://aws.amazon.com/lambda/)