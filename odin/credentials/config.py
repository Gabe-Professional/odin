import os
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import logging
<<<<<<< HEAD
# import six
logger = logging.getLogger(__name__)
# import json




#
#
# # def get_creds():
# #     cp = os.path.expanduser(os.path.join('~/.cred', 'ODIN_CONFIG', 'odin_backbone_properties.json'))
# #     with open(cp, 'r') as f:
# #         data = json.load(f)
# #     return data
#
#
# # todo: try and replicate the pysigma way of doing this...
#
#
#
#
# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]
#
# def load_environment(prefix=None):
#     logger.debug("Loading From Environment Variables...")
#     logger.debug("prefix: {}".format(prefix))
#     if prefix is None:
#         prefix = "SIGMA_"
#     else:
#         prefix = "SIGMA_" + prefix + "_"
#     keys = {
#         key[len(prefix):].upper(): v
#         for key, v in os.environ.items()
#         if key.startswith(prefix)
#         }
#
#     return keys
#
#
# def load_stuff_from_file(filename):
#     _file = os.path.expanduser(filename)
#     logger.debug("Loading From File: {}".format(_file))
#     if not os.path.exists(_file):
#         logger.warning("Expected configuration file {} does not exist".format(_file))
#         return {}
#
#     config = ConfigParser.ConfigParser()
#     config.read(_file)
#     credDict = {}
#
#     logger.debug("Loading Properties from File: {}".format(_file))
#     for section in config.sections():
#         for key, val in config.items(section):
#             try:
#                 val = json.loads(val)
#             except:
#                 pass
#             credDict["{}_{}".format(str(section).upper(), str(key).upper())] = val
#     return credDict
#
#
# @six.add_metaclass(Singleton)
# class Properties(object):
#     _file = ""
#
#     @property
#     def file(self):
#         dir = os.path.expanduser(os.environ.get("ODIN_CONFIG", "~/.cred"))
#         return os.path.join(dir, self._file)
#
#     def __init__(self):
#         logger.debug("Constructing Singleton Properties for {}".format(self.file))
#         self._credDict = load_stuff_from_file(self.file)
#         self._credDict.update(load_environment(self._prefix))
#         logger.debug(str(self))
#
#     def __getitem__(self, item):
#         return self._credDict[item]
#
#     def keys(self):
#         return self._credDict.keys()
#
#     def __str__(self):
#         pretty_keys = []
#         cat = ''
#         for k in list(self.keys()):
#             c = '_'.join(k.split('_')[:2])
#             if cat != c:
#                 pretty_keys.append("")
#             pretty_keys.append(k)
#             cat = c
#         return "Property keys:\n\t{}".format('\n\t'.join(pretty_keys))
#
#
# class Credentials(Properties):
#     _file = "credentials"
#     _prefix = "CREDS"
#
#
# class BackboneProperties(Properties):
#     _file = "backbone.properties"
#     _prefix = "BACKBONE"
#
=======
import six
import json
logger = logging.getLogger(__name__)


class AirTable:
    file = os.path.expanduser('~/.cred/ODIN_CONFIG/at_api.json')

    def get_base_names(self):
        with open(self.file, 'r') as f:
            base_data = json.load(f)['base_names']
            base_names = list(base_data.keys())
            return base_names

    def get_headers(self, base_name):
        with open(self.file, 'r') as f:
            data = json.load(f)
            base_data = data['base_names'][base_name]
            cred_data = data['data']

            header_data = base_data | cred_data

        return header_data


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def load_environment(prefix=None):
    logger.debug("Loading From Environment Variables...")
    logger.debug("prefix: {}".format(prefix))

    if prefix is None:
        prefix = "ODIN_"
    else:
        prefix = "ODIN_" + prefix + "_"
    # for k, v in os.environ.items():
    #     print(k)
    keys = {
        key[len(prefix):].upper(): v
        for key, v in os.environ.items()
        if key.startswith(prefix)
        }
    return keys


def load_stuff_from_file(filename):
    _file = os.path.expanduser(filename)
    logger.debug("Loading From File: {}".format(_file))
    if not os.path.exists(_file):
        logger.warning("Expected configuration file {} does not exist".format(_file))
        return {}

    config = ConfigParser.ConfigParser()
    config.read(_file)

    credDict = {}

    logger.debug("Loading Properties from File: {}".format(_file))
    for section in config.sections():
        for key, val in config.items(section):
            try:
                val = json.loads(val)
            except:
                pass
            credDict["{}_{}".format(str(section).upper(), str(key).upper())] = val
    return credDict


@six.add_metaclass(Singleton)
class Properties(object):
    _file = ""
    # _prefix = ""

    @property
    def file(self):



        directory = os.path.expanduser(os.environ.get("ODIN_CONFIG", "~/.cred/ODIN_CONFIG"))
        return os.path.join(directory, self._file)

    def __init__(self):
        logger.debug("Constructing Singleton Properties for {}".format(self.file))


        self._credDict = load_stuff_from_file(self.file)
        self._credDict.update(load_environment(self._prefix))

        logger.debug(str(self))

    def __getitem__(self, item):

        return self._credDict[item]

    def keys(self):
        return self._credDict.keys()

    def __str__(self):
        pretty_keys = []
        cat = ''
        for k in list(self.keys()):
            c = '_'.join(k.split('_')[:2])
            if cat != c:
                pretty_keys.append("")
            pretty_keys.append(k)
            cat = c
        return "Property keys:\n\t{}".format('\n\t'.join(pretty_keys))


class Credentials(Properties):
    _file = "credentials"
    _prefix = "CREDS"


class BackboneProperties(Properties):
    _file = "backbone.properties"
    _prefix = "BACKBONE"



# todo: get rid of this soon...
# def get_creds_file(file_path):
#     return file_path
# class Properties:
#     def __init__(self):
#         fp = os.path.expanduser('~/.cred/ODIN_CONFIG/odin_backbone_properties.json')
#         if not os.path.exists(fp):
#             print(f'THE FILE {fp} DOES NOT EXIST...PLEASE SET UP YOUR CREDENTIALS')
#         elif os.path.exists(fp):
#             print('LOADING YOUR CREDENTIALS FILE')
#             self.file = fp
#             get_creds_file(self.file)
#         else:
#             print('SOMETHING ELSE WENT WRONG...')

# class Credentials(Properties):
#
#     def get_creds(self, cluster):
#         with open(Properties().file, 'r') as f:
#             print(f'GETTING POSTGRES {cluster} CREDENTIALS')
#             creds = json.load(f)[cluster]
#
#         return creds
>>>>>>> bd6535f45e11f7c51cf8ff423e518968868dabe4
