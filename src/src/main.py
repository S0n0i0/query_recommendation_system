from data_struct import *

baseFilesPath = "."

a = People(baseFilesPath + "/files/people.csv")
b = Users(baseFilesPath + "/files/users.csv")
c = Queries(baseFilesPath + "/files/queries.csv")
d = UtilityMatrix(baseFilesPath + "/files/um.csv")

print(a)
print(b)
print(c)
print(d)