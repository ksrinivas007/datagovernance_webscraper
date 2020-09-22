


class Standards(object):

    def __init__(self):
        self.date = None
        self.no_published = None
        self.standard = None
        self.link = None

    def set_date(self, date):
        self.date = date

    def set_no_published(self, no_published):
        self.no_published = no_published

    def set_standard(self, standard):
        self.standard = standard

    def set_link(self, link):
        self.link = link

    def __repr__(self):
        return '{date:'+ self.date+', no_published:'+self.no_published+', standard:' + self.standard + ', link:' + self.link + '}'