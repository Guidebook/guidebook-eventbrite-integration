import requests

import settings
from guidebook_api import GuidebookAPI


class EventbriteAPI(object):

    EVENTBRITE_API_BASE_URL = 'https://www.eventbriteapi.com/v3/'

    def __init__(self, eventbrite_api_key=None, event_id=None, gb_api_key=None, guide_id=None):
        """
        Initialize the instance with the given parameters.  This sets up the basic Eventbrite
        credentials and also an API client for the guidebook API.
        We use https://github.com/Guidebook/guidebook-api-python/ to handle Guidebook API requests
        """
        self.eventbrite_api_key = eventbrite_api_key
        self.headers = {'Authorization': 'Bearer {}'.format(eventbrite_api_key)}
        self.event_id = event_id
        self.gb_api_key = gb_api_key
        self.guide_id = guide_id
        self.gb_api_client = GuidebookAPI(api_key=gb_api_key, guide_id=guide_id)

    def fetch_attendees_and_ticket_classes(self, changed_since=None):
        """
        Function that fetches all the attendees that is owned by the authenticated Eventbrite user.
        `changed_since` is an optional filter option that can be used to find only recently updated attendees
        We use `event_id` to do additional filtering so that we only process Attendees for a specific Eventbrite event.
        """
        if changed_since is None:
            url = '{}users/me/owned_event_attendees'.format(self.EVENTBRITE_API_BASE_URL)
        else:
            url = '{}users/me/owned_event_attendees?changed_since={}'.format(self.EVENTBRITE_API_BASE_URL, changed_since)
        r = requests.get(url, headers=self.headers)
        attendees = r.json()['attendees']
        if settings.DEBUG:
            print '{} Attendees returned from Eventbrite'.format(len(attendees))
        condensed_attendees = []
        ticket_classes = []
        for attendee in attendees:
            if attendee['event_id'] != self.event_id:
                continue
            profile = attendee['profile']
            # We only want the basic profile and ticket class name information from the Eventbrite Attendee object
            attendee_dict = {'id': attendee['id'], 'first_name': profile['first_name'],
                             'last_name': profile['last_name'], 'email': profile['email'],
                             'ticket_class_name': attendee['ticket_class_name']}
            condensed_attendees.append(attendee_dict)
            if attendee['ticket_class_name'] not in ticket_classes:
                ticket_classes.append(attendee['ticket_class_name'])
        # Return all the attendee profiles that match our filter criteria along with all ticket_classes
        return condensed_attendees, ticket_classes

    def import_attendees_into_guidebook(self, changed_since=None):
        """
        Function that imports attendees into Guidebook
        """
        fetched_attendees, ticket_classes = self.fetch_attendees_and_ticket_classes(changed_since=changed_since)

        # First we create attendee groups for all ticket classes.
        # For this integration, we will be grouping attendees by ticket classes.
        ticket_class_name_id_mapping = {}
        for ticket_class in ticket_classes:
            ticket_class_id = self.gb_api_client.get_or_create_attendee_group(name=ticket_class)
            ticket_class_name_id_mapping[ticket_class] = ticket_class_id

        # Process all the fetched attendees and create them in Guidebook.  We keep track of already processed
        # attendees in `unique_attendees` to minimize redundant API calls
        unique_attendees = []
        tickets_and_members = {}
        for attendee in fetched_attendees:
            unique_attendee_ticket_group = u'{}-{}'.format(attendee['email'], attendee['ticket_class_name'])
            if unique_attendee_ticket_group in unique_attendees:
                continue
            attendee_id = self.gb_api_client.get_or_create_attendee(first_name=attendee['first_name'],
                                                                    last_name=attendee['last_name'],
                                                                    email=attendee['email'])
            if attendee_id is None:
                continue
            unique_attendees.append(unique_attendee_ticket_group)
            # build a list of attendees that belong to each ticket class
            ticket_class_name = attendee['ticket_class_name']
            list_of_attendees = tickets_and_members.get(ticket_class_name)
            if list_of_attendees is None:
                list_of_attendees = [attendee_id]
            else:
                list_of_attendees.append(attendee_id)
            tickets_and_members[ticket_class_name] = list_of_attendees
        if settings.DEBUG:
            print unique_attendees
        #  For each ticket class, add the corresponding attendees
        for ticket_class_name, attendee_ids in tickets_and_members.iteritems():
            self.gb_api_client.add_members_to_group(attendee_group_id=ticket_class_name_id_mapping[ticket_class_name], attendee_ids=attendee_ids)
            if settings.DEBUG:
                print 'Added Attendees: {} to Group {}'.format(attendee_ids, ticket_class_name_id_mapping[ticket_class_name])
