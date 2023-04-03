import os

<<<<<<< HEAD
from odin.credentials.config import BackboneProperties, Credentials
import odin.credentials.config as config
import logging
logger = logging.getLogger(__name__)


=======
from odin.credentials.config import Properties, Credentials, BackboneProperties
import odin.credentials.config as config
import logging
import odin.credentials.config as conf
logger = logging.getLogger(__name__)


def test_backbone_props():
    bp = BackboneProperties()
    assert "DEV_POSTGRES_HOST" in bp.keys()
    assert "DEV_POSTGRES_PORT" in bp.keys()


# todo: working test creds function
# def test_credentials():
#     fp = Properties()
#     assert os.path.exists(fp.file)


def test_postgres():
    creds = Credentials().get_creds('DEV')
    assert set(creds.keys()) == {'POSTGRES_HOST', 'POSTGRES_PORT',
                                 'POSTGRES_DBNAME', 'POSTGRES_USER', 'POSTGRES_PASSWORD'}



# # todo: need to fix the stuff below
# def test_get_base_names():
#     at = conf.AirTable()
#     base_names = at.get_base_names()
#     assert type(base_names) == list
#     assert len(base_names) > 0
#
#
# def test_get_headers():
#
#     at = conf.AirTable()
#     creds = at.get_headers('ODIN: English')
#     assert creds.keys() == {'base_id', 'api_key', 'table_names', 'api_key', 'url'}
#     assert os.path.exists(at.file)








>>>>>>> bd6535f45e11f7c51cf8ff423e518968868dabe4
# def test_get_creds():
#     creds = config.get_creds()
#     assert type(creds) == dict
#     assert set(creds.keys()) == {'DEV'}

# todo: try and replicate the pysigma way of doing this.


# def test_backbone_props():
#     bp = Backbone_Properties()
#     file = os.path.abspath(bp.file)
#     print(bp.keys())
#     # print(bp.file)


<<<<<<< HEAD
def test_creds():
    creds = Credentials()

    print(creds)

def test_backbone_props():
    bp = BackboneProperties()
    logger.info(bp.keys())

    print(bp)
=======
# def test_backbone_props():
#     bp = BackboneProperties()
#     logger.info(bp.keys())
#
#     print(bp)
>>>>>>> bd6535f45e11f7c51cf8ff423e518968868dabe4


    # assert "DEV_EXPORT_HOST" in bp.keys()
    # assert "DEV_EXPORT_PORT" in bp.keys()