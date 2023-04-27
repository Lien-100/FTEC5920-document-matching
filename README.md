# FTEC5920-document-matching
Here are in total two files:
1. Extractor-the scripts and data used in content extraction
2. Matching- the scripts and data used in matching

In Extractor:
1. The data included: 'Extractor\Step1_extract_from_file\data' is a folder of resumes with different extension
2. What to run: 'Extract_from_file.py' is the script tha can automaticaly go through the folder and return the result
3. "parsed_result_from_folder.csv" is the running result
    
In Matching:
1. Run "beforeStart.py" if you got raw csv data prepared to generate json files needed in later steps
2. Run "run_InsightModel.py" to train the model
3. Folder "data_before_processing" contains the raw data I used to generate json files
4. The "data" folder contains the json files I used in training
    
Reference packages:
1. https://github.com/OmkarPathak/pyresparser
2. GitHub - CCIIPLab/PJFCANN
