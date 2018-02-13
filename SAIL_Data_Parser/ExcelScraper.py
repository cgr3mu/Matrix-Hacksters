
import xlrd, json, sys, jsonpickle, os
import time


# needs to be run as admin

# Look mom, I can use object-oriented programming!
class Hospital:

    def __init__(self, name):
        self.name = name
        self.coordinates = ()
        self.year_qtr_dict = {}


if __name__ == '__main__':

    t1 = time.clock()
    VISN_data_dict = {}
    with open('VISN_dict.txt', 'r') as f:
        VISN_dict = dict(json.loads(f.read()))
    years = ['15', '16', '17']
    qtrs = ['1', '2','3', '4']

    path = 'SAILDATA/'
    directory = os.listdir(path)
    count = 0
    for file in directory:

        count += 1
        #monitor progress -- runtime is around 25-30 s
        sys.stdout.write('\r' + str(round(count*100/len(directory),0)) + '% of records analyzed in '
                         + str(round(time.clock()-t1,1)) + 's')
        sys.stdout.flush()

        #parse the filename to obtain the required parameters
        data_str = file[5:-4].split('_')

        VISN = 'VISN ' + data_str[0]
        location = data_str[1]
        year = '20' + data_str[2][2:4]
        qtr = data_str[2][-1]

        #open the file
        spreadsheet = xlrd.open_workbook(filename = path+file).sheet_by_index(0)

        #if VISN_data_dict is empty, create list
        if VISN not in VISN_data_dict:
            VISN_data_dict[VISN] = []

        #check if the hospital object already exists in VISN_data_dict[VISN].
        alreadyInDictPos = -1
        for i in range(0, len(VISN_data_dict[VISN])):
            if VISN_data_dict[VISN][i].name == location:
                alreadyInDictPos = i
                break
        if alreadyInDictPos >= 0:
            h = VISN_data_dict[VISN][alreadyInDictPos]
        else:
            h = Hospital(location)
            h.coordinates = VISN_dict[VISN][location]
            VISN_data_dict[VISN].append(h)

        #for the hospital object, make sure that year_qtr_dict is properly initialized if it hasn't yet been.
        if year not in h.year_qtr_dict:
            h.year_qtr_dict[year] = {}
        if qtr not in h.year_qtr_dict[year]:
            h.year_qtr_dict[year][qtr] = {}

        #The SAIL data files are inconsistent in where they put data endpoints in their spreadsheets
        # (i.e. one sheet will have parameter X in cell T20, while another will have that parameter in cell S19.
        #Fix this by finding where the data to use is located for each spreadsheet.
        start_row = -1
        target_col = -1
        for row in range(0, spreadsheet.nrows):
            for col in range(0, spreadsheet.ncols):
                cell = spreadsheet.cell(row, col)
                if cell.ctype == 1:
                    keywords = ['mental', 'health', 'from', 'date']
                    #Apparently it's hard to consistently name your parameters too! So I have to check if certain words
                    #are in the parameter name.
                    if len(cell.value) > 3 and all(word in cell.value.strip()[3:].lower().split() for word in keywords):
                        start_row = row
                    if cell.value == 'Measure':
                        while spreadsheet.cell_value(row, col) not in ['Benchmark', '5-Star Facilities']:
                            col += 1
                        target_col = col - 1
                    break

        #Some data endpoints are blank, which throws an error when python tries to convert to float.  Annoying.
        if spreadsheet.cell_value(start_row, target_col) != '':
            h.year_qtr_dict[year][qtr]['mhApptCompletionRate'] = float(spreadsheet.cell_value(start_row, target_col))
        if spreadsheet.cell_value(start_row + 2, target_col) != '':
            h.year_qtr_dict[year][qtr]['callCenterSpeed'] = float(spreadsheet.cell_value(start_row + 2, target_col))
        if spreadsheet.cell_value(start_row + 3, target_col) != '':
            h.year_qtr_dict[year][qtr]['callCenterAbandonmentRate'] = float(spreadsheet.cell_value(start_row + 3, target_col))
        if spreadsheet.cell_value(start_row + 4, target_col) != '':
            h.year_qtr_dict[year][qtr]['mhOverallScore'] = float(spreadsheet.cell_value(start_row + 4, target_col))
        if spreadsheet.cell_value(start_row + 5, target_col) != '':
            h.year_qtr_dict[year][qtr]['mhCoverage'] = float(spreadsheet.cell_value(start_row + 5, target_col))
        if spreadsheet.cell_value(start_row + 6, target_col) != '':
            h.year_qtr_dict[year][qtr]['mhContinuityOfCare'] = float(spreadsheet.cell_value(start_row + 6, target_col))
        if spreadsheet.cell_value(start_row + 7, target_col) != '':
            h.year_qtr_dict[year][qtr]['mhExperienceOfCare'] = float(spreadsheet.cell_value(start_row + 7, target_col))


    #write completed VISN_data_dict to file as JSON object.
    with open('Parsed_VISN_SAIL_data.txt','w') as f:
        f.write(json.dumps(json.loads(jsonpickle.encode(VISN_data_dict, unpicklable=False)),indent=4))