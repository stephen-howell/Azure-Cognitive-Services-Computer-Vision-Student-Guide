import requests
import os.path
import sys

# Refer to https://code.visualstudio.com/docs/python/debugging for advice with debugging Python
# This is a much simplfied version of https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts/python-analyze

# Add your 32 character Computer Vision subscription key and endpoint to your environment variables.
subscription_key = '00000000000000000000000000000000'
endpoint = "https://?????????.cognitiveservices.azure.com/"
# The general model was v2.0, uncomment this and comment out the v3.1 below to try it
# analyze_url = endpoint + "vision/v2.0/analyze"
# The new VIVO api is v3.1 - paper here: https://www.microsoft.com/en-us/research/blog/novel-object-captioning-surpasses-human-performance-on-benchmarks/
analyze_url = endpoint + "vision/v3.1/analyze"

# Edit launch.json to add "args" : ["./images/1.jpg"] when running in debugger, this passes the command line argument to the program
if len(sys.argv) < 2:
    print("Usage: py whatis.py file.jpg")
    raise SystemExit

# input file is the command line argument
inputfile = sys.argv[1] 
# split the file into it's name and extension (eg. filename and .jpg)
fileext = os.path.splitext(inputfile)
# If the input argument is a file
if os.path.isfile(inputfile):
    # If the extenstion is a jpg or png
    if fileext[1] == ".jpg" or fileext[1] =='.png':
        # If the file is smaller than 4MB
        if os.path.getsize(inputfile) < 4194304:
            # Read the image into a byte array
            image_data = open(inputfile, "rb").read()
            # Set the headers for the RESTful API call
            headers = { 'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream' }
            # If you specify just Description (or Tags etc.) then only that response will come back. Asking for lots here
            params = {'visualFeatures': 'Categories,Description,Tags,Objects'}
            response = requests.post(analyze_url, headers=headers, params=params, data=image_data)
            response.raise_for_status()

            # The 'analysis' object contains various fields that describe the image. The most
            # relevant caption for the image is obtained from the 'description' property.
            analysis = response.json()
            # Uncomment the print below to see the raw json returned
            # print(analysis)    
                        
            try:
                vision_caption = "Vision AI sees: "
                vision_caption += analysis["description"]["captions"][0]["text"].capitalize()
                vision_caption += " (" + str(round(analysis["description"]["captions"][0]["confidence"] * 100, 1)) + "%)"    
            except IndexError:
                vision_caption = "Nothing!"                        
            print(vision_caption)

            # Iterate over the categories and add them underneath caption
            vision_category =  ""
            for c in analysis["categories"]:
                vision_category += c["name"] + " (" + str(round(c["score"] * 100, 1)) + "%), "            
            print("Categories: " + vision_category);

            # Tags interesting too...
            vision_tags = "Tags: "    
            for tag in analysis["tags"]:
                vision_tags += tag["name"] + " (" + str(round(tag["confidence"] * 100, 1)) + "%), "
            print(vision_tags);
        else:
            print("Please specify a file that is 4MB or smaller.")
    else:
        print("Please specify a JPEG or PNG file.")
else:
    print("Please specify a file that exists")