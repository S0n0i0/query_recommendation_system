from data_struct import *

baseFilesPath = "."

a = People.fromCsv(baseFilesPath + "/files/people.csv")
b = Users.fromCsv(baseFilesPath + "/files/users.csv")
c = Queries.fromCsv(baseFilesPath + "/files/queries.csv")
d = UtilityMatrix.fromCsv(baseFilesPath + "/files/utility_matrix.csv")

print(a)
print(b)
print(c)
print(d)