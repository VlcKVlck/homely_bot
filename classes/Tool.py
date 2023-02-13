class Tool:
    def __init__(self, user_id, name, category = None, image_ref = None, type_of = None,  availability = False):
        self.user_id = user_id
        self.name = name
        self.type_of = type_of
        self.category = category
        self.availability = availability
        self.image_ref = image_ref

    def get_availability(self):
        return self.availability

    def set_availability(self, status):
        self.availability = status


