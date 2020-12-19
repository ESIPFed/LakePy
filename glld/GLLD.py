def search(name=None, source=None, id_No=None):
    from sqlalchemy import create_engine
    from sqlalchemy import text
    import pandas as pd
    import warnings
    cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
    secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
    database = 'GlobalLakeLevel'
    if name:
        safe_name = text(name)

    sql_engine = create_engine('mysql+pydataapi://',
                               connect_args={
                                   'resource_arn': cluster_arn,
                                   'secret_arn': secret_arn,
                                   'database': database}, pool_pre_ping=True).connect()
    if id_No:
        df_lake = pd.read_sql('select * from reference_ID where id_No = :id',
                              con=sql_engine, params={'id': id_No})
    elif source:
        df_lake = pd.read_sql('select * from reference_ID where lake_name like :name and source like :source',
                              con=sql_engine, params={'name': safe_name, 'source': source})
    else:
        df_lake = pd.read_sql('SELECT * FROM reference_ID WHERE MATCH (lake_name) AGAINST (:name IN NATURAL LANGUAGE '
                              'MODE) LIMIT 0, 5',
                              con=sql_engine, params={'name': safe_name})

    if len(df_lake) < 1:
        raise RuntimeError('No results returned. Please adjust search parameters or see documentation')
    if len(df_lake) > 1:
        print('Search Result: \'{}\' has more than 1 Result. Showing the {} most relevant results.\n'
              'Specify \'id_No\' or narrow search name.'.format(safe_name, len(df_lake)))
        print(df_lake.filter(['id_No', 'source', 'lake_name']).to_markdown())

    elif len(df_lake) == 1:
        meta_series = df_lake['metadata'].map(eval).apply(pd.Series)
        df_unpacked = pd.merge(left=df_lake,
                               right=meta_series.drop(['source', 'lake_name'],
                               axis=1),
                               left_index=True,
                               right_index=True,
                               how='outer').drop('metadata', axis=1)
        lake_object = _lake_meta_constructor(df_unpacked)

        return lake_object

    sql_engine.close()


def _lake_meta_constructor(df):
    from sqlalchemy import create_engine
    from sqlalchemy import text
    import pandas as pd
    import warnings
    cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
    secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
    database = 'GlobalLakeLevel'

    sql_engine = create_engine('mysql+pydataapi://',
                               connect_args={
                                   'resource_arn': cluster_arn,
                                   'secret_arn': secret_arn,
                                   'database': database}).connect()
    import pandas as pd
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
            misc_data = {'Type' : df.Type[0], 'Resolution': df.Resolution[0]}
            dataframe = df
            lake = Lake(name=name,
                        country = country,
                        continent=continent,
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
            misc_data = {'basin' : df.basin[0], 'status': df.status[0]}
            dataframe = df
            lake = Lake(name=name,
                        country = country,
                        continent=None,
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
            df_new = pd.read_sql('select lake_name, min(date), max(date) from lake_water_level where lake_name = '
                                 ':name', con = sql_engine, params = {'name': df.lake_name[0]})
            name = df.lake_name[0]
            id_No = df.id_No[0]
            country = 'USA'
            continent = 'North America'
            original_id = df.site_no[0]
            observation_period = df_new['min(date)'][0] + ' -- ' + df_new['max(date)'][0]
            latitude = df.dec_lat_va[0]
            longitude = df.dec_long_va[0]
            df_misc = df.drop(['id_No', 'site_no', 'dec_lat_va', 'dec_long_va'], axis = 1)
            misc_data = df_misc.to_dict(orient='list')
            for k in misc_data:
                misc_data[k] = misc_data[k][0]
            dataframe = df
            lake = Lake(name=name,
                        country = country,
                        continent=continent,
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

    :param lake: must be of class Lake()
    :return:
    """
    from glld.utils import _printProgressBar
    from sqlalchemy import create_engine
    import pandas as pd
    import numpy as np
    cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
    secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
    database = 'GlobalLakeLevel'
    chunksize = 500
    id_No = lake.id_No
    sql_engine = create_engine('mysql+pydataapi://',
                               connect_args={
                                   'resource_arn': cluster_arn,
                                   'secret_arn': secret_arn,
                                   'database': database}).connect()
    df_status = pd.read_sql('select id_No, count(*) as count from lake_water_level where id_No = :id_No',
                            con = sql_engine,
                            params = {'id_No': id_No})
    rownum = df_status.loc[0, "count"]
    space = np.arange(0, rownum, chunksize)
    space = space.tolist()
    space.append(rownum)
    df_list = []
    _printProgressBar(0, len(space), prefix='Building Lake', suffix='Complete', length=50)
    for count, i in enumerate(space, 0):
        search_df = pd.read_sql('select * from lake_water_level where id_No = :id_No limit {}, {}'.format(i, chunksize),
                                con = sql_engine,
                                params = {'id_No': id_No})
        df_list.append(search_df)
        _printProgressBar(count + 1, len(space), prefix = 'Building Lake', suffix = 'Complete', length = 50)
    df = pd.concat(df_list).sort_values('date')
    return df


class Lake(object):
    """
    blump
    """
    def __init__(self, name, country, continent, source, original_id, id_No,
             observation_period, latitude, longitude, misc_data, dataframe, data):
        """constructor"""
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
    @staticmethod
    def check_connection(self):
        from sqlalchemy import create_engine
        cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
        secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
        database = 'GlobalLakeLevel'
        try:
            create_engine('mysql+pydataapi://',
                                       connect_args = {
                                           'resource_arn': cluster_arn,
                                           'secret_arn': secret_arn,
                                           'database': database}, pool_pre_ping = True).connect()
            connected = True
            return connected
        except Exception as e:
            connected = False
            return connected

    def plot_mapview(self, show=True, out_path=None, *args, **kwargs):
        import geopandas as gpd
        import contextily as ctx
        from shapely.geometry import Point
        import matplotlib.pyplot as plt
        gdf = gpd.GeoDataFrame(self.dataframe, geometry = [Point(self.longitude.astype(float), self.latitude.astype(
            float))])
        gdf.crs = 'EPSG:4326'
        fig, ax = plt.subplots(1,1)
        gdf.plot(*args, **kwargs, alpha=.5, ax=ax, color='red')
        ctx.add_basemap(ax, source = ctx.providers.OpenTopoMap, crs = 'EPSG:4326')
        ax.set_title(self.id_No.astype(str) + " : " + self.name)
        if out_path:
            plt.savefig(out_path)
        if show == True:
            plt.show()
        else:
            return ax

    def plot_timeseries(self, how='plotly', color="blue", show = True, *args, **kwargs):
        import matplotlib.ticker as ticker
        import plotly.io as pio
        import plotly.express as px
        import seaborn as sns
        import matplotlib.pyplot as plt
        import warnings
        if how == 'plotly':
            pio.renderers.default = "browser"
            plot = px.line(self.data, x='date', y = 'water_level', title = self.id_No.astype(str)
                                                                                         + ": " + self.name)
            if color:
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
            ax.set_title(self.id_No.astype(str) + " : " + self.name)
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
    lake = search(name='Ayakkum')

    # lake.plot_timeseries(how='plotly', color = 'red')
    # lake.plot_mapview()

