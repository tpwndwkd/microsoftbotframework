import datetime
from .response import Response


class Activity(Response):
    def __init__(self, **kwargs):
        self.defaults = {
            'action': None,
            'attachments': None,          # Attachment[]
            'attachmentLayout': None,
            'channelData': None,          # ChannelData object
            'channelId': None,
            'conversation': None,         # ConversationAccount object
            'entities': None,             # mentioned entities ie Mention or Place objects
            'fromAccount': None,          # ChannelAccount
            'historyDisclosed': None,
            'id': None,                   # ActivityId - may not be required in response?
            'inputHint': None,            # (acceptingInput, expectingInput, ignoringInput)
            'locale': None,               # <language>-<country>
            'localTimestamp': None,
            'membersAdded': None,         # This will be passed only in conversationUpdates
            'membersRemoved': None,       # This will be passed only in conversationUpdates
            'recipient': None,            # ChannelAccount
            'relatesTo': None,            # ConversationReferece - references a specific point in a convo
            'replyToId': None,            # Used to reply to a thread / specific activity.
            'serviceUrl': None,
            'speak': None,                # Text to be spoken
            'suggestedActions': None,
            'summary': None,              # A summary of information
            'text': None,                 # The text to be sent to a user
            'textFormat': None,           # [markdown, plain, xml]
            'timestamp': None,            # UTC
            'topicName': None,
            'type': 'message',                 # [contactRelationUpdate, conversationUpdate, deleteUserData, message, ping, typing, endOfConversation]
        }

        # Used to grab the activityId for responses
        self.activityId = None

        # Used in create Conversation - not is not required and will default to from
        self.isGroup = kwargs.get('isGroup', False)
        self.members = kwargs.get('members', None)
        self.bot = kwargs.get('bot', None)

        for (prop, default) in self.defaults.items():
            setattr(self, prop, kwargs.pop(prop, default))

        fill = kwargs.pop('fill', None)
        reply_to_activity = kwargs.pop('reply_to_activity', None)
        if fill is not None:
            self.fill(fill, reply_to_activity)

        # Clean up the conversationId if Microsoft has added messageid to it. (bug?)
        #if re.search(';', self.conversation['id']):
        #    self.conversation['id'] = re.match('[^;]+', self.conversation['id']).group()

        # Create timestamp
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ")

        # A nicer way to set conversation = {"id": "asdfsdf"}
        self.conversationId = kwargs.pop('conversationId', None)
        if self.conversationId is not None:
            self.conversation = {"id": self.conversationId}
            
        # Set activityId if passed in args
        activityId_arg = kwargs.pop('activityId', None)
        if activityId_arg is not None:
            self.activityId = activityId_arg
            self.id = self.activityId

        flip = kwargs.pop('flip', False if fill is None else True)
        if flip:
            self.flip()

        super(Activity, self).__init__(**kwargs)

    def flip(self):
        recipient = self.recipient
        self.recipient = self.fromAccount
        self.fromAccount = recipient

    def fill(self, message, reply_to_activity=False):
        skip = ['timestamp', 'localTimestamp', 'entities', 'text', 'id', 'membersAdded', 'membersRemoved', 'attachments', 'channelData']
        for key, value in message.items():
            # in code from is called fromAccount, from is a reserved word (note from is still set)
            if key == 'from':
                if getattr(self, 'fromAccount') is None:
                    setattr(self, 'fromAccount', value)

            # set the activityId to id to make it easy to set in conversation operations.
            if key == 'id':
                self.activityId = value

            # fill the remaining keys if they have not been set using defaults or arguments
            if key not in skip:
                if getattr(self, key, None) is None:
                    setattr(self, key, value)

            # We need to remove the slack channel data when posting back.
            if key == 'channelData':
                if 'SlackMessage' in message['channelData']:
                    setattr(self, key, None)
                else:
                    setattr(self, key, value)

        if reply_to_activity:
            self.replyToId = message['id']

    def to_dict(self):
        json = {}
        for key in self.defaults:
            attribute = getattr(self, key)
            if attribute is not None:
                if key == 'fromAccount':
                    json['from'] = attribute
                else:
                    json[key] = attribute
        return json
