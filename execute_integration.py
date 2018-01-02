import settings
from eventbrite import EventbriteAPI

if __name__ == "__main__":
    """ Script that instantiates an Eventbrite API class and imports Eventbrite Attendees into Guidebook."""
    eb_api = EventbriteAPI(eventbrite_api_key=settings.EVENTBRITE_API_KEY, event_id=settings.EVENT_ID, gb_api_key=settings.GB_API_KEY, guide_id=settings.GUIDE_ID)
    print 'Importing Attendees from Eventbrite {} into Guide {}'.format(settings.EVENT_ID, settings.GUIDE_ID)
    eb_api.import_attendees_into_guidebook()
