
import requests, json, sys
from pathlib import Path


#needs to be run as admin
#warning: first download of SAIL data set takes ~10 minutes. Still better than downloading each file by hand!

def downloadVAspreadsheets(dict_path, destination_folder_path):

    with open(dict_path, 'r') as f:
        VISN_dict = dict( json.loads(f.read()) )

    #Select the years and quarters to examine SAIL data from
    years = ['15','16','17']
    qtrs = ['1','2','3','4']
    count = 0
    #Due to changing VISN's and other factors, not all paths that are tried will work (but most will, around 90%).
    paths_tried = 0
    for VISN in VISN_dict:
        VISN_str = VISN.split(' ')[-1]
        for hospital in VISN_dict[VISN].keys():
            for year in years:
                for qtr in qtrs:
                    #create filename and path
                    filename = 'SAIL-'+VISN_str+'_'+hospital+'_fy'+year+'q'+qtr+'.xls'
                    path = destination_folder_path + filename
                    paths_tried += 1
                    #monitor progress
                    sys.stdout.write('\r' + str(count)+' files downloaded, '+str(paths_tried) + ' paths tried.')
                    sys.stdout.flush()

                    #if the excel file isn't already in the directory, then download
                    if not Path(path).is_file():
                        r = requests.get('https://www.va.gov/QUALITYOFCARE/SAIL_FY'+year+'_Q'+qtr+'/' + filename)
                        if r.status_code == 200:
                            with open(path,'wb') as f:
                                f.write(r.content)
                            count += 1


if __name__ == '__main__':
    downloadVAspreadsheets('VISN_dict.txt',
                           'SAILDATA/')
