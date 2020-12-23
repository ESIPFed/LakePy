def search(name=None, source=None, id_No=None, markdown=False):
    """
    Main search function for querying the Global Lake Level Database
    :param name: Name of Lake or Reservoir. Be sure to use proper spelling. Wildcards (%) are allowed,
    as is any MySQL 5.7 syntax
    :type name: str
    :param source: Lake water level source flag, accepted values are "usgs", "grealm", or "hydroweb"
    :type source: str
    :param id_No: Global Lake Level Database identification number,
    :type id_No: str or int
    :return: Lake() object
    """
    import pandas as pd
    import requests
    import warnings
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
            print(df_unpacked.to_string())
        lake_object = _lake_meta_constructor(df_unpacked)
        return lake_object


def _lake_meta_constructor(df):
    """
    This function populates the Lake() object with metadata
    :param df: Pandas DataFrame of lake metadata from search()
    :type df: Pandas DataFrame
    :return: Lake() object with associated metadata
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
            dataframe = df
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
                        dataframe = dataframe,
                        data = None)
            lake.data = _get_levels(lake)
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
            dataframe = df

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
                        dataframe = dataframe,
                        data = None)
            lake.data = _get_levels(lake)
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
            dataframe = df
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
                        dataframe = dataframe,
                        data = None)
            lake.data = _get_levels(lake)
            return lake


def _get_levels(lake):
    """
    This function populates the Lake().data attribute with all available lake levels
    :param lake: must be of Lake() object with metadata built from _lake_meta_constructor
    :type lake: class Lake()
    :return:
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
    """

    """

    def __init__(self, name, country, continent, source, original_id, id_No,
                 observation_period, latitude, longitude, misc_data, dataframe, data):
        """
        Lake() constructor
        :param name: Lake name
        :type name: str
        :param country: Country of lake residence
        :type country: str
        :param continent: Continent of lake residence
        :type continent: str
        :param source: Original database of lake data
        :type source: str
        :param original_id: Original identifier of lake
        :type original_id: str
        :param id_No: GLLD identification number
        :type id_No: int
        :param observation_period: Range of water level data
        :type observation_period: str
        :param latitude: Decimal degree latitude
        :type latitude: str
        :param longitude: Decimal degree longitude
        :type longitude: str
        :param misc_data: Database-specific metadata
        :type misc_data: dict
        :param dataframe: Lake metadata as Pandas DataFrame
        :type dataframe: pandas.DataFrame()
        :param data: Lake water level timeseries data
        :type data: pandas.DataFrame()
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
        self.dataframe = dataframe
        self.data = data

    def plot_mapview(self, show=True, out_path=None, zoom=None, return_gdf=False, *args, **kwargs):
        """
        Plot map-style overview of lake location using geopandas as contextily
        :param show: Flag to determine whether matplotlib.pyplot.show() is called (True) or axis object is returned (
        False)
        :type show: bool
        :param out_path: If supplied, figure will be saved to local filepath
        :type out_path: str
        :param args: additonal *args to pass to matplotlib.pyplot axis
        :param kwargs: additonal **kwargs to pass to matplotlib.pyplot axis
        :return: matplotlib axis instance if :param show is False
        """
        import geopandas as gpd
        import contextily as ctx
        from shapely.geometry import Point
        import matplotlib.pyplot as plt
        gdf = gpd.GeoDataFrame(self.dataframe, geometry = [Point(float(self.longitude),
                                                                 float(self.latitude))])
        gdf.crs = 'EPSG:4326'
        fig, ax = plt.subplots(1, 1)
        gdf.plot(*args, **kwargs, alpha = .5, ax = ax, color = 'red')
        if zoom:
            ctx.add_basemap(ax, source = ctx.providers.OpenTopoMap, crs = 'EPSG:4326', zoom = zoom)
        else:
            ctx.add_basemap(ax, source = ctx.providers.OpenTopoMap, crs = 'EPSG:4326')
        ax.set_title(str(self.id_No) + " : " + self.name)
        if out_path:
            plt.savefig(out_path)
        if show == True:
            plt.show()
        elif return_gdf == True:
            return gdf
        else:
            return ax

    def plot_timeseries(self, how='plotly', color="blue", show=True,
                        date_start=None, date_end=None, *args, **kwargs):
        """
        Plot timeseries of lake water level data
        :param how: what plotting package to use: "plotly", "seaborn" or "matplotlib"
        :type how: str
        :param color: color to plot timeseries with, must conform with selected package syntax
        :type color: str
        :param show:
        :type show: bool
        :param args: args to pass to matplotlib or seaborn axis
        :param kwargs: kwargs to pass to matplotlib or seaborn axis
        :return: matplotlib axis object, or None
        """
        import matplotlib.ticker as ticker
        import plotly.io as pio
        import plotly.express as px
        import seaborn as sns
        import pandas as pd
        import matplotlib.pyplot as plt
        import warnings
        from lakepy.utils import _validate
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
            pio.renderers.default = "browser"
            plot = px.line(self.data, x = 'date', y = 'water_level', title = str(self.id_No)
                                                                             + ": " + self.name)
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
            ax.xaxis.set_major_locator(ticker.AutoLocator())
            ax.set_title(str(self.id_No) + " : " + self.name)
            ax.set_ylabel('Water Level [m]')
            ax.set_xlabel('Date')
            if how == 'seaborn':
                sns.set_style('whitegrid')
                sns.lineplot(data = self.data, x = "date", y = "water_level", ax = ax, color = color, *args, **kwargs)
            elif how == 'matplotlib':
                ax.plot(self.data.date, self.data.water_level, color = color, *args,
                        **kwargs)
                plt.xticks(rotation = 45, ha = 'right')
            else:
                raise SyntaxError("'how' parameter must be 'plotly', 'seaborn', or 'matplotlib'")
            if show == True:
                plt.show()
            else:
                return ax


if __name__ == '__main__':
    ay = search(name='mead', source = 'hydroweb')
    print(ay.data)
    ay.plot_timeseries()
    ay.plot_timeseries(how='matplotlib')
    ay.plot_timeseries(how='seaborn')
    ay.plot_mapview()
    print('done!')
