from clarifai.rest import ClarifaiApp
from clarifai.rest import FeedbackInfo

app = ClarifaiApp(api_key='346833e142374f2aa871b330773976d7')

# positive feedback: this is a dog
m = app.models.get('general-v1.3')

m.send_concept_feedback(input_id='id1', url='https://samples.clarifai.com/dog2.jpeg',
                        concepts=['dog', 'animal'],
                        feedback_info=FeedbackInfo(output_id='OID',
                                                   session_id='SID',
                                                   end_user_id='UID',
                                                   event_type='annotation'))

# negative feedback: this is not a cat
m = app.models.get('general-v1.3')

m.send_concept_feedback(input_id='id1', url='https://samples.clarifai.com/dog2.jpeg',
                        not_concepts=['cat', 'kitty'],
                        feedback_info=FeedbackInfo(output_id='OID',
                                                   session_id='SID',
                                                   end_user_id='UID',
                                                   event_type='annotation'))

# all together: this is a dog but not a cat
m = app.models.get('general-v1.3')

m.send_concept_feedback(input_id='id1', url='https://samples.clarifai.com/dog2.jpeg',
                        concepts=['dog'], not_concepts=['cat', 'kitty'],
                        feedback_info=FeedbackInfo(output_id='OID',
                                                   session_id='SID',
                                                   end_user_id='UID',
                                                   event_type='annotation'))
Detection model prediction
from clarifai.rest import ClarifaiApp
from clarifai.rest import FeedbackInfo
from clarifai.rest import Region, RegionInfo, BoundingBox, Concept

app = ClarifaiApp()

m.send_region_feedback(input_id='id2', url='https://developer.clarifai.com/static/images/model-samples/celeb-001.jpg',
                       regions=[Region(region_info=RegionInfo(bbox=BoundingBox(top_row=0.1,
                                                                               left_col=0.2,
                                                                               bottom_row=0.5,
                                                                               right_col=0.5)),
                                       concepts=[Concept(concept_id='people', value=True),
                                                 Concept(concept_id='portrait', value=True)])],
                       feedback_info=FeedbackInfo(output_id='OID',
                                                  session_id='SID',
                                                  end_user_id='UID',
                                                  event_type='annotation'))