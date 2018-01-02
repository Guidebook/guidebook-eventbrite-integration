from guidebook import api_requestor, exceptions

import settings


class GuidebookAPI(object):

    # This class uses the guidebook api_requestor found at https://github.com/Guidebook/guidebook-api-python
    # to interact with the Guidebook API.  Documentation found at: https://developer.guidebook.com/v1/
    BASE_API_URL = 'https://builder.guidebook.com/open-api/v1/'

    def __init__(self, api_key=None, guide_id=None):
        """Initialize the instance with the given parameters."""
        if settings.DEBUG:
            print 'BASE API URL: {}'.format(self.BASE_API_URL)
        self.api_client = api_requestor.APIRequestor(api_key)
        self.guide_id = guide_id
        if settings.DEBUG:
            print 'Starting Guidebook API connection...'
        self.attendees = self.fetch_existing_attendees()
        if settings.DEBUG:
            print '{} existing attendees fetched from guide {}'.format(len(self.attendees), guide_id)
        self.attendee_groups = self.fetch_existing_attendee_groups()
        if settings.DEBUG:
            print '{} existing attendee groups fetched from guide {}'.format(len(self.attendee_groups), guide_id)

    def concatenate_all_page_data(self, api_url, result_keys):
        """Guidebook API responses are paged.  This helper function will iterate through the pages and return all objects in one list."""
        objects = []
        next_page = api_url
        while next_page:
            response = self.api_client.request('get', next_page)
            results = response['results']
            next_page = response['next']
            for result in results:
                objects.append({key: result[key] for key in result_keys})
        return objects

    def find_attendee_by_email(self, email):
        """Check to see if an Attendee already exists in Guidebook that matches on email.  Return Attendee id if matched."""
        for attendee in self.attendees:
            if attendee['email'] == email:
                return attendee['id']
        return None

    def find_attendee_group_by_name(self, name):
        """Check to see if an Attendee Group already exists in Guidebook that matches on name.  Return Attendee Group id if matched."""
        for attendee_group in self.attendee_groups:
            if attendee_group['name'] == name:
                return attendee_group['id']
        return None

    def fetch_existing_attendees(self):
        """Fetch all existing Attendees for a given Guide in Guidebook."""
        api_url = '{}attendees/?guide={}'.format(self.BASE_API_URL, self.guide_id)
        locations = self.concatenate_all_page_data(api_url, ['id', 'email'])
        return locations

    def fetch_existing_attendee_groups(self):
        """Fetch all existing Attendee Groups for a given Guide in Guidebook."""
        api_url = '{}attendee-groups/?guide={}'.format(self.BASE_API_URL, self.guide_id)
        attendee_groups = self.concatenate_all_page_data(api_url, ['id', 'name'])
        return attendee_groups

    def create_attendee(self, first_name=None, last_name=None, email=None):
        """Create an Attendee in the Guidebook Guide."""
        api_url = '{}attendees/'.format(self.BASE_API_URL)
        post_data = {
            'guide': self.guide_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        }
        try:
            response = self.api_client.request('post', api_url, data=post_data)
        except exceptions.BadRequestError:
            return {}
        return response

    def create_attendee_group(self, name=None):
        """Create an Attendee Group in the Guidebook Guide."""
        api_url = '{}attendee-groups/'.format(self.BASE_API_URL)
        post_data = {
            'guide': self.guide_id,
            'name': name,
        }
        response = self.api_client.request('post', api_url, data=post_data)
        return response

    def get_or_create_attendee(self, **kwargs):
        """Checks for an existing Attendee before creating an Attendee in the Guidebook Guide."""
        existing_attendee_id = self.find_attendee_by_email(kwargs['email'])
        if existing_attendee_id is None:
            return self.create_attendee(**kwargs).get('id')
        else:
            return existing_attendee_id

    def get_or_create_attendee_group(self, **kwargs):
        """Checks for an existing Attendee Group before creating an Attendee Group in the Guidebook Guide."""
        existing_attendee_group_id = self.find_attendee_group_by_name(kwargs['name'])
        if existing_attendee_group_id is None:
            return self.create_attendee_group(**kwargs).get('id')
        else:
            return existing_attendee_group_id

    def add_members_to_group(self, attendee_group_id, attendee_ids):
        """Add Attendees to an Attendee Group."""
        api_url = '{}attendee-groups/{}/add-attendees/'.format(self.BASE_API_URL, attendee_group_id)
        data = {'attendees': attendee_ids}
        response = self.api_client.request('post', api_url, data=data)
        return response
