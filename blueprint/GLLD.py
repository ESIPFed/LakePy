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
                                   'database': database}).connect()
    if id_No:
        df_lake = pd.read_sql('select * from reference_ID where id_No = :id',
                              con=sql_engine, params={'id': id_No})
    elif source:
        df_lake = pd.read_sql('select * from reference_ID where lake_name like :name and source like :source',
                              con=sql_engine, params={'name': safe_name, 'source': source})
    else:
        df_lake = pd.read_sql('SELECT * FROM reference_ID WHERE MATCH (lake_name) AGAINST (:name IN NATURAL LANGUAGE MODE) LIMIT 0, 5',
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
        lake_object = lake_meta_constructor(df_unpacked)

        return lake_object

    sql_engine.close()


def lake_meta_constructor(df):
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
            # df = df.query('source == "grealm')
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
            lake.data = get_levels(lake)
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
            lake.data = get_levels(lake)
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
            lake.data = get_levels(lake)
            return lake

def get_levels(lake):
    """

    :param lake: must be of class Lake()
    :return:
    """
    from utils import
    from sqlalchemy import create_engine
    import pandas as pd
    import numpy as np
    cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
    secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
    database = 'GlobalLakeLevel'
    chunksize = 500
    id_No = '1220'
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
    for i in space:
        search_df = pd.read_sql('select * from lake_water_level where id_No = :id_No', con = sql_engine,
                                params = {'id_No': id_No})
        df_list.append(search_df)
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



if __name__ == '__main__':
    # import pprint
    possum = search('possum', id_No='1220')
