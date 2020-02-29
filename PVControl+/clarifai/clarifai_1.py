from clarifai.rest import ClarifaiApp

app = ClarifaiApp(api_key='346833e142374f2aa871b330773976d7')

#General model
#model = app.models.get('general-v1.3')
#response = model.predict_by_url(url='https://samples.clarifai.com/metro-north.jpg')

#model = app.public_models.general_model
model = app.models.get('face')
response1 = model.predict_by_filename('/home/pi/motion/deteccion/40-20190814155919-03.jpg')
response2 = model.predict_by_filename('/home/pi/motion/deteccion/37-20190814134801-00.jpg')

print ('Foto1')
print (response1)
print('--------------------')
print('--------------------')

print ('Foto2')
print (response2)

print('--------------------')
"""
concepts = response['outputs'][0]['data']['concepts']
for concept in concepts:
    print(concept['name'], concept['value'])
"""
caras = response1['outputs'][0]['data']#['regions']
print('Foto 1 caras=', caras)
print (len(caras))
"""
for cara in caras:
    print(cara['id'])
print()
"""


caras = response2['outputs'][0]['data']#['regions']
print('Foto 2 caras=', caras)
print (len(caras))

"""
for cara in caras:
    print(regions['id'])
"""

"""
#Travel model
model = app.models.get('travel-v1.0')

response = model.predict_by_url(url='https://samples.clarifai.com/travel.jpg')


#Food model
model = app.models.get('food-items-v1.0')

response = model.predict_by_url(url='https://samples.clarifai.com/food.jpg')


#NSFW model
model = app.models.get('nsfw-v1.0')

response = model.predict_by_url(url='https://samples.clarifai.com/nsfw.jpg')


#Apparel model
model = app.models.get('apparel')

response = model.predict_by_url(url='https://samples.clarifai.com/apparel.jpg')


#Celebrity model
model = app.models.get('celeb-v1.3')

response = model.predict_by_url(url='https://samples.clarifai.com/celebrity.jpg')


#Demographics model
model = app.models.get('demographics')

response = model.predict_by_url(url='https://samples.clarifai.com/demographics.jpg')


#Face Detection model
model = app.models.get('face')

response = model.predict_by_url(url='https://developer.clarifai.com/static/images/model-samples/face-001.jpg')


#Focus Detection model
model = app.models.get('focus')

response = model.predict_by_url(url='https://samples.clarifai.com/focus.jpg')


#General Embedding model
model = app.models.get('general-v1.3', model_type='embed')

response = model.predict_by_url(url='https://samples.clarifai.com/metro-north.jpg')


#Logo model
model = app.models.get('logo')

response = model.predict_by_url(url='https://samples.clarifai.com/logo.jpg')


#Color model
model = app.models.get('color', model_type='color')

response = model.predict_by_url(url='https://samples.clarifai.com/wedding.jpg')
"""
