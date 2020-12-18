def search(name=None, source=None, id_No=None):
    from sqlalchemy import create_engine
    from sqlalchemy import text
    import pandas as pd
    import warnings
    cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
    secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
    database = 'GlobalLakeLevel'
    safe_name = text(name)

    sql_engine = create_engine('mysql+pydataapi://',
                               connect_args={
                                   'resource_arn': cluster_arn,
                                   'secret_arn': secret_arn,
                                   'database': database}).connect()
    if id_No:
        df_lake = pd.read_sql('select * from reference_ID where id_No like :id',
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
        print('Search Result: \'{}\' has more than 1 Result. Showing the {} most relevant results. Specify \'id_No\'.'.format(safe_name, len(df_lake)))
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
            id = df.id_No[0]
            observation_period = df['Satellite Observation Period'][0]
            lake = Lake(name=name,
                        country = country,
                        continent=continent,
                        source = source,
                        original_id = original_id,
                        id = id,
                        observation_period = observation_period,
                        latitude = None,
                        longitude = None)
            return lake

        elif source == 'hydroweb':
            name = df.lake_name[0]
            id = df.id_No[0]
            country = df.country[0]
            original_id = df.identifier[0]
            observation_period = df.start_date[0] + ' -- ' + df.end_date[0]
            latitude = df.latitude[0]
            longitude = df.longitude[0]
            lake = Lake(name=name,
                        country = country,
                        continent=None,
                        source = source,
                        original_id = original_id,
                        id = id,
                        observation_period = observation_period,
                        latitude = latitude,
                        longitude = longitude)
            return lake
        # elif source == 'usgs':


class Lake(object):
    """
    blump
    """
    def __init__(self, name, country, continent, source, original_id, id,
             observation_period, latitude, longitude):
        """constructor"""
        self.name = name
        self.country = country
        self.continent = continent
        self.source = source
        self.original_id = original_id
        self.id = id
        self.observation_period = observation_period
        self.latitude = latitude
        self.longitude = longitude


if __name__ == '__main__':
    # import pprint
    my_lake = search('possum king')
    # pprint.pprint(df)
    # my_lake = lake_meta_constructor(df)