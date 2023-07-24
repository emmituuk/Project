# moves a list element to the end of the list, required in the drop-down/select menu
def move_to_end(lst, elem):
    new_lst = []
    temp = None
    for i in lst:
        if i != elem:
            new_lst.append(i)
        else:
            temp = i
    new_lst.append(temp)
    return new_lst

# function for validating animal ID
def is_valid_animal_id(text, db, animal_id):
    sql = text("SELECT COUNT(*) FROM animals WHERE animal_id = :animal_id")
    result = db.session.execute(sql, {"animal_id": animal_id}).scalar()
    return result == 1

# function for validating country ID
def is_valid_country_id(text, db, country_id):
    sql = text("SELECT COUNT(*) FROM countries WHERE country_id = :country_id")
    result = db.session.execute(sql, {"country_id": country_id}).scalar()
    return result == 1