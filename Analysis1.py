
import urllib.request, json
with urllib.request.urlopen("https://www.data.va.gov/sites/default/files/VeteransCrisisLineFY11toFY14AggregateFOIA1500242.json") as url:
    data = json.loads(url.read().decode())
    print(data)

activeDuty = 0
notActiveDuty = 0
parameterList = {} #dictionary of dictionaries

for call in data:
    parameter = call['DataElement']
    value = call['DataValue']
    if parameter not in parameterList:
        parameterList[parameter] = {}
        parameterList[parameter][value] = 1
    else:
        if value not in parameter:
            parameterList[parameter][value] = 1
    '''
        elif value in parameter:
            parameterList[parameter][value] += 1
        else:
            continue
'''
print(parameterList)



