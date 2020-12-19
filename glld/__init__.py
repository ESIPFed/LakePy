cluster_arn = 'arn:aws:rds:us-east-2:003707765429:cluster:esip-global-lake-level'
secret_arn = 'arn:aws:secretsmanager:us-east-2:003707765429:secret:esip-lake-level-enduser-qugKfY'
database = 'GlobalLakeLevel'

from .GLLD import search
from .GLLD import Lake
