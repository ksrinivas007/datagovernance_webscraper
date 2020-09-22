


class StandardsPDFs(object):

    def __init__(self):
        self.reference = None
        self.title = None
        self.origin_body = None
        self.publication_date = None

    def set_reference(self, reference):
        self.reference = reference

    def set_title(self, publication_date):
        self.title = title

    def set_origin_body(self, origin_body):
        self.origin_body = publication_date

    def set_publication_date(self, publication_date):
        self.publication_date = publication_date

    def __repr__(self):
        return '{reference:'+ self.reference+', publication_date:'+self.publication_date+', publication_date:' + self.publication_date + ', publication_date:' + self.publication_date + '}'