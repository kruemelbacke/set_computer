"""test file to try out python functions
"""
# from turtle import update             (woher? Hab ich nicht eingefügt....)

# create empty dict - all face-up cards on table
face_up_cards = {}

# create empty dict for each card on table (max. 3 rows and 7 columns)
for card_row in range(3):
    for card_column in range(7):
        # create keys with row and column index as well as values 
        face_up_cards.update({'card_'+str(card_row)+'_'+str(card_column):{'colour':'','quantity':'','shape':'','filling':''}})

print(face_up_cards)
#print(face_up_cards.values())

def fun_is_a_set(face_up_cards):
    '''This function checks whether (at least) one set can be formed with the cards at hand and returns a boolean value accordingly
    
    face_up_cards: dict with all face-up cards on table and containing properties
    '''
    # test variable
    is_set=True
    
    # return true if there is a set
    if is_set==True:
        msg_is_a_set = 'There\'s a set availible!'
        return msg_is_a_set
        
    # return false if there is no set
    elif is_set==False:
        msg_is_a_set = 'I can\'t find a set here!'
        return msg_is_a_set
    
    # return error message otherwise
    else:
        error_msg = 'An error message!'
        return error_msg

