# chess_models / models / __init__ . py
2 from .tournament import ( Tournament , RankingSystemClass ) # noqa F401
3 # the tag noqa informs fake8 to ignore the fact that
4 # we are importing a method that is never used in the file
5
6 # those classes exported in __init__ . py
7 # may be import as
8 # from chess_models . models import Tournament
9 # instead of
10 # from chess_models . models . Tournament import Tournament