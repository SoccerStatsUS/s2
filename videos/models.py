from django.db import models


class VideoManager(models.Manager):

    def video_dict(self):
        """
        Returns a dict mapping a name to a source id.
        """
        d = {}
        for e in self.get_query_set():
            d[e.name] = e.id
            if e.base_url:
                d[e.base_url] = e.id

        return d



class Video(models.Model):
    """
    A video is an embeddable video.
    """

    name = models.CharField(max_length=1023)
    url = models.CharField(max_length=1023) 


    objects = VideoManager()



    def __unicode__(self):
        return self.url


