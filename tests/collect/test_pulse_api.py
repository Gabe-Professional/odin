from odin.collect.pulse_api import Api


def test_api_create():
    with Api.Create('DEV') as api:
        encoding = api.make_request(text='this is a sentence of test text to get a vector', method='post')
        assert len(encoding) > 0
        assert type(encoding) is not None
