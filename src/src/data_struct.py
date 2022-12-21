from enum import Enum

Person = tuple
Query = dict
QueryResult = list[Person]
Id = str
Score = float

class ReferenceType(Enum):
    USER = 0
    QUERY = 1

class People:
    def __init__(self, csvName: str) -> None:
        pass

    def getFields() -> tuple:
        pass

    def getPerson(id) -> Person:
        pass

    def poseQuery(query: Query) -> QueryResult:
        pass

class Users:
    def __init__(self, csvName: str) -> None:
        pass

    def getUser(index: int) -> Id:
        pass

    def addUser(id: Id) -> bool:
        pass

class Queries:
    def __init__(self) -> None:
        pass

    def getQuery(id: Id) -> Query:
        pass

    def addQuery(query: Query) -> bool:
        pass

class UtilityMatrix:
    def __init__(self, csvName: str) -> None:
        pass

    def getScore(userId: Id, queryId: Id) -> Score:
        pass

    def setScore(userId: Id, queryId: Id, score: Score) -> None:
        pass

    def hasRates(id: Id, type: ReferenceType) -> bool:
        pass

    def addUser(id: Id) -> bool:
        pass

    def addQuery(id: Id) -> bool:
        pass