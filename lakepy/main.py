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
                        timeseries = None,
                        datum = ('meters above TOPEX/Poseidon ellipsoid'),
                        mean = None,
                        median = None,
                        mode = None)
            lake.data = _get_levels(lake)
            lake.timeseries = lake.data.filter(['date', 'water_level']).set_index('date')
            lake.timeseries.index = pd.to_datetime(lake.timeseries.index)
            lake.mean = lake.data['water_level'].mean()
            lake.median = lake.data['water_level'].median()
            lake.mode = lake.data['water_level'].mode()
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
                        timeseries=None,
                        datum = ('meters above WGS84 ellipsoid'),
                        mean = None,
                        median = None,
                        mode = None)
            lake.data = _get_levels(lake)
            lake.timeseries = lake.data.filter(['date', 'water_level']).set_index('date')
            lake.timeseries.index = pd.to_datetime(lake.timeseries.index)
            lake.mean = lake.data['water_level'].mean()
            lake.median = lake.data['water_level'].median()
            lake.mode = lake.data['water_level'].mode()
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
                        timeseries=None,
                        datum = [''],
                        mean = None,
                        median = None,
                        mode = None)
            lake.data = _get_levels(lake)
            lake.timeseries = lake.data.filter(['date', 'water_level']).set_index('date')
            lake.timeseries.index = pd.to_datetime(lake.timeseries.index)
            lake.mean = lake.data['water_level'].mean()
            lake.median = lake.data['water_level'].median()
            lake.mode = lake.data['water_level'].mode()
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
                 observation_period, latitude, longitude, misc_data, metadata, data, timeseries, datum, mean, median, \
                                                                                                     mode):
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
        self.datum = datum
        self.mean = mean
        self.median = median
        self.mode = mode



    def plot_mapview(self, show=True, out_path=None, zoom=None, provider=None, return_gdf=False, force_contextily=False, *args, **kwargs):
        """
        Plot map-style overview of lake location using [geopandas](https://geopandas.org/en/stable/) and [contextily](https://contextily.readthedocs.io/en/latest/)
        Arguments:
            show (bool): Flag to determine whether matplotlib.pyplot.show() is called (True) or axis object is
                returned (False)
            out_path (str): If supplied, figure will be saved to filepath
            zoom (int): contextily zoom level
            provider (str): contextily provider
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
        from matplotlib.dates import AutoDateLocator
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


    def auto_correlation(self, lags = 30, show=True, *args, **kwargs):
        """
        Provides autocorrelation and partial autocorrelation plots to determine the coefficient of correlation
        between two values in the lake level timeseries.

        Args:
            lags (int or array_like): An int or array of lag values, used on horizontal axis. Uses np.arange(lags) when
                lags is an int.
            show (bool): Boolean flag to show plot (True) or return axis (False)
            *args: matplotlib args
            **kwargs: matplotlib kwargs

        Returns:
            NoneType or ax (optional): None if show is True, Matplotlib axis if show is False
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_style('whitegrid')
        from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
        data = self.timeseries
        if data.isnull() is False:
            pass
        else:
            data = data.dropna(how = 'any')
        data['diff'] = data.diff()
        data["diff"].iloc[0] = 0
        if show is True:
            plot_acf(x = data['diff'], lags = lags, title = 'Autocorrelation for {}, Median Time Interval: {}'.format(
                self.name, self.timeseries.index.to_series().diff().median().days + ' days'), *args, **kwargs)
            plt.show()
        else:
            return plot_acf(x = data['diff'], lags = lags, title = 'Autocorrelation for {}, Median Time Interval: {}'.format(
                self.name, self.timeseries.index.to_series().diff().median().days + ' days'), *args, **kwargs)
        if show is True:
            plot_pacf(x = data['diff'], lags = lags, title = 'Partial Autocorrelation for {}, Median Time '
                                                                    'Interval: {}'.format(
                self.name, self.timeseries.index.to_series().diff().median().days + ' days'))
            plt.show()
        else:
            return plot_pacf(x = data['diff'], lags = lags, title = 'Partial Autocorrelation for {}, '
                                                                                 'Median Time '
                                                                    'Interval: {}'.format(
                self.name, self.timeseries.index.to_series().diff().median()))


    def seasonal_decompose(self, model='additive', period=None, show=True):
        """
        Performs seasonal decomposition using moving averages. Plots trend, seasonality, and residual components. [
        See here for more details](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.seasonal_decompose.html)
        Args:
            model (str): Model type: "additive" or "multiplicative" see
                https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.seasonal_decompose.html for more details.
            period (int): Period of the series.
            show (bool): Displays figure if

        Returns:
            NoneType or ax (optional): None if show is True, Matplotlib axis if show is False

        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_style('whitegrid')
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        from statsmodels.tsa.seasonal import seasonal_decompose
        data = self.timeseries
        if period is None:
            period = round(365/self.timeseries.index.to_series().diff().median().days)
        res = seasonal_decompose(data, model = model, period = period)
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (15, 8))
        res.trend.plot(ax = ax1, ylabel = "trend", color='k')
        res.resid.plot(ax = ax2, ylabel = "seasoanlity", color='k')
        res.seasonal.plot(ax = ax3, ylabel = "residual", color='k')
        plt.suptitle('Seasonal Decomposition of {}'.format(self.name), fontsize=24)
        plt.tight_layout()
        if show is True:
            plt.show()
        else:
            return fig

    def check_stationarity(self, ADF=True, KPSS=True, return_params=False):
        """
        Determine stationarity of lake level time series by computing the [Augmented Dickey Fuller Test](
        https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.adfuller.html) and/or the [
        Kwiatkowski-Phillips-Schmidt-Shin](https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.kpss
        .html) test for stationarity.

        Credit for this code goes to [Sivakar Sivarajah](
        https://towardsdatascience.com/most-useful-python-functions-for-time-series-analysis-ed1a9cb3aa8b)
        Args:
            ADF (bool): Computes Augmented Dickey Fuller Test for stationarity.
            KPSS (bool): Computes Kwiatkowski-Phillips-Schmidt-Shin test for stationarity
            return_params (bool): if True and only one method selected (ADF or KPSS), returns test statistics. 8
                terms are packed into one term for ADF, 4 statistics are returned for KPSS.

        Returns:
            NoneType or ax (optional): Test statistics for either ADF or KPSS if return_params is true

        """

        from statsmodels.tsa.stattools import adfuller, kpss
        if ADF is True and KPSS is True and return_params is True:
            raise RuntimeError('One method (KPSS or ADF) must be False for parameters to be returned.')
        if ADF is True:
            result = adfuller(self.timeseries, autolag = 'AIC')
            print('STATIONARITY TEST FOR {}\n'.format(self.name))
            print('ADF Statistic: {}'.format(result[0]))
            print('p-value: {}'.format(result[1]))
            if return_params is True:
                return result
            else:
                if result[1] > 0.05:
                    print('Series is not Stationary')
                else:
                    print('Series is Stationary')
        # KPSS Test
        if KPSS is True:
            stats, p, lags, critical_values = kpss(self.timeseries, 'ct', nlags='auto')
            print('KPSS Test Statistics: {}'.format(stats))
            print('p-value: {}'.format(p))
            if return_params is True:
                return stats, p, lags, critical_values
            else:
                if p < 0.05:
                    print('Series is not Stationary')
                else:
                    print('Series is Stationary')

    def plot_rolling_statistic(self, figsize=None, median=False, show=True):
        """
        Plot rolling statistics for lake water level at a series of window sizes (7, 10, 30, 50). Default statistic
        is mean, set median to True to compute medians.
        Args:
            figsize (tuple): figure size entered as a tuple
            median (bool): Boolean flag, computes the median instead of mean if True
            show (bool):

        Returns:
            NoneType or ax (optional): None if show is True, matplotlib axis object if show is False

        """
        import matplotlib.pyplot as plt
        import seaborn as sns; sns.set_style('darkgrid')
        SMALL_SIZE = 12
        MEDIUM_SIZE = 14
        BIGGER_SIZE = 24
        plt.rc('font', size = MEDIUM_SIZE)  # controls default text sizes
        plt.rc('axes', titlesize = MEDIUM_SIZE)  # fontsize of the axes title
        plt.rc('axes', labelsize = MEDIUM_SIZE)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize = MEDIUM_SIZE)  # fontsize of the tick labels
        plt.rc('ytick', labelsize = MEDIUM_SIZE)  # fontsize of the tick labels
        plt.rc('legend', fontsize = SMALL_SIZE)  # legend fontsize
        plt.rc('figure', titlesize = BIGGER_SIZE)  # fontsize of the figure title
        start = laket.timeseries.index.min()
        end = laket.timeseries.index.max()
        if figsize:
            fig, ax = plt.subplots(figsize = figsize)
        else:
            fig, ax = plt.subplots(figsize=(10,6))
        df = self.timeseries
        if median is False:
            ax.plot(df.loc[start:end], marker = 'o', markersize = 1, linestyle = '-', label = 'ORIGINAL_DATA',
                    linewidth = 1, color = 'k')

            ax.plot(df.rolling(window = 7, center = True).mean().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_5', linewidth = 0.5, color = 'b')

            ax.plot(df.rolling(window = 10, center = True).mean().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_10', linewidth = 0.5, color = 'r')

            ax.plot(df.rolling(window = 30, center = True).mean().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_20', linewidth = 0.5, color = 'y')

            ax.plot(df.rolling(window = 50, center = True).mean().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_50', linewidth = 0.5, color = 'm')
            ax.set_title('Rolling Mean for {}'.format(self.name), fontsize=24)
        else:
            ax.plot(df.loc[start:end], marker = 'o', markersize = 1, linestyle = '-', label = 'ORIGINAL_DATA',
                    linewidth = 1, color = 'k')

            ax.plot(df.rolling(window = 7, center = True).median().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_5', linewidth = 0.5, color = 'b')

            ax.plot(df.rolling(window = 10, center = True).median().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_10', linewidth = 0.5, color = 'r')

            ax.plot(df.rolling(window = 30, center = True).median().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_20', linewidth = 0.5, color = 'y')

            ax.plot(df.rolling(window = 50, center = True).median().loc[start:end], marker = 'o', markersize = 1,
                    linestyle = '--', label = 'ROLLING_WINDOW_SIZE_50', linewidth = 0.5, color = 'm')
            ax.set_title('Rolling Median for {}'.format(self.name), fontsize=24)


        if self.source == 'grealm':
            ax.set_ylabel('Water Level (meters above TOPEX/Poseidon ellipsoid)')
            ax.legend()
        if self.source == 'hydroweb':
            ax.set_ylabel('Water Level (meters above WGS84 ellipsoid')
            ax.legend()
        if self.source == 'usgs':
            ax.set_ylabel('Water Level (ft)')
            ax.legend()
        ax.set_xlabel('Time')
        plt.tight_layout()
        if show is True:
            plt.show()
        else:
            return ax
    def lag_plot(self, nlags=4, figsize=None, show = True):
        """
        Computes the common lag plot, used to investigate patterns in time-series data. [See here for more
        information.](https://www.statisticshowto.com/lag-plot/)
        Args:
            nlags (int or array_like): An int or array of lag values, used on horizontal axis. Uses np.arange(lags)
                when lags is an int.
            figsize (tuple): figure size entered as a tuple

        Returns:
            NoneType or ax (optional): None if show is True, matplotlib axis object if show is False

        """
        import matplotlib.pyplot as plt
        from pandas.plotting import lag_plot
        if figsize is None:
            figsize = (10, 3)
        plt.rcParams.update({'ytick.left': False, 'axes.titlepad': 10})
        fig, axes = plt.subplots(1, nlags, figsize = figsize, sharex = True, sharey = True, dpi = 100)
        for i, ax in enumerate(axes.flatten()[:nlags]):
            lag_plot(self.timeseries, lag = i + 1, ax = ax, c = 'firebrick')
            ax.set_title('Lag ' + str(i + 1))
        plt.suptitle('Lag Plots for {}'.format(self.name))
        plt.tight_layout()
        if show is True:
            plt.show()
        else:
            return fig
    def wavelet_analysis(self, scales=None, wavelet=None, yaxis = 'scale', show=True):
        """
        1D lake water level data analysis with the Scaleogram package by [Alexandre
        Sauvé](https://github.com/alsauve). Utilizes Continuous Wavelet Transforms built on [PyWavelets](
        https://github.com/PyWavelets/pywt). These descriptions are taken from [Alexandre
        Sauvé](https://github.com/alsauve).
        Args:
            scales: an array of float or int >= 1 with increasing values.
                The scale parameter is homogenous with the periodicity of the events
                to be analyzed in the signal.

                The relation between scale ``s`` and corresponding period length ``p`` is:

                    ``p = s / C``

                where ``C`` is the central frequency parameter used to build the wavelet.

                Example: if ``wavelet='cmor1-1.5'`` the name pattern of the wavelet is
                ``nameB-C``, hence ``C=1.5``  and ``period=s/1.5``.

                ``scales`` can be any array of values as long as they are in
                increasing order. Under the hood, plotting is implemented with
                ``pmeshgrid`` which allow to associate reliably for each pixel the
                correct axis coordinates.

                Examples::

                    import numpy as np
                    scales_linear = np.arange(1,200, 2)
                    scales_log    = np.logspace(0,2)

                Online doc about scale:
                    https://github.com/alsauve/scaleogram/tree/master/doc/scale-to-frequency.ipynb
                ** This description comes directly from Scaleogram by [Alexandre
                    Sauvé](https://github.com/alsauve)**
            wavelet: The default wavelet function is Morlay (``cmor1-1.5``) which is a good start
                as a general purpose wavelet because it has a good compromise betwen
                compacity and smoothness in both time and frequency domain.

                Note : for the continuous transform, there is no scaling function
                by contrast with the discrete transform.

                Example::

                    wavelet=pywt.ContinuousWavelet('cmor1-1.5')
            yaxis: selects the Y axis units.
                - [``'period'``] : Convert scales to human readable period values.
                    The period units is the same as the ``time`` input parameter.
                    If time is not provided, periods are in number of samples units.

                - ``'frequency'`` : Converts scales to frequency
                    The frequency unit is depending on the time argument value.
                    If time is not provided, the frequency represents the number of
                    oscillations per sample.

                    In this mode ``yscale`` is set to ``'log'`` by default (if not provided).

                - ``'scale'`` : display the wavelet scales parameter.

        Returns:
            NoneType or ax (optional): None if show is True, scaleogram axis object if show is False

        """
        import scaleogram as scg
        import numpy as np
        import matplotlib.pyplot as plt
        if scales is None:
            scales = np.logspace(.1, 2.5, num = 600, dtype = np.int64)
        if wavelet:
            scg.set_default_wavelet(wavelet)
        else:
            scg.set_default_wavelet('cmor1-3.5')
        ax = scg.cws(self.timeseries.iloc[:,0], scales = scales, yaxis = yaxis)
        if show is True:
            plt.show()
        else:
            return ax





if __name__ == '__main__':
    laket = search(id_No = 2034)
    laket.check_stationarity()
    laket.plot_rolling_statistic()
    laket.auto_correlation(lags = 20)
    laket.seasonal_decompose()
    laket.wavelet_analysis()