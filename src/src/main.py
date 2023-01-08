from data_struct import *
import pandas
import random

baseFilesPath = "../data/"

a = People.fromCsv(baseFilesPath + "people.csv")
b = Users.fromCsv(baseFilesPath + "users.csv")
c = Queries.fromCsv(baseFilesPath + "queries.csv")
d = UtilityMatrix.fromCsv(baseFilesPath + "utility_matrix.csv")

print(a)
print(b)
print(c)
print(d)