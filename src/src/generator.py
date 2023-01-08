from data_struct import *
from functions import *

import pandas as pd
import random
from faker import Faker
from numpy import NaN
from math import sqrt

# initialize Faker
fake = Faker(['it_IT', 'en_US'])

# Configuration
# number of users, people and queries
num_users = 10
num_people = 10
num_queries = 10
# user profiles informations
usersToNaN = 0 #Fraction (range of [0,1]) of users that has pose no query
preferences = {
    "minMu": 80, #Minimum mean of the Gaussian normal that defines the highest grades
    "maxMu": 100, #Maximum mean of the Gaussian normal that defines the highest grades
    "minSd": 1, #Minimum standard deviation of the Gaussian normal that defines the highest grades
    "maxSd": 10, #Maximum standard deviation of the Gaussian normal that defines the highest grades
    "elementFrac": random.uniform(0, 1), #Fraction (range of [0,1]) of elements of a field that a user can like out of all those possible
    "randomLen": True, #Tell if elementFrac is the actual or a maximum value
    "everyone": {} #Element that everyone like
}
disinterests = {
    "minMu": 20, #Minimum mean of the Gaussian normal that defines the lowest grades
    "maxMu": 40, #Maximum mean of the Gaussian normal that defines the lowest grades
    "minSd": 1, #Minimum standard deviation of the Gaussian normal that defines the lowest grades
    "maxSd": 10, #Maximum standard deviation of the Gaussian normal that defines the lowest grades
    "elementFrac": random.uniform(0, 1), #Fraction (range of [0,1]) of elements of a field that a user could be disinterested out of all the remaining from from the preferences
    "randomLen": True, #Tell if elementFrac is the actual or a maximum value
    "everyone": {} #Element that everyone dislike
}
average_grades = [Normal(50, 5)] #Gaussian normals, ordered by mean, that defines the intermediary grades (so, not the lowest and the highest)
min_grade = 0 #Min grade possible
max_grade = 100 #Max grade possible
#Queries
queriesWeights = [1,0,5] #Weights for queries: query with [elements existing in people, random new elements, not present in the query]
queriesToNaN = 0 #Fraction (range of [0,1]) of query posed by nobody
#Utility matrix
sparsity = 0.9 #Fraction (range of [0,1]) of elements to remove
#Various
special_char_regex = "(\\n|,|\'|\")" #Special character to remove from random strings
base_files_path = "../data/" #Base path of CSVs


# Create a dataframe for the people
people = People(pd.DataFrame({'id': ['p{}'.format(i) for i in range(num_people)],  # Rimettere 'id' come index in caso si voglia tornare in quel modo
                              'name': [fake.first_name() for _ in range(num_people)],
                              'surname': [fake.last_name() for _ in range(num_people)],
                              'address': [strWithoutChar(fake.city, special_char_regex) for _ in range(num_people)],
                              'age': [random.randint(10, 90) for _ in range(num_people)],
                              'occupation': [strWithoutChar(fake.job, special_char_regex) for _ in range(num_people)]}))


# Create a dataframe for the users
users = Users(pd.Series(['u{}'.format(i) for i in range(num_users)]))


# Create a dataframe for the queries
queries = Queries(pd.DataFrame({'id': [randomElement(people.getColumnSubset('id'), rndFormattedInt, [num_queries, num_queries*2, "p{}"], alsoNaN=True, weights=queriesWeights) for _ in range(num_queries)],
                                'name': [randomElement(people.getColumnSubset('name'), fake.first_name, alsoNaN=True, weights=queriesWeights) for _ in range(num_queries)],
                                'surname': [randomElement(people.getColumnSubset('name'), fake.last_name, alsoNaN=True, weights=queriesWeights) for _ in range(num_queries)],
                                'address': [randomElement(people.getColumnSubset('address'), strWithoutChar, [fake.city, special_char_regex], alsoNaN=True, weights=queriesWeights) for _ in range(num_queries)],
                                'age': [randomElement(people.getColumnSubset('age'), random.randint, [10, 90], alsoNaN=True, weights=queriesWeights) for _ in range(num_queries)],
                                'occupation': [randomElement(people.getColumnSubset('occupation'), strWithoutChar, [fake.job, special_char_regex], alsoNaN=True, weights=queriesWeights) for _ in range(num_queries)]},
                               ['q{}'.format(i) for i in range(num_queries)]))


# Save people, users and queries to CSV files
people.toCsv(base_files_path + "people.csv")
print("People file generated")
users.toCsv(base_files_path + "users.csv")
print("Users file generated")
queries.toCsv(base_files_path + "queries.csv")
print("Queries file generated")


# Create profiles for users that has posed some queries
users = Users(users.sample(frac=1-usersToNaN))
users.sort_index(inplace=True)
usersProfile: dict[str, UserProfile] = {}
for i in users.values:
    usersProfile[i] = UserProfile(people,
                                  Conditions(Normal(random.uniform(preferences['minMu'], preferences['maxMu']), random.uniform(preferences['minSd'], preferences['maxSd'])),
                                             elementsProp=preferences['elementFrac'], randomLen=preferences['randomLen'], specialCases=preferences['everyone']),
                                  Conditions(Normal(random.uniform(disinterests['minMu'], disinterests['maxMu']), random.uniform(disinterests['minSd'], disinterests['maxSd'])),
                                             elementsProp=disinterests['elementFrac'], randomLen=disinterests['randomLen'], specialCases=disinterests['everyone']),
                                  average_grades)


# Create a dataframe for users's rating of people
tmp_persona_rating = []
persona_rating = pd.DataFrame([[usersProfile[i].getGrade(people.iloc[j], min_grade, max_grade) for j in people.index] for i in usersProfile],
                                users.values, people.index)
del usersProfile

# Remove queries that nobody pose
queries = Queries(queries.sample(frac=1-queriesToNaN))
queries.sort_index(inplace=True)

# Create a dataframe for the utility matrix
utility_matrix = UtilityMatrix(pd.DataFrame([[NaN for _ in range(queries.index.size)] for _ in range(users.size)], users.values, queries.index.values))

cellCoordinates = populateUtilityMatrix(utility_matrix, people, queries, persona_rating, min_grade, max_grade)

removeValuesUtilityMatrix(utility_matrix, cellCoordinates, sparsity)

# Save utility matrix to CSV files
utility_matrix.toCsv(base_files_path + "utility_matrix.csv")
print("Utility matrix file generated")