import json
test = {}

test2 = {}
test2['data'] = []
print(test2)
with open('test.json') as data_file:
    data = json.load(data_file)
    print(len(data['movies']))
    for element in data['movies']:
        test2['movies'].append({"image": element['image']})
        test2['movies'].append(
            {"productionCompany": element['productionCompany']})
    print(test2)
    for element in data['actors']:
        del element['@type']
        del element['sameAs']


# limit = 0
# actors = data['actors']
# print(len(actors))
# if len(actors) >= 20 and len(actors) < 27:
#     limit = len(actors)*0.6
# elif len(actors) >= 27:
#     limit = len(actors)*0.4
# else:
#     limit = len(actors)
# limit = round(limit)
# i = len(actors)-1
# while i >= limit:
#     del actors[i]
#     i -= 1
# print(len(actors))
# test["actors"] = actors
# print(test)
