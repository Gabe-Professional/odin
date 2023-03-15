import os

from odin.credentials.config import BackboneProperties, Credentials
import odin.credentials.config as config
import logging
logger = logging.getLogger(__name__)


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


def test_creds():
    creds = Credentials()

    print(creds)

def test_backbone_props():
    bp = BackboneProperties()
    logger.info(bp.keys())

    print(bp)


    # assert "DEV_EXPORT_HOST" in bp.keys()
    # assert "DEV_EXPORT_PORT" in bp.keys()