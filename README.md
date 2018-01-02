# About

This code provides an example of how to integrate Guidebook with Eventbrite.

It fetches Attendee data from the [Eventbrite API](https://www.eventbrite.com/developer/v3/) and imports it into Guidebook via the [Guidebook Open API](https://developer.guidebook.com/).

# Sample Usage

Before testing out the code.  Please `pip install -r requirements.txt` to get the package dependencies.  We highly recommend you do this in an [virtualenv](https://virtualenv.pypa.io/en/stable/).

Update `settings.py` with your API information from both services.  Setting the `DEBUG` flag to `True` will output debugging info with each stage.  Then the following command will perform the import.

`python execute_integration`

# Customizing this Integration

This code is provided to Guidebook clients to customize for their own integrations.  Clients are welcome to take this integration code as a starting point and adapt it to their own needs.