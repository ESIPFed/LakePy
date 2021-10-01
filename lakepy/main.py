def search(name=None, source=None, id_No=None, markdown=False):
    """
    Search function that interacts directly with the Global Lake Level Database API.
    Arguments:
        name (str): Name of Lake or Reservoir. Be sure to use proper spelling. Wildcards (%) are allowed,as is any MySQL 5.7 syntax
        source (str): Lake water level source flag, accepted values are "usgs", "grealm", or "hydroweb"
        id_No (str,int): Global Lake Level Database identification number
        markdown (bool, optional): Returns markdown dataframe when True

    Returns:
        Lake object: `Lake()` object
    """

    import pandas as pd
    import requests
    import warnings
    from IPython.display import display
    if id_No:
        id_No = str(id_No)
        url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/prod/glld/search/?idNo={}'.format(
            id_No)
        r = requests.get(url)
        json_decode = r.json()
        df = pd.DataFrame().from_records(json_decode, columns = ['id_No', 'lake_name', 'source', 'metadata'])

    elif not source:
        url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/prod/glld/search/?name={}'.format(
            name)
        r = requests.get(url)
        json_decode = r.json()
        df = pd.DataFrame().from_records(json_decode, columns = ['id_No', 'lake_name', 'source', 'metadata'])

    elif source:
        url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/prod/glld/' \
              'search?name={}&source={}'.format(name, source)
        r = requests.get(url)
        json_decode = r.json()
        df = pd.DataFrame().from_records(json_decode, columns = ['id_No', 'lake_name', 'source', 'metadata'])
    else:
        raise ValueError("I don't know how you did this, but if you did, make a github issue!")
    if len(df) < 1:
        raise RuntimeError('No results returned. Please adjust search parameters or see documentation')
    if len(df) > 1:
        warnings.warn('Search Result: \'{}\' has more than 1 Result. Showing the {} most relevant results.\n'
                      'Specify \'id_No\' or narrow search name.'.format(name, len(df)), category = RuntimeWarning)
        if markdown is True:
            print(df.filter(['id_No', 'source', 'lake_name']).to_markdown())
        else:
            print(df.filter(['id_No', 'source', 'lake_name']))

    elif len(df) == 1:
        meta_series = df['metadata'].map(eval).apply(pd.Series)
        df_unpacked = pd.merge(left = df,
                               right = meta_series.drop(['source', 'lake_name'],
                                                        axis = 1),
                               left_index = True,
                               right_index = True,
                               how = 'outer').drop('metadata', axis = 1)
        if markdown is True:
            print(df_unpacked.to_markdown())
        else:
            with pd.option_context('display.max_rows', 5, 'display.max_columns', None):
                display(df_unpacked)
        lake_object = _lake_meta_constructor(df_unpacked)
        return lake_object


def _lake_meta_constructor(df):
    """

    Arguments:
        df (): Pandas DataFrame of lake metadata from :function:`search`

    Returns:
        {:class:`Lake`}

    """

    import pandas as pd
    import requests
    # todo location!!!!!!!!
    if len(df) > 1:
        raise RuntimeError('{} lakes have been passed to the constructor which only accepts one as input.\n'
                           'Utilize search parameters by passing "source" or "id_No" to refine results')
    elif len(df) == 1:
        source = df.source[0]
        if source == 'grealm':
            name = df.lake_name[0]
            country = df.Country[0]
            continent = df.Continent[0]
            original_id = df.grealm_database_ID[0]
            id_No = df.id_No[0]
            observation_period = df['Satellite Observation Period'][0]
            misc_data = {'Type': df.Type[0], 'Resolution': df.Resolution[0]}
            metadata = df
            lake = Lake(name = name,
                        country = country,
                        continent = continent,
                        source = source,
                        original_id = original_id,
                        id_No = id_No,
                        observation_period = observation_period,
                        latitude = None,
                        longitude = None,
                        misc_data = misc_data,
                        metadata = metadata,
                        data = None,
                        timeseries = None)
            lake.data = _get_levels(lake)
            lake.timeseries = lake.data.filter(['date', 'water_level']).set_index('date')
            return lake

        elif source == 'hydroweb':
            name = df.lake_name[0]
            id_No = df.id_No[0]
            country = df.country[0]
            original_id = df.identifier[0]
            observation_period = df.start_date[0] + ' -- ' + df.end_date[0]
            latitude = df.latitude[0]
            longitude = df.longitude[0]
            misc_data = {'basin': df.basin[0], 'status': df.status[0]}
            metadata = df

            lake = Lake(name = name,
                        country = country,
                        continent = None,
                        source = source,
                        original_id = original_id,
                        id_No = id_No,
                        observation_period = observation_period,
                        latitude = latitude,
                        longitude = longitude,
                        misc_data = misc_data,
                        metadata = metadata,
                        data = None,
                        timeseries=None)
            lake.data = _get_levels(lake)
            lake.timeseries = lake.data.filter(['date', 'water_level']).set_index('date')
            return lake
        elif source == 'usgs':
            name = df.lake_name[0]
            id_No = df.id_No[0]
            url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/prod/glld/usgsdate/?idNo={}'.format(
                id_No)
            r = requests.get(url)
            json_decode = r.json()
            datedf = pd.DataFrame().from_records(json_decode, columns = ['lake_name', 'start_date', 'end_date'])
            country = 'USA'
            continent = 'North America'
            original_id = df.site_no[0]
            observation_period = datedf['start_date'][0] + ' -- ' + datedf['end_date'][0]
            latitude = df.dec_lat_va[0]
            longitude = df.dec_long_va[0]
            df_misc = df.drop(['id_No', 'site_no', 'dec_lat_va', 'dec_long_va'], axis = 1)
            misc_data = df_misc.to_dict(orient = 'list')
            for k in misc_data:
                misc_data[k] = misc_data[k][0]
            metadata = df
            lake = Lake(name = name,
                        country = country,
                        continent = continent,
                        source = source,
                        original_id = original_id,
                        id_No = id_No,
                        observation_period = observation_period,
                        latitude = latitude,
                        longitude = longitude,
                        misc_data = misc_data,
                        metadata = metadata,
                        data = None,
                        timeseries=None)
            lake.data = _get_levels(lake)
            lake.timeseries = lake.data.filter(['date', 'water_level']).set_index('date')
            return lake


def _get_levels(lake):
    """
    This function populates the Lake().data attribute with all available lake levels
    Arguments:
        lake(object): must be :class:`Lake` with metadata built from :function:`_lake_meta_constructor`

    Returns:
        Pandas DataFrame

    """
    import requests
    import pandas as pd
    print('Reading lake level records from database...')
    url = 'https://4o8d0ft32f.execute-api.us-east-2.amazonaws.com/prod/glld/data?idNo={}'.format(
        lake.id_No)
    r = requests.get(url)
    json_decode = r.json()
    df = pd.DataFrame().from_records(json_decode, columns = ['id_No', 'date', 'lake_name', 'water_level'])
    return df


class Lake(object):

    def __init__(self, name, country, continent, source, original_id, id_No,
                 observation_period, latitude, longitude, misc_data, metadata, data, timeseries):
        """
        Lake object with associated lake attributes and plotting methods
        Arguments:
            name (str): Lake name
            country (str): Country of lake residence
            continent (str): Continent of lake residence
            source (str): Original database of lake data
            original_id (str): Identifier within original lake database
            id_No (str): Global Lake Level Database identification number
            observation_period (str): Date range of accessible water level data
            latitude (str): Decimal degree latitutde
            longitude (str): Decimal degree longitude
            misc_data (dict): Database-specific metadata
            metadata (DataFrame): Lake metadata as Pandas DataFrame
            data (DataFrame): Lake water level time-series data
        """
        self.name = name
        self.country = country
        self.continent = continent
        self.source = source
        self.original_id = original_id
        self.id_No = id_No
        self.observation_period = observation_period
        self.latitude = latitude
        self.longitude = longitude
        self.misc_data = misc_data
        self.metadata = metadata
        self.data = data
        self.timeseries = timeseries


    def plot_mapview(self, show=True, out_path=None, zoom=None, provider=None, return_gdf=False, force_contextily=False, *args, **kwargs):
        """
        Plot map-style overview of lake location using [geopandas]() and [contextily]()
        Arguments:
            show (bool): Flag to determine whether matplotlib.pyplot.show() is called (True) or axis object is
            returned (False)
            out_path (str): If supplied, figure will be saved to filepath
            zoom (int): contextily zoom level
            provider ():
            return_gdf (bool): Returns GeoDataFrame if True
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            ax: matplotlib ax object

        """
        from lakepy.utils import _isnotebook
        import geopandas as gpd
        import contextily as ctx
        from shapely.geometry import Point
        import matplotlib.pyplot as plt

        if _isnotebook() == False or force_contextily == True:
            if self.metadata.source[0] == "usgs":
                gdf = gpd.GeoDataFrame(self.metadata, crs="epsg:4269", geometry=[Point(float(self.longitude),
                                                                      float(self.latitude))])

            elif self.metadata.source[0] == "hydroweb":
                gdf = gpd.GeoDataFrame(self.metadata, crs="epsg:4326", geometry=[Point(float(self.longitude),
                                                                      float(self.latitude))])

            elif self.metadata.source[0] == "grealm":
                gdf = gpd.GeoDataFrame(self.metadata, crs="epsg:4326", geometry=[Point(float(self.longitude),
                                                                      float(self.latitude))])
            else:
                gdf = None
            fig, ax = plt.subplots(1, 1)
            temp = gdf.to_crs("epsg:3857")
            temp.plot(*args, **kwargs, alpha = .5, ax = ax, color = 'red')
            if zoom != None and provider != None:
                ctx.add_basemap(ax, source = provider, zoom = zoom)
            elif provider != None:
                ctx.add_basemap(ax, source = provider)
            elif zoom != None:
                ctx.add_basemap(ax, zoom=zoom)
            else:
                ctx.add_basemap(ax)

            ax.set_title(str(self.id_No) + " : " + self.name)
            if out_path:
                plt.savefig(out_path)
            if show == True:
                plt.show()
            elif return_gdf == True:
                return gdf
            else:
                return ax
        else:
            import leafmap.foliumap as leafmap
            from IPython.display import display
            import warnings
            warnings.simplefilter(action='ignore', category=FutureWarning)
            gdf = gpd.GeoDataFrame(self.metadata, crs="epsg:4326", geometry=[Point(float(self.longitude),
                                                                                   float(self.latitude))])
            m = leafmap.Map(center=[float(self.latitude), float(self.longitude)], zoom=11, google_map="HYBRID") # center=[lat, lon]
            m.add_gdf(gdf, zoom_to_layer=False,layer_name=self.name)
            display(m)

    def plot_timeseries(self, how='plotly', color="blue", show=True,
                        date_start=None, date_end=None, jupyter=False, *args, **kwargs):
        """
        Plot timeseries of lake water level data
        Arguments:
            how (str): Which method of plotting to use. Plotly (default), Matplotlib, or Seaborn.
            color (str): Color of lineplot, cannot be passed to Plotly.
            show (bool): If True, display figure, else return `ax` object
            date_start (str): The beginning of the desired plotting date range supplied as %Y-%m-%d string.
            date_end (str): The end of the desired plotting date range supplied as %Y-%m-%d string.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            NoneType or ax (optional): Time-series plotted through plotly in web browser. if `how` argument is
                                        specified, returns matplotlib ax object


        """
        import matplotlib.ticker as ticker
        import matplotlib.dates as mdates
        from matplotlib.dates import DateFormatter
        from matplotlib.dates import AutoDateLocator
        from matplotlib.dates import AutoDateFormatter
        import plotly.io as pio
        import plotly.express as px
        import seaborn as sns; sns.set_style('darkgrid')
        import pandas as pd
        import matplotlib.pyplot as plt
        import warnings
        from lakepy.utils import _validate
        from lakepy.utils import _isnotebook
        if date_start and date_end:
            _validate(date_start)
            _validate(date_end)

            self.data.date = pd.to_datetime(self.data.date)
            self.data = self.data[(self.data['date'] > pd.Timestamp(date_start)) & (self.data['date'] < pd.Timestamp(
                date_end))]
        elif date_start is None and date_end is None:
            pass
        else:
            raise ValueError('date_start and date_end params must both be None or strings with date format "%Y-%m-%d"')
        if how == 'plotly':
            if jupyter == True or _isnotebook() == True:
                pio.renderers.default = "notebook"
            else:
                pio.renderers.default = "browser"
            plot = px.line(self.timeseries, title = str(self.id_No)+ ": " + self.name)
            plot.update_yaxes(title_text='Water Level (m)')

            if color != "blue":
                warnings.warn('Cannot specify color for plotly style plots, use how = "seaborn" or "matplotlib" to '
                              'pass color', category = RuntimeWarning)
            plot.update_xaxes(
                rangeslider_visible = True,
                rangeselector = dict(
                    buttons = list([
                        dict(count = 1, label = "1m", step = "month", stepmode = "backward"),
                        dict(count = 6, label = "6m", step = "month", stepmode = "backward"),
                        dict(count = 1, label = "YTD", step = "year", stepmode = "todate"),
                        dict(count = 1, label = "1Y", step = "year", stepmode = "backward"),
                        dict(count = 5, label = "5Y", step = "year", stepmode = "backward"),
                        dict(count = 10, label = "10Y", step = "year", stepmode = "backward"),
                        dict(step = "all"),
                    ])), type = "date")
            plot.show()

        else:
            fig, ax = plt.subplots(1, 1)
            ax.xaxis.set_major_locator(AutoDateLocator())
            fig.autofmt_xdate()
            ax.set_title(str(self.id_No) + " : " + self.name)
            ax.set_ylabel('Water Level [m]')
            ax.set_xlabel('Date')

            if how == 'seaborn':
                sns.lineplot(data = self.timeseries, ax = ax, color = color, *args, **kwargs)
            elif how == 'matplotlib':
                plt.plot(self.timeseries, c = color, *args,
                        **kwargs, label='Water Level')
                plt.legend()
                # plt.xticks(rotation = 45, ha = 'right')
            else:
                raise SyntaxError("'how' parameter must be 'plotly', 'seaborn', or 'matplotlib'")
            if show == True:
                plt.show()
            else:
                return ax
if __name__ == '__main__':
    texoma = search(id_No = 1104)
    texoma.plot_mapview()