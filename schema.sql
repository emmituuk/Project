-- table for storing information about different animals
CREATE TABLE animals(
animal_id SERIAL PRIMARY KEY,
animal VARCHAR(250) UNIQUE,
created_on TIMESTAMP NOT NULL
);

-- table for storing information about different countries
CREATE TABLE countries(
country_id SERIAL PRIMARY KEY,
country VARCHAR(250) UNIQUE,
created_on TIMESTAMP NOT NULL
);

-- table for storing information about persons
CREATE TABLE person(
person_id SERIAL PRIMARY KEY,
first_name VARCHAR(50) NOT NULL,
last_name VARCHAR(100) NOT NULL,
email VARCHAR(250) UNIQUE NOT NULL CHECK (email LIKE '%_@_%._%'),
own_country_id INTEGER NOT NULL REFERENCES countries(country_id),
created_on TIMESTAMP NOT NULL
);

-- table for storing information about a person's favorite animals
CREATE TABLE favorite_animals(
person_id INTEGER NOT NULL REFERENCES person(person_id),
favorite_animal_id INTEGER NOT NULL REFERENCES animals(animal_id),
other_animal VARCHAR(250),
created_on TIMESTAMP NOT NULL
);

-- table for storing information about a person's favorite countries
CREATE TABLE favorite_countries(
person_id INTEGER NOT NULL REFERENCES person(person_id),
favorite_country_id INTEGER NOT NULL REFERENCES countries(country_id),
created_on TIMESTAMP NOT NULL
);