import odin.collect.postgres as pg


def test_create():
    pg.create(cluster='DEV')