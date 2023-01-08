from data_struct import *
from functions import *

import pandas as pd
import random
from faker import Faker
from numpy import NaN
from math import sqrt

# initialize Faker
fake = Faker(['it_IT', 'en_US'])
# Faker.seed(12345)
# random.seed(12345)

# Configuration
# number of users, people and queries
num_users = 10
num_people = 10
num_queries = 10
# user profiles informations
usersToNaN = 0 #Fraction (range of [0,1]) of users that has pose no query
high_grades = {
    "minMu": 80,
    "maxMu": 100,
    "minSd": 1,
    "maxSd": 10,
    "lenProp": random.uniform(0, 1),
    "randomLen": True,
    "everyone": {}
}
low_grades = {
    "minMu": 20,
    "maxMu": 40,
    "minSd": 1,
    "maxSd": 10,
    "lenProp": random.uniform(0, 1),
    "randomLen": True,
    "everyone": {}
}
average_grades = [Normal(50, 5)]
min_grade = 0
max_grade = 100
#Queries
queriesWeights = [1,0,5] #Weights for queries: query with [elements existing in people, random new elements, not present in the query]
queriesToNaN = 0 #Fraction (range of [0,1]) of query posed by nobody
#Utility matrix
sparsity = 0.9
#Various
special_char_regex = "(\\n|,|\'|\")"
baseFilesPath = "."


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
people.toCsv(baseFilesPath + "/files/people.csv")
users.toCsv(baseFilesPath + "/files/users.csv")
queries.toCsv(baseFilesPath + "/files/queries.csv")


# Create profiles for users that has posed some queries
users = Users(users.sample(frac=1-usersToNaN))
users.sort_index(inplace=True)
usersProfile: dict[str, UserProfile] = {}
for i in users.values:
    usersProfile[i] = UserProfile(people,
                                  Conditions(Normal(random.uniform(high_grades['minMu'], high_grades['maxMu']), random.uniform(high_grades['minSd'], high_grades['maxSd'])),
                                             elementsProp=high_grades['lenProp'], randomLen=high_grades['randomLen'], specialCases=high_grades['everyone']),
                                  Conditions(Normal(random.uniform(low_grades['minMu'], low_grades['maxMu']), random.uniform(low_grades['minSd'], low_grades['maxSd'])),
                                             elementsProp=low_grades['lenProp'], randomLen=low_grades['randomLen'], specialCases=low_grades['everyone']),
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
print(utility_matrix)

# Save utility matrix to CSV files
utility_matrix.toCsv(baseFilesPath + "/files/utility_matrix.csv")
