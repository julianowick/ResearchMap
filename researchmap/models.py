from django.db import models

# Create your models here.   
class Document(models.Model):
    """
    Documents (papers, articles, books, etc.)
    """
    # Possible document types
    DOC_TYPES = (
        (u'A', u'Article'),
        (u'B', u'Book'),
        (u'C', u'Booklet'),
        (u'D', u'Conference'),
        (u'E', u'In Book'),
        (u'F', u'In Collection'),
        (u'G', u'In Proceedings'),
        (u'H', u'Manual'),
        (u'I', u'Masters Thesis'),
        (u'J', u'Misc'),
        (u'K', u'PhD Thesis'),
        (u'L', u'Proceedings'),
        (u'M', u'Tech Report'),
        (u'N', u'Unpublished'),
        (u'O', u'WWW'),       
    )

    # Main
    type = models.CharField(max_length=1, choices=DOC_TYPES, default='J', db_index=True)
    title = models.CharField(max_length=250, db_index=True)
    month = models.CharField(max_length=50, null=True)
    pages = models.CharField(max_length=50, null=True)
    year = models.PositiveIntegerField(default=0)
    conference = models.CharField(max_length=200)
    citations = models.IntegerField()    
    
    def __unicode__(self):
        return self.title